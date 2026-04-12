import os
import json
import logging
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_anthropic_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key.startswith("sk-ant-your"):
            raise EnvironmentError("ANTHROPIC_API_KEY is not configured in .env")
        _anthropic_client = anthropic.Anthropic(api_key=api_key)
    return _anthropic_client


def _load_config_from_db() -> tuple[list[dict], dict]:
    try:
        from database.db import categories_collection, settings_collection
        categories = list(categories_collection.find({"active": True}, {"_id": 0}))
        threshold_doc = settings_collection.find_one({"key": "priority_thresholds"})
        thresholds = {
            "low_max":    threshold_doc.get("low_max",    30) if threshold_doc else 30,
            "medium_max": threshold_doc.get("medium_max", 70) if threshold_doc else 70,
        }
        return categories, thresholds
    except Exception as e:
        logger.error(f"Failed to load config from DB: {e}")
        fallback_cats = [
            {"name": "Road Damage"},
            {"name": "Waste Management"},
            {"name": "Electrical Issues"},
            {"name": "Water Leakage"},
            {"name": "Illegal Construction"},
        ]
        return fallback_cats, {"low_max": 30, "medium_max": 70}


def _get_priority(score: int, thresholds: dict) -> str:
    if score > thresholds["medium_max"]:
        return "High"
    elif score > thresholds["low_max"]:
        return "Medium"
    return "Low"


def _build_prompt(description: str, categories: list[dict]) -> str:
    cat_names = [c["name"] for c in categories]
    cats_str  = "\n".join(f"  - {n}" for n in cat_names)
    return f"""You are an expert civic infrastructure analyst working for a smart city monitoring system.

A citizen has submitted the following infrastructure issue report:

REPORT DESCRIPTION:
\"\"\"{description}\"\"\"

YOUR TASK:
Analyse this report and return a JSON object with EXACTLY these fields:

1. "category" — Choose the SINGLE most appropriate category from this list only:
{cats_str}

2. "risk_score" — An integer from 0 to 100 representing the severity/urgency:
   - 0–30  = Low risk (cosmetic/minor, no immediate danger)
   - 31–70 = Medium risk (functional issue, needs attention soon)
   - 71–100 = High risk (dangerous, urgent, potential for injury or major damage)

   Consider: public safety impact, potential for accidents, scale of damage, 
   number of people affected, urgency of repair needed.

3. "priority" — Must be exactly one of: "Low", "Medium", "High"
   (Must align with risk_score: 0-30=Low, 31-70=Medium, 71-100=High)

4. "reasoning" — 1–2 sentences explaining your risk assessment in plain English.

5. "affected_population" — Estimate: "Individual", "Neighbourhood", "District", or "City-wide"

6. "recommended_action" — One sentence on what authorities should do.

IMPORTANT: Return ONLY valid JSON. No markdown, no explanation outside the JSON object.

Example output format:
{{
  "category": "Electrical Issues",
  "risk_score": 82,
  "priority": "High",
  "reasoning": "Exposed live wires near a busy pedestrian path pose immediate electrocution risk, especially during rain.",
  "affected_population": "Neighbourhood",
  "recommended_action": "Dispatch electrical crew immediately and cordon off the area."
}}"""


def analyze_report(description: str) -> dict:
    categories, thresholds = _load_config_from_db()

    try:
        client  = _get_client()
        prompt  = _build_prompt(description, categories)

        logger.info("Calling Claude API for risk analysis...")
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = message.content[0].text.strip()
        logger.debug(f"Claude raw response: {raw_text}")

        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        result = json.loads(raw_text)

        required = {"category", "risk_score", "priority", "reasoning",
                    "affected_population", "recommended_action"}
        missing = required - result.keys()
        if missing:
            raise ValueError(f"Claude response missing fields: {missing}")

        result["risk_score"] = max(0, min(100, int(result["risk_score"])))

        result["priority"] = _get_priority(result["risk_score"], thresholds)
        result["ai_powered"] = True

        logger.info(
            f"AI analysis complete — category={result['category']} "
            f"score={result['risk_score']} priority={result['priority']}"
        )
        return result

    except EnvironmentError as e:
        logger.error(f"AI engine config error: {e}")
        return _fallback_analysis(description, categories, thresholds,
                                  reason=f"API key not configured: {e}")

    except json.JSONDecodeError as e:
        logger.error(f"Claude returned invalid JSON: {e}")
        return _fallback_analysis(description, categories, thresholds,
                                  reason="AI response parse error")

    except anthropic.APIStatusError as e:
        logger.error(f"Anthropic API error {e.status_code}: {e.message}")
        return _fallback_analysis(description, categories, thresholds,
                                  reason=f"API error {e.status_code}")

    except anthropic.APIConnectionError as e:
        logger.error(f"Anthropic connection error: {e}")
        return _fallback_analysis(description, categories, thresholds,
                                  reason="API connection failed")

    except Exception as e:
        logger.exception(f"Unexpected AI engine error: {e}")
        return _fallback_analysis(description, categories, thresholds,
                                  reason=str(e))


def _fallback_analysis(description: str, categories: list, thresholds: dict,
                       reason: str = "") -> dict:
    logger.warning(f"Using fallback analysis. Reason: {reason}")

    text  = description.lower()
    score = 35

    high_words   = ["danger", "hazard", "urgent", "emergency", "fire",
                    "electrocution", "collapse", "flood", "fatal"]
    low_words    = ["minor", "small", "slight", "cosmetic", "tiny"]

    if any(w in text for w in high_words):
        score = 72
    elif any(w in text for w in low_words):
        score = 18

    cat_map = {
        "Road Damage":          ["pothole", "road", "pavement", "crack", "highway"],
        "Electrical Issues":    ["wire", "electric", "power", "spark", "light"],
        "Water Leakage":        ["water", "leak", "pipe", "flood", "drain"],
        "Waste Management":     ["garbage", "trash", "waste", "dump", "litter"],
        "Illegal Construction": ["illegal", "construction", "encroach", "unauthorised"],
    }
    detected = categories[0]["name"] if categories else "Road Damage"
    for cat_name, kws in cat_map.items():
        if any(kw in text for kw in kws):
            detected = cat_name
            break

    return {
        "category":            detected,
        "risk_score":          score,
        "priority":            _get_priority(score, thresholds),
        "reasoning":           f"Heuristic analysis (AI unavailable: {reason}). Manual review recommended.",
        "affected_population": "Unknown",
        "recommended_action":  "Assign to relevant department for manual assessment.",
        "ai_powered":          False,
    }