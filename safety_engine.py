"""
Safety Score Engine

Provides reusable functions to compute risk and safety scores from detections.
"""
from typing import List, Dict, Tuple

# Base risk mapping (matches app hazards)
HAZARD_RISK_MAP = {
    'Pothole': 20,
    'Flooded Road': 30,
    'Road Block': 40,
    'Garbage': 5,
    'Fallen Tree': 25,
    'Construction Area': 20,
    'Low Visibility': 20,
    'Damaged Road': 15
}


def compute_total_risk(detections: List[Dict]) -> int:
    """Compute total risk from a list of detections.

    Each detection is expected to have a 'label' field matching a hazard.
    If a label is unknown, it contributes zero risk by default.
    """
    total = 0
    for d in detections or []:
        label = d.get('label') if isinstance(d, dict) else None
        risk = HAZARD_RISK_MAP.get(label, 0)
        total += risk
    return int(total)


def risk_to_safety_score(risk: int, max_risk: int = 100) -> int:
    """Convert a raw risk (higher is worse) into a safety percentage (0-100).

    Safety = max(0, 100 - (risk / max_risk * 100)).
    """
    if risk <= 0:
        return 100
    score = max(0, 100 - (risk / max_risk * 100))
    return int(round(score))


def safety_level(score: int) -> str:
    if score >= 80:
        return 'Safe'
    if score >= 50:
        return 'Moderate'
    return 'Dangerous'


def generate_ai_report(detections: List[Dict], risk: int, score: int) -> Dict[str, str]:
    """Create a structured AI-style road safety report."""
    hazards = sorted({d.get('label', 'road hazard') for d in detections if d.get('label')})
    hazard_text = ', '.join(hazards) if hazards else 'no significant hazards'
    level = safety_level(score)
    if score >= 80:
        action = 'Proceed carefully and maintain awareness of the route ahead.'
        alternative = 'This route is currently recommended.'
    elif score >= 50:
        action = 'Slow down, watch for obstacles, and use an alternative route if conditions worsen.'
        alternative = 'Alternative Route B is recommended for a safer journey.'
    else:
        action = 'Avoid this route if possible; choose a safer alternative immediately.'
        alternative = 'Alternative Route C is recommended for maximum safety.'

    summary = (
        f"The road contains {hazard_text}. Traffic movement may be affected. "
        f"This route is {level.lower()} safe with a safety score of {score}%. "
        f"Recommendation: {alternative}"
    )

    return {
        'summary': summary,
        'hazard_text': hazard_text,
        'action': action,
        'alternative': alternative,
        'level': level,
        'score': score,
        'risk': risk,
        'hazards': hazards,
    }


def generate_ai_recommendation(detections: List[Dict], risk: int, score: int) -> str:
    return generate_ai_report(detections, risk, score)['summary']
