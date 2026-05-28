import time
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.ai import safe_generate
from utils.charts import get_chart_plan
from utils.charts import fallback_chart
from utils.pdf_generator import generate_pdf
from utils.report_utils import build_fallback_report


st.set_page_config(page_title="InsightGPT", layout="wide")

st.title("📊 InsightGPT – AI Data Analyst SaaS")

st.sidebar.info(
    "Uploaded files are processed temporarily in-memory and are not stored permanently. "
    "Avoid uploading sensitive or personally identifiable data."
)

if "last_report" not in st.session_state:
    st.session_state.last_report = None

if "last_report_time" not in st.session_state:
    st.session_state.last_report_time = 0


mode = st.sidebar.selectbox(
    "Select Mode",
    ["Chat", "Insights", "Charts", "Report"]
)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])


if uploaded_file:

    df = pd.read_csv(uploaded_file)
    sample = df.head(20).to_csv(index=False)

    st.subheader("📂 Dataset Preview")
    st.dataframe(df.head())

    st.subheader("📊 Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing Values", int(df.isnull().sum().sum()))

    # =====================================================
    # CHAT MODE
    # =====================================================

    if mode == "Chat":

        st.subheader("🧠 Chat with Your Data")

        question = st.text_input("Ask a question")

        if question:

            prompt = f"""
You are a senior data analyst.

Dataset:
{sample}

Question:
{question}

Provide concise and useful insights.
"""

            with st.spinner("Thinking..."):
                response = safe_generate(prompt)

            st.write(response)

    # =====================================================
    # INSIGHTS MODE
    # =====================================================

    elif mode == "Insights":

        st.subheader("📌 AI Insights Engine")

        if st.button("Generate Insights"):

            prompt = f"""
You are a senior analyst.

Dataset:
{sample}

Generate:
- trends
- anomalies
- risks
- opportunities
"""

            with st.spinner("Generating insights..."):
                response = safe_generate(prompt)

            st.write(response)

        if st.button("Executive Summary"):

            prompt = f"""
You are a CEO-level business analyst.

Dataset:
{sample}

Write a short executive summary:
- key findings
- risks
- opportunities
- recommendations
"""

            with st.spinner("Generating summary..."):
                response = safe_generate(prompt)

            st.success(response)

    # =====================================================
    # CHART MODE
    # =====================================================

    elif mode == "Charts":

        st.subheader("📊 Autonomous Chart Generator")

        chart_request = st.text_input(
            "Describe chart (e.g. churn by contract type)"
        )

        if chart_request:

            plan = get_chart_plan(
                chart_request,
                df.columns.tolist()
            )

            if plan is None:
                st.warning("AI could not determine chart plan. Using fallback chart.")

                figure = fallback_chart(df)

                if figure:
                    st.plotly_chart(figure, use_container_width=True)

            else:
                try:
                    st.json(plan)

                    if plan["chart_type"] == "line":
                        figure = px.line(
                            df,
                            x=plan["x_axis"],
                            y=plan["y_axis"]
                        )

                    elif plan["chart_type"] == "bar":
                        figure = px.bar(
                            df,
                            x=plan["x_axis"],
                            y=plan["y_axis"]
                        )

                    else:
                        figure = px.scatter(
                            df,
                            x=plan["x_axis"],
                            y=plan["y_axis"]
                        )

                    st.plotly_chart(figure, use_container_width=True)

                except (KeyError, ValueError) as error:
                    st.error(f"Chart generation failed: {error}")

                    fallback = fallback_chart(df)

                    if fallback:
                        st.plotly_chart(fallback, use_container_width=True)

    # =====================================================
    # REPORT MODE
    # =====================================================

    elif mode == "Report":

        st.subheader("📄 AI Business Report Generator")

        if st.button("Generate Report"):

            if time.time() - st.session_state.last_report_time < 10:
                st.warning("Please wait before generating another report.")
                st.stop()

            st.session_state.last_report_time = time.time()

            prompt = f"""
You are a senior business analyst.

Dataset:
{sample}

Create:
1. Executive Summary
2. Key Insights
3. Risks
4. Opportunities
5. Recommendations
"""

            with st.spinner("Generating report..."):
                report = safe_generate(prompt)

            if "overloaded" in report.lower():
                report = build_fallback_report(df)

            st.session_state.last_report = report

            st.success("Report Ready")
            st.write(report)

        if st.session_state.last_report:

            pdf_path = generate_pdf(st.session_state.last_report)

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    "📥 Download PDF Report",
                    pdf_file,
                    file_name="InsightGPT_Report.pdf",
                    mime="application/pdf"
                )