import streamlit as st
import json
import pandas as pd
from utils.text_preprocessor import clean_text
from utils.hazard_classifier import detect_hazards, detect_specific_thresholds
from utils.risk_scorer import calculate_risk

st.set_page_config(page_title="Mine Safety DSS", page_icon="🛡️", layout="wide")

# Force memory clear
if 'report_input' not in st.session_state:
    st.session_state['report_input'] = ""

def hard_reset():
    st.session_state['report_input'] = ""
    st.cache_data.clear() # This clears the background memory
    st.rerun()

rules = None
try:
    with open('assets/dgms_hazard_rules.json', 'r') as f:
        rules = json.load(f)
except:
    st.error("Missing JSON rules file.")

st.sidebar.title("⛏️ DGMS Portal")
user_text = st.sidebar.text_area("Report Text:", value=st.session_state['report_input'], height=200, key="report_input")

col1, col2 = st.sidebar.columns(2)
run_btn = col1.button("🔍 Run Analysis", type="primary")
col2.button("🗑️ Clear All", on_click=hard_reset)

st.title("🛡️ Mine Safety Dashboard")

if run_btn and user_text and rules:
    cleaned = clean_text(user_text)
    hazards = detect_hazards(cleaned, rules)
    alerts = detect_specific_thresholds(cleaned)
    score, level, icon, form = calculate_risk(hazards, alerts)
    
    # DISPLAY RESULTS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Risk Score", f"{score}/100")
    m2.metric("Status", f"{icon} {level}")
    m3.metric("Statutory Form", form)
    m4.metric("Hazards", len(hazards))
    
    st.divider()
    if hazards:
        st.write("### Detected Hazards")
        st.write(", ".join(hazards.keys()))
    if alerts:
        for a in alerts: st.error(a)
else:
    st.info("Please enter text and click 'Run Analysis'.")
