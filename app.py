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

# --- RESET LOGIC ---
def reset_application():
    st.cache_data.clear()
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- SIDEBAR ---
st.sidebar.title("⛏️ DGMS Safety Portal")
st.sidebar.markdown("---")

input_mode = st.sidebar.radio("📁 Select Input Method", ["Manual Entry", "Upload Document"])
report_text = ""
report_name = ""

if input_mode == "Manual Entry":
    report_text = st.sidebar.text_area("Paste Inspection Report:", height=250, key="manual_in")
    report_name = "Manual_Report"
else:
    uploaded_file = st.sidebar.file_uploader("Upload PDF or DOCX", type=['pdf', 'docx'])
    if uploaded_file:
        report_name = uploaded_file.name
        if report_name.endswith('.pdf'):
            report_text = extract_text_from_pdf(uploaded_file)
        else:
            report_text = extract_text_from_docx(uploaded_file)

# ACTION BUTTONS
col_btn1, col_btn2 = st.sidebar.columns(2)
run_analysis = col_btn1.button("🔍 Run Analysis", type="primary")
if col_btn2.button("🗑️ Reset App"):
    reset_application()

# --- MAIN DASHBOARD ---
st.title("🛡️ Mine Safety Decision Support System")
st.markdown("#### NLP-Based Analysis for CMR 2017 Compliance")

if run_analysis and report_text:
    # Load Rules
    try:
        with open('assets/dgms_hazard_rules.json', 'r') as f:
            rules = json.load(f)
    except:
        st.error("Error: Could not find hazard rules JSON.")
        st.stop()

    # 1. Processing Logic
    cleaned = clean_text(report_text)
    hazards = detect_hazards(cleaned, rules)
    alerts = detect_specific_thresholds(cleaned)
    score, level, icon, form = calculate_risk(hazards, alerts)
    
    # 2. Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Risk Score", f"{score}/100")
    m2.metric("Safety Status", f"{icon} {level}")
    m3.metric("Statutory Form", form)
    m4.metric("Hazards Found", len(hazards))
    
    st.divider()

    # 3. Visual Analysis (Text Mining & Charts)
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.subheader("📊 Hazard Distribution")
        if hazards:
            df = pd.DataFrame({"Category": list(hazards.keys()), "Count": [1]*len(hazards)})
            fig = px.bar(df, x="Category", y="Count", color="Category", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No major hazards detected.")

        # WORD CLOUD (TEXT MINING)
        st.subheader("☁️ Text Mining: Word Cloud")
        if len(cleaned) > 10:
            wc = WordCloud(width=800, height=400, background_color="white", max_words=50).generate(cleaned)
            fig_wc, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig_wc)
        else:
            st.info("Not enough text for word cloud analysis.")

    with right_col:
        st.subheader("💡 Recommendations")
        if alerts:
            for a in alerts: st.error(f"⚠️ {a}")
        
        for h in hazards:
            st.warning(f"**{h}:** {rules['recommendations'].get(h, 'Follow Standard Safety Procedures.')}")
            
        st.info(f"**Summary:** Analysis of {report_name} indicates {level} risk. Filing {form} is recommended.")

elif run_analysis and not report_text:
    st.warning("Please provide report text or upload a document first.")
else:
    st.info("👈 Use the sidebar to provide input data and click 'Run Analysis'.")
