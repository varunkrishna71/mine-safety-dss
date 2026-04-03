def calculate_risk(hazards, alerts):
    # Base score per hazard category
    score = len(hazards) * 15
    
    # Weightage for critical alerts
    for alert in alerts:
        if "CRITICAL" in alert: score += 40
        if "DANGER" in alert: score += 25
        if "WARNING" in alert: score += 10
        
    score = min(score, 100) # Cap at 100
    
    if score >= 70:
        return score, "HIGH", "🔴", "Form IV-A (Dangerous Occurrence)"
    elif score >= 40:
        return score, "MEDIUM", "🟡", "Form J (Serious Deficiency)"
    else:
        return score, "LOW", "🟢", "Form K (Routine Observation)"
