from rapidfuzz import process, fuzz
import re

def detect_hazards(text, rules):
    found_hazards = {}
    words = text.split()
    
    for category, keywords in rules['hazards'].items():
        matches = []
        for kw in keywords:
            # Match keywords with 90% spelling tolerance
            best_match = process.extractOne(kw, words, scorer=fuzz.WRatio)
            if best_match and best_match[1] >= 90:
                matches.append(kw)
        
        if matches:
            found_hazards[category] = matches
            
    return found_hazards

def detect_specific_thresholds(text):
    alerts = []
    
    # Methane Thresholds (CMR 2017 Reg 166/169)
    methane_values = re.findall(r"(\d+\.?\d*)\s*%", text)
    for val in methane_values:
        v = float(val)
        if v >= 2.0:
            alerts.append(f"CRITICAL: {v}% Methane detected. Evacuation required (Reg 166).")
        elif v >= 1.25:
            alerts.append(f"DANGER: {v}% Methane. Dangerous Occurrence - Form IV-A (Reg 169).")
        elif v >= 0.75:
            alerts.append(f"WARNING: {v}% Methane. Enhance ventilation immediately.")

    # Ventilation Compliance
    if "0.5" in text and "m/s" in text:
        if "below" in text or "less than" in text:
            alerts.append("COMPLIANCE: Air velocity below 0.5 m/s. Violation of CMR 2017.")
            
    return alerts
