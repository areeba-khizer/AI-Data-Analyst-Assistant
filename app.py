import streamlit as st
import pandas as pd
import os
import time
import re
from dotenv import load_dotenv
from google import genai
import plotly.express as px

# -----------------------------
# ENV SETUP
# -----------------------------
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="InsightGPT", layout="wide")
st.title("📊 InsightGPT – Autonomous AI Data Analyst")

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# -----------------------------
# SAFE GEMINI CALL (handles 503)
# -----------------------------
def safe_generate(prompt, retries=3):
    for i in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception:
            time.sleep(2 ** i)

    return "⚠️ AI is busy. Please try again."


# -----------------------------
# CHAT RESPONSE
# -----------------------------
def get_ai_response(prompt):
    return safe_generate(prompt)


# -----------------------------
# ROBUST CHART PARSER (NO JSON RELIANCE)
# -----------------------------
def get_chart_plan(question, columns):
    prompt = f"""
You are a data analyst.

User question:
{question}

Available columns:
{columns}

Return ONLY in this format:

x_axis: <column>
y_axis: <column>
chart_type: line OR bar OR scatter

NO explanation. NO JSON. ONLY raw text.
"""

    result = safe_generate(prompt)

    try:
        # extract values using regex (VERY IMPORTANT FIX)
        x = re.search(r"x_axis:\s*(.*)", result).group(1).strip()
        y = re.search(r"y_axis:\s*(.*)", result).group(1).strip()
        chart_type = re.search(r"chart_type:\s*(.*)", result).group(1).strip().lower()

        return {
            "x_axis": x,
            "y_axis": y,
            "chart_type": chart_type
        }

    except Exception:
        return None


# -----------------------------
# FALLBACK CHART
# -----------------------------
def fallback_chart(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns

    if len(numeric_cols) >= 2:
        return px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])

    return None


# -----------------------------
# MAIN APP
# -----------------------------
if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # Dataset preview
    st.subheader("📂 Dataset Preview")
    st.dataframe(df.head())

    # Stats
    st.subheader("📊 Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing Values", df.isnull().sum().sum())

    # -----------------------------
    # AI CHAT
    # -----------------------------
    st.subheader("🧠 Ask AI About Your Data")

    question = st.text_input("Ask anything about your dataset")

    if question:
        sample = df.head(30).to_csv(index=False)

        prompt = f"""
You are a senior data analyst.

Dataset:
{sample}

Question:
{question}

Give:
- clear answer
- business insight
"""

        with st.spinner("Thinking..."):
            answer = get_ai_response(prompt)

        st.success("AI Response")
        st.write(answer)

    # -----------------------------
    # INSIGHTS
    # -----------------------------
    st.subheader("📌 Auto Insights")

    if st.button("Generate Insights"):
        sample = df.head(50).to_csv(index=False)

        insight_prompt = f"""
You are a senior data analyst.

Dataset:
{sample}

Generate:
- trends
- anomalies
- patterns
- business insights
"""

        with st.spinner("Generating insights..."):
            insights = get_ai_response(insight_prompt)

        st.write(insights)

    # -----------------------------
    # AUTONOMOUS CHART ENGINE (FIXED)
    # -----------------------------
    st.subheader("📊 Autonomous AI Chart Generator")

    chart_question = st.text_input(
        "Describe chart (e.g. churn by contract type)"
    )

    if chart_question:

        plan = get_chart_plan(chart_question, df.columns.tolist())

        if plan is None:
            st.warning("AI failed → showing fallback chart")

            fig = fallback_chart(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        else:
            try:
                x = plan["x_axis"]
                y = plan["y_axis"]
                chart_type = plan["chart_type"]

                st.json(plan)

                # safe chart rendering
                if chart_type == "line":
                    fig = px.line(df, x=x, y=y)
                elif chart_type == "bar":
                    fig = px.bar(df, x=x, y=y)
                else:
                    fig = px.scatter(df, x=x, y=y)

                st.plotly_chart(fig, use_container_width=True)

            except Exception:
                st.warning("Chart rendering failed → fallback mode")

                fig = fallback_chart(df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)