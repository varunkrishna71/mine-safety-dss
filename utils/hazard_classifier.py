from rapidfuzz import process, fuzz

def detect_hazards(text, rules):
    detected = {}
    if not text or len(text.strip()) < 10: # Safety check for empty text
        return detected
        
    text_lower = text.lower()
    
    for category, keywords in rules['hazards'].items():
        for kw in keywords:
            # Using a stricter threshold (85) to avoid false positives
            if kw.lower() in text_lower:
                detected[category] = kw
                break 
    return detected

def detect_specific_thresholds(text):
    alerts = []
    import re
    
    # Methane patterns
    methane_val = re.findall(r"(\d+\.?\d*)\s*%\s*methane", text.lower())
    if methane_val:
        val = float(methane_val[0])
        if val > 2.0:
            alerts.append(f"CRITICAL: Methane at {val}% exceeds CMR 2017 evacuation limits!")
        elif val >= 1.25:
            alerts.append(f"DANGER: Methane at {val}% requires immediate ventilation adjustment.")
            
    if "evacuation" in text.lower() or "emergency" in text.lower():
        alerts.append("CRITICAL: Manual evacuation order detected in report.")
        
    return alerts
