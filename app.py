import streamlit as st
import pandas as pd
import time
import re
import os
from dotenv import load_dotenv
from google import genai
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# ENV SETUP
# -----------------------------
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="InsightGPT", layout="wide")
st.title("📊 InsightGPT – AI Data Analyst SaaS")

# -----------------------------
# SESSION STATE
# -----------------------------
if "last_report" not in st.session_state:
    st.session_state.last_report = None

if "last_report_time" not in st.session_state:
    st.session_state.last_report_time = 0

# -----------------------------
# SIDEBAR MODE
# -----------------------------
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Chat", "Insights", "Charts", "Report"]
)

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

# -----------------------------
# SAFE GEMINI CALL (PRODUCTION SAFE)
# -----------------------------
def safe_generate(prompt, retries=5):
    for i in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception:
            time.sleep(2 + i * 2)

    return "⚠️ AI is currently overloaded. Try again later."


# -----------------------------
# CHAT
# -----------------------------
def get_ai_response(prompt):
    return safe_generate(prompt)


# -----------------------------
# CHART PLANNER (NO JSON RELIANCE)
# -----------------------------
def get_chart_plan(question, columns):
    prompt = f"""
You are a data visualization assistant.

User question:
{question}

Columns:
{columns}

Return ONLY format:

x_axis: column
y_axis: column
chart_type: line | bar | scatter
"""

    result = safe_generate(prompt)

    try:
        x = re.search(r"x_axis:\s*(.*)", result).group(1).strip()
        y = re.search(r"y_axis:\s*(.*)", result).group(1).strip()
        c = re.search(r"chart_type:\s*(.*)", result).group(1).strip().lower()

        return {"x_axis": x, "y_axis": y, "chart_type": c}
    except:
        return None


# -----------------------------
# FALLBACK CHART
# -----------------------------
def fallback_chart(df):
    num_cols = df.select_dtypes(include=["number"]).columns
    if len(num_cols) >= 2:
        return px.scatter(df, x=num_cols[0], y=num_cols[1])
    return None


# -----------------------------
# PDF GENERATOR
# -----------------------------
def generate_pdf(text):
    file_path = "InsightGPT_Report.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 6))

    doc.build(content)
    return file_path


# -----------------------------
# MAIN APP
# -----------------------------
if uploaded_file:

    df = pd.read_csv(uploaded_file)
    sample = df.head(20).to_csv(index=False)

    # -------------------------
    # DATA PREVIEW
    # -------------------------
    st.subheader("📂 Dataset Preview")
    st.dataframe(df.head())

    st.subheader("📊 Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing Values", df.isnull().sum().sum())

    # =====================================================
    # CHAT MODE
    # =====================================================
    if mode == "Chat":

        q = st.text_input("Ask your data")

        if q:
            prompt = f"""
You are a senior data analyst.

Dataset:
{sample}

Question:
{q}

Explain clearly with insights.
"""

            with st.spinner("Thinking..."):
                res = get_ai_response(prompt)

            st.write(res)

    # =====================================================
    # INSIGHTS MODE
    # =====================================================
    elif mode == "Insights":

        if st.button("Generate Insights"):

            prompt = f"""
You are a senior analyst.

Dataset:
{sample}

Generate:
- trends
- risks
- anomalies
- opportunities
"""

            with st.spinner("Generating..."):
                res = get_ai_response(prompt)

            st.write(res)

        if st.button("Executive Summary"):

            prompt = f"""
You are a CEO-level analyst.

Dataset:
{sample}

Write a 60-second executive summary:
- key findings
- risks
- opportunities
- recommendation
"""

            with st.spinner("Generating..."):
                res = get_ai_response(prompt)

            st.success(res)

    # =====================================================
    # CHART MODE
    # =====================================================
    elif mode == "Charts":

        q = st.text_input("Describe chart")

        if q:

            plan = get_chart_plan(q, df.columns.tolist())

            if plan is None:
                st.warning("Fallback chart used")
                fig = fallback_chart(df)
                if fig:
                    st.plotly_chart(fig)
            else:
                try:
                    st.json(plan)

                    if plan["chart_type"] == "line":
                        fig = px.line(df, x=plan["x_axis"], y=plan["y_axis"])
                    elif plan["chart_type"] == "bar":
                        fig = px.bar(df, x=plan["x_axis"], y=plan["y_axis"])
                    else:
                        fig = px.scatter(df, x=plan["x_axis"], y=plan["y_axis"])

                    st.plotly_chart(fig)

                except:
                    fig = fallback_chart(df)
                    if fig:
                        st.plotly_chart(fig)

    # =====================================================
    # REPORT MODE (FULLY STABLE)
    # =====================================================
    elif mode == "Report":

        st.subheader("📄 AI Business Report Generator")

        # rate limit protection
        if st.button("Generate Report"):

            if time.time() - st.session_state.last_report_time < 10:
                st.warning("Please wait a few seconds before regenerating report.")
                st.stop()

            st.session_state.last_report_time = time.time()

            prompt = f"""
You are a senior business analyst.

Dataset:
{sample}

Create report:
1. Summary
2. Insights
3. Risks
4. Opportunities
5. Recommendations
"""

            with st.spinner("Generating report..."):
                report = safe_generate(prompt)

            # fallback if AI fails
            if "busy" in report.lower():
                report = f"""
BUSINESS REPORT (FALLBACK)

Summary:
Dataset has {df.shape[0]} rows and {df.shape[1]} columns.

Note:
AI temporarily unavailable.

Recommendation:
Retry in a few seconds.
"""

            st.session_state.last_report = report

            st.success("Report Ready")
            st.write(report)

        # download last report
        if st.session_state.last_report:

            st.subheader("📥 Download Report")

            pdf_path = generate_pdf(st.session_state.last_report)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    "Download PDF",
                    f,
                    file_name="InsightGPT_Report.pdf",
                    mime="application/pdf"
                )

            if st.button("Show Last Report"):
                st.write(st.session_state.last_report)