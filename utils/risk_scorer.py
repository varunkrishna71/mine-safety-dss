def calculate_risk(hazards, alerts):
    score = 0 # Fresh start
    
    score += len(hazards) * 15
    
    for alert in alerts:
        if "CRITICAL" in alert:
            score += 50
        elif "DANGER" in alert:
            score += 30
            
    score = min(score, 100)
    
    # If it's a safe report (Case 3), force it below 20
    if len(hazards) == 0 and len(alerts) == 0:
        score = 10
        
    if score >= 70:
        return score, "HIGH", "🔴", "Form IV-A"
    elif score >= 35:
        return score, "MEDIUM", "🟡", "Form J"
    else:
        return score, "LOW", "🟢", "Form K"
