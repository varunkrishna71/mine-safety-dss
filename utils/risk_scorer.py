def calculate_risk(hazards, alerts):
    # Initialize score at zero for every new report
    score = 0
    
    # 1. Base Score: 15 points for every unique hazard category found
    score += len(hazards) * 15
    
    # 2. Regulatory Severity Bonuses (CMR 2017)
    for alert in alerts:
        if "CRITICAL" in alert: 
            score += 45  # e.g., 2% Methane
        elif "DANGER" in alert: 
            score += 25  # e.g., 1.25% Methane
        elif "WARNING" in alert: 
            score += 10
            
    # Cap the score at 100
    score = min(score, 100)
    
    # 3. Determine Level and Statutory Form
    if score >= 70:
        return score, "HIGH", "🔴", "Form IV-A (Dangerous Occurrence)"
    elif score >= 35:
        return score, "MEDIUM", "🟡", "Form J (Serious Deficiency)"
    else:
        return score, "LOW", "🟢", "Form K (Routine Observation)"
