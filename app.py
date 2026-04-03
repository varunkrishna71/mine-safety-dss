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

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Mine Safety DSS", page_icon="🛡️", layout="wide")

# Initialize Session State for the text area
if 'report_text' not in st.session_state:
    st.session_state['report_text'] = ""

def clear_text():
    st.session_state['report_text'] = ""

# --- LOAD KNOWLEDGE BASE ---
def load_rules():
    try:
        with open('assets/dgms_hazard_rules.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: 'assets/dgms_hazard_rules.json' not found.")
        return None

rules = load_rules()

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("# ⛏️ DGMS Portal")
st.sidebar.markdown("---")

upload_mode = st.sidebar.radio("📁 Select Input Method", ["Manual Entry", "Document Upload"])
all_reports_data = []

if upload_mode == "Manual Entry":
    # Text area linked to session state
    text_input = st.sidebar.text_area(
        "Paste Inspection Report Text:", 
        value=st.session_state['report_text'], 
        height=300, 
        key="report_text"
    )
    
    # CLEAR BUTTON
    st.sidebar.button("🗑️ Clear Report", on_click=clear_text)
    
    if text_input:
        all_reports_data.append({"filename": "Manual_Entry", "content": text_input})
else:
    files = st.sidebar.file_uploader("Upload PDF or DOCX", type=['pdf', 'docx'], accept_multiple_files=True)
    for f in files:
        if f.name.endswith('.pdf'):
            content = extract_text_from_pdf(f)
        else:
            content = extract_text_from_docx(f)
        all_reports_data.append({"filename": f.name, "content": content})

# --- MAIN DASHBOARD ---
st.title("🛡️ Mine Safety Decision Support System")
st.markdown("#### NLP-Based Analysis for DGMS Compliance")

if all_reports_data and rules:
    summary_list = []
    
    for report in all_reports_data:
        raw_text = report['content']
        cleaned = clean_text(raw_text)
        hazards = detect_hazards(cleaned, rules)
        alerts = detect_specific_thresholds(cleaned)
        score, level, icon, form = calculate_risk(hazards, alerts)
        
        summary_list.append({
            "Report": report['filename'], "Risk Score": score, "Level": level,
            "icon": icon, "Reporting": form, "Hazards": list(hazards.keys()),
            "Alerts": alerts, "Text": cleaned
        })

    latest = summary_list[-1]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Risk Score", f"{latest['Risk Score']}/100")
    m2.metric("Safety Status", f"{latest['icon']} {latest['Level']}")
    m3.metric("Statutory Form", latest['Reporting'])
    m4.metric("Hazards Found", len(latest['Hazards']))

    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Hazard Analysis")
        if latest['Hazards']:
            h_df = pd.DataFrame({"Hazard": latest['Hazards'], "Count": [1]*len(latest['Hazards'])})
            fig = px.bar(h_df, x="Hazard", y="Count", color="Hazard", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        if len(summary_list) > 1:
            trend_df = pd.DataFrame(summary_list)
            fig_t = px.line(trend_df, x="Report", y="Risk Score", markers=True)
            st.plotly_chart(fig_t, use_container_width=True)

    with col2:
        st.subheader("💡 Recommendations")
        if latest['Alerts']:
            for a in latest['Alerts']: st.error(f"⚠️ {a}")
        for h in latest['Hazards']:
            st.warning(f"**{h}:** {rules['recommendations'].get(h)}")

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("☁️ Word Cloud")
        if latest['Text'].strip():
            wc = WordCloud(width=600, height=300, background_color="white").generate(latest['Text'])
            st.image(wc.to_array(), use_container_width=True)
    with c4:
        st.subheader("📝 Safety Summary")
        st.write(f"Analysis of **{latest['Report']}** indicates a **{latest['Level']}** risk. Suggests filing **{latest['Reporting']}**.")

else:
    st.info("👈 Please enter report text or upload a file in the sidebar to begin.")
