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
st.set_page_config(
    page_title="Mine Safety DSS", 
    page_icon="🛡️", 
    layout="wide"
)

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
st.sidebar.markdown("### Safety Monitoring System")
st.sidebar.markdown("---")

upload_mode = st.sidebar.radio("📁 Select Input Method", ["Manual Entry", "Document Upload"])
all_reports_data = []

if upload_mode == "Manual Entry":
    text_input = st.sidebar.text_area("Paste Inspection Report Text here:", height=300)
    if text_input:
        all_reports_data.append({"filename": "Manual_Entry_Report", "content": text_input})
else:
    files = st.sidebar.file_uploader("Upload PDF or DOCX Reports", type=['pdf', 'docx'], accept_multiple_files=True)
    for f in files:
        if f.name.endswith('.pdf'):
            content = extract_text_from_pdf(f)
        else:
            content = extract_text_from_docx(f)
        all_reports_data.append({"filename": f.name, "content": content})

# --- MAIN DASHBOARD ---
st.title("🛡️ Mine Safety Decision Support System")
st.markdown("#### NLP-Based Analysis for DGMS Compliance & CMR 2017")
st.info("This system uses Text Mining to identify hazards and suggest regulatory actions.")

if all_reports_data and rules:
    summary_list = []
    
    # Process each report
    for report in all_reports_data:
        raw_text = report['content']
        cleaned = clean_text(raw_text)
        
        hazards = detect_hazards(cleaned, rules)
        alerts = detect_specific_thresholds(cleaned)
        score, level, icon, form = calculate_risk(hazards, alerts)
        
        summary_list.append({
            "Report": report['filename'],
            "Risk Score": score,
            "Level": level,
            "icon": icon,
            "Reporting": form,
            "Hazards": list(hazards.keys()),
            "Alerts": alerts,
            "Text": cleaned
        })

    # --- TOP METRICS SECTION ---
    latest = summary_list[-1]
    m1, m2, m3, m4 = st.columns(4)
    
    m1.metric("Risk Score", f"{latest['Risk Score']}/100")
    m2.metric("Safety Status", f"{latest['icon']} {latest['Level']}")
    m3.metric("Statutory Form", latest['Reporting'])
    m4.metric("Hazards Found", len(latest['Hazards']))

    # --- VISUALIZATION SECTION ---
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Hazard Analysis & Trends")
        
        if latest['Hazards']:
            h_df = pd.DataFrame({"Hazard Category": latest['Hazards'], "Count": [1]*len(latest['Hazards'])})
            fig = px.bar(h_df, x="Hazard Category", y="Count", color="Hazard Category", 
                         title="Detected Hazards", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No major hazard keywords detected.")

        if len(summary_list) > 1:
            trend_df = pd.DataFrame(summary_list)
            fig_trend = px.line(trend_df, x="Report", y="Risk Score", 
                                title="Safety Risk Trend Comparison", markers=True)
            st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.subheader("💡 Recommendations")
        if latest['Alerts']:
            st.error("⚠️ **Regulatory Alerts:**")
            for alert in latest['Alerts']:
                st.write(f"- {alert}")
        
        st.markdown("**Safety Interventions:**")
        for h in latest['Hazards']:
            rec = rules['recommendations'].get(h, "Follow Standard Operating Procedures.")
            st.warning(f"**{h}:** {rec}")
        
        if not latest['Hazards']:
            st.info("Continue routine monitoring as per Safety Management Plan (SMP).")

    # --- WORDCLOUD & SUMMARY SECTION ---
    st.markdown("---")
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("☁️ Inspection Word Cloud")
        if latest['Text'].strip():
            wc = WordCloud(width=600, height=300, background_color="white", 
                           colormap='viridis').generate(latest['Text'])
            st.image(wc.to_array(), use_container_width=True)

    with c4:
        st.subheader("📝 Automated Safety Summary")
        summary_text = (
            f"Analysis of **{latest['Report']}** indicates a **{latest['Level']}** risk level "
            f"with a quantified score of **{latest['Risk Score']}**. "
        )
        if latest['Hazards']:
            summary_text += f"The primary concerns identified are: {', '.join(latest['Hazards'])}. "
        
        summary_text += (
            f"Based on CMR 2017 provisions, this situation warrants filing **{latest['Reporting']}**."
        )
        st.write(summary_text)

else:
    st.markdown("### 📋 Instructions")
    st.write("1. Select **Manual Entry** or **Document Upload** in the sidebar.")
    st.write("2. Provide the DGMS inspection report text.")
    st.write("3. The system will generate safety analytics automatically.")
    st.success("Ready for Analysis. Please provide input data.")
