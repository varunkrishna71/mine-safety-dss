import streamlit as st
import json
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Import custom utilities
from utils.text_preprocessor import extract_text_from_pdf, extract_text_from_docx, clean_text
from utils.hazard_classifier import detect_hazards, detect_specific_thresholds
from utils.risk_scorer import calculate_risk

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mine Safety DSS", page_icon="🛡️", layout="wide")

# --- SESSION STATE ---
if 'report_input' not in st.session_state:
    st.session_state['report_input'] = ""
if 'run_analysis' not in st.session_state:
    st.session_state['run_analysis'] = False

def clear_all():
    st.session_state['report_input'] = ""
    st.session_state['run_analysis'] = False
    st.rerun()

def trigger_analysis():
    st.session_state['run_analysis'] = True

# --- LOAD RULES ---
def load_rules():
    try:
        with open('assets/dgms_hazard_rules.json', 'r') as f:
            return json.load(f)
    except Exception:
        st.error("Missing assets/dgms_hazard_rules.json")
        return None

rules = load_rules()

# --- SIDEBAR ---
st.sidebar.markdown("# ⛏️ DGMS Safety Portal")
st.sidebar.markdown("---")

upload_mode = st.sidebar.radio("📁 Input Method", ["Manual Entry", "Document Upload"])
all_reports = []

if upload_mode == "Manual Entry":
    user_text = st.sidebar.text_area(
        "Paste Inspection Text:", 
        value=st.session_state['report_input'], 
        height=250, 
        key="report_input"
    )
    
    # MOBILE OPTIMIZED BUTTONS
    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        st.button("🔍 Run Analysis", on_click=trigger_analysis, type="primary")
    with col_b:
        st.button("🗑️ Clear", on_click=clear_all)
        
    if st.session_state['run_analysis'] and user_text:
        all_reports.append({"name": "Manual_Report", "content": user_text})
else:
    files = st.sidebar.file_uploader("Upload PDF/DOCX", type=['pdf', 'docx'], accept_multiple_files=True)
    if files:
        for f in files:
            if f.name.endswith('.pdf'):
                txt = extract_text_from_pdf(f)
            else:
                txt = extract_text_from_docx(f)
            all_reports.append({"name": f.name, "content": txt})
        st.session_state['run_analysis'] = True

# --- DASHBOARD LOGIC ---
st.title("🛡️ Mine Safety Decision Support System")
st.markdown("#### NLP Analysis for CMR 2017 Compliance")

if st.session_state['run_analysis'] and all_reports and rules:
    summary_data = []
    
    for r in all_reports:
        cleaned = clean_text(r['content'])
        hazards = detect_hazards(cleaned, rules)
        alerts = detect_specific_thresholds(cleaned)
        score, level, icon, form = calculate_risk(hazards, alerts)
        
        summary_data.append({
            "Report": r['name'], "Score": score, "Level": level,
            "icon": icon, "Form": form, "Hazards": list(hazards.keys()),
            "Alerts": alerts, "Raw": cleaned
        })

    latest = summary_data[-1]
    
    # 1. Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Risk Score", f"{latest['Score']}/100")
    m2.metric("Status", f"{latest['icon']} {latest['Level']}")
    m3.metric("DGMS Form", latest['Form'])
    m4.metric("Hazards Found", len(latest['Hazards']))

    # 2. Charts & WordCloud
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if latest['Hazards']:
            df_h = pd.DataFrame({"Category": latest['Hazards'], "Detected": [1]*len(latest['Hazards'])})
            fig = px.bar(df_h, x="Category", y="Detected", color="Category", title="Hazard Distribution", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        if latest['Raw'].strip():
            st.subheader("☁️ Word Cloud")
            wc = WordCloud(width=600, height=300, background_color="white").generate(latest['Raw'])
            st.image(wc.to_array(), use_container_width=True)

    with col2:
        st.subheader("💡 Interventions")
        if latest['Alerts']:
            for a in latest['Alerts']: st.error(f"⚠️ {a}")
        for h in latest['Hazards']:
            st.warning(f"**{h}:** {rules['recommendations'].get(h)}")
        
        st.subheader("📝 Summary")
        st.write(f"**{latest['Level']}** risk detected. Recommended Action: **{latest['Form']}**.")

else:
    st.info("👈 Paste the report text in the sidebar and click **'Run Analysis'** to begin.")
