import os
import json
import logging
import re
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_openrouter_api_key: Optional[str] = None


def _get_api_key() -> str:
    global _openrouter_api_key
    if _openrouter_api_key is None:
        # Try Streamlit secrets first
        try:
            import streamlit as st
            api_key = st.secrets.get("OPENROUTER_API_KEY")
        except Exception:
            api_key = None
        # Fallback to .env
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENROUTER_API_KEY not configured")
        _openrouter_api_key = api_key
    return _openrouter_api_key


def _call_llm(prompt: str) -> str:
    api_key = _get_api_key()

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "google/gemma-3-12b-it",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        },
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(f"OpenRouter API error {response.status_code}: {response.text}")

    return response.json()["choices"][0]["message"]["content"]


def _safe_json_parse(text: str) -> dict:
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


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
   - 0–30  = Low risk
   - 31–70 = Medium risk
   - 71–100 = High risk

3. "priority" — Must be exactly one of: "Low", "Medium", "High"

4. "reasoning" — 1–2 sentences

5. "affected_population" — "Individual", "Neighbourhood", "District", or "City-wide"

6. "recommended_action" — One sentence

STRICT RULE:
- Return ONLY valid JSON
- No markdown
- No explanation
- Output must start with {{ and end with }}

Example:
{{
  "category": "Electrical Issues",
  "risk_score": 82,
  "priority": "High",
  "reasoning": "Exposed wires are dangerous.",
  "affected_population": "Neighbourhood",
  "recommended_action": "Fix immediately."
}}"""


def analyze_report(description: str) -> dict:
    categories, thresholds = _load_config_from_db()

    try:
        prompt = _build_prompt(description, categories)

        logger.info("Calling OpenRouter (Gemma 3 12B)...")
        raw_text = _call_llm(prompt).strip()

        logger.debug(f"LLM raw response: {raw_text}")

        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        result = _safe_json_parse(raw_text)

        required = {"category", "risk_score", "priority", "reasoning",
                    "affected_population", "recommended_action"}
        missing = required - result.keys()
        if missing:
            raise ValueError(f"Missing fields: {missing}")

        result["risk_score"] = max(0, min(100, int(result["risk_score"])))
        result["priority"] = _get_priority(result["risk_score"], thresholds)
        result["ai_powered"] = True

        logger.info(
            f"AI analysis complete — category={result['category']} "
            f"score={result['risk_score']} priority={result['priority']}"
        )
        return result

    except Exception as e:
        logger.exception(f"AI error: {e}")
        return _fallback_analysis(description, categories, thresholds, reason=str(e))


def _fallback_analysis(description: str, categories: list, thresholds: dict,
                       reason: str = "") -> dict:
    logger.warning(f"Using fallback analysis. Reason: {reason}")

    text  = description.lower()
    score = 35

    high_words = ["danger", "hazard", "urgent", "emergency", "fire",
                  "electrocution", "collapse", "flood", "fatal"]
    low_words  = ["minor", "small", "slight", "cosmetic", "tiny"]

    if any(w in text for w in high_words):
        score = 72
    elif any(w in text for w in low_words):
        score = 18

    cat_map = {
        "Road Damage":          ["pothole", "road", "pavement", "crack"],
        "Electrical Issues":    ["wire", "electric", "power"],
        "Water Leakage":        ["water", "leak", "pipe"],
        "Waste Management":     ["garbage", "trash", "waste"],
        "Illegal Construction": ["illegal", "construction"],
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
        "reasoning":           f"Heuristic analysis (AI unavailable: {reason}).",
        "affected_population": "Unknown",
        "recommended_action":  "Assign to relevant department.",
        "ai_powered":          False,
    }