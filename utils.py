# Utility functions for SafePath AI

def calculate_safety_score(risk_score):
    """
    Converts a raw risk score into a safety score (0-100) and a recommendation.
    """
    safety_score = max(0, 100 - risk_score) # Simple inverse relationship
    
    recommendation = "Safe"
    if risk_score > 50:
        recommendation = "Dangerous"
    elif risk_score > 20:
        recommendation = "Moderate"
        
    return safety_score, recommendation

# Add other utility functions here as needed
