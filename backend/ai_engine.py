"""
AI Risk Engine — scores a civic report 0-100 based on
keyword analysis of description and assigns category + priority.
Pure Python, no external AI API needed.
"""

import re

CATEGORY_KEYWORDS = {
    "Road Damage": [
        "pothole", "crack", "broken road", "road damage", "pavement",
        "asphalt", "speed bump", "road broken", "highway damage", "pit"
    ],
    "Waste Management": [
        "garbage", "trash", "waste", "dump", "litter", "sewage",
        "smell", "odor", "dirty", "filth", "bin overflow", "garbage pile"
    ],
    "Electrical Issues": [
        "wire", "electric", "power", "outage", "shock", "spark",
        "cable", "transformer", "streetlight", "light not working", "electrocution"
    ],
    "Water Leakage": [
        "leak", "water", "flood", "pipe", "drainage", "overflow",
        "burst", "puddle", "waterlogging", "sewage overflow", "tap"
    ],
    "Illegal Construction": [
        "illegal", "unauthorized", "encroach", "construction",
        "building violation", "blocked road", "obstruction", "demolish"
    ],
}

SEVERITY_BOOSTERS = {
    "high": ["dangerous", "hazard", "fatal", "serious", "urgent", "critical",
             "emergency", "severe", "life threatening", "accident", "fire", "explosion"],
    "medium": ["bad", "significant", "concerning", "moderate", "issue", "problem"],
    "low": ["minor", "small", "tiny", "slight", "little", "not urgent"],
}


def detect_category(description: str) -> str:
    text = description.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text)
        scores[category] = count
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Road Damage"


def calculate_risk_score(description: str, category: str) -> int:
    text = description.lower()
    base_score = 30  # default baseline

    # Category base scores
    category_base = {
        "Electrical Issues": 55,
        "Water Leakage": 45,
        "Road Damage": 40,
        "Illegal Construction": 35,
        "Waste Management": 25,
    }
    base_score = category_base.get(category, 30)

    # Boost/reduce by severity keywords
    for kw in SEVERITY_BOOSTERS["high"]:
        if kw in text:
            base_score += 15
            break

    for kw in SEVERITY_BOOSTERS["medium"]:
        if kw in text:
            base_score += 7
            break

    for kw in SEVERITY_BOOSTERS["low"]:
        if kw in text:
            base_score -= 10
            break

    # Length of description adds minor detail score
    word_count = len(description.split())
    if word_count > 30:
        base_score += 5
    elif word_count < 5:
        base_score -= 5

    return max(0, min(100, base_score))


def get_priority(score: int) -> str:
    if score >= 71:
        return "High"
    elif score >= 31:
        return "Medium"
    return "Low"


def analyze_report(description: str) -> dict:
    category = detect_category(description)
    score = calculate_risk_score(description, category)
    priority = get_priority(score)
    return {
        "category": category,
        "risk_score": score,
        "priority": priority,
    }