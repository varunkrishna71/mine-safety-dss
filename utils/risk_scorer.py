def calculate_risk(hazards, alerts):
    # Total Reset
    score = 0
    
    # 1. Base Score: 15 per hazard
    score += len(hazards) * 15
    
    # 2. Alert Bonuses
    for alert in alerts:
        if "CRITICAL" in alert:
            score += 50
        elif "DANGER" in alert:
            score += 30
            
    # Final Cap
    score = min(score, 100)
    
    # If no hazards and no alerts, score MUST be low
    if len(hazards) == 0 and len(alerts) == 0:
        score = 5 # Baseline for routine inspection
        
    if score >= 70:
        return score, "HIGH", "🔴", "Form IV-A"
    elif score >= 35:
        return score, "MEDIUM", "🟡", "Form J"
    else:
        return score, "LOW", "🟢", "Form K"
