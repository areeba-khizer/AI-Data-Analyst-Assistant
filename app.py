import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
import plotly.express as px

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="InsightGPT", layout="wide")

st.title("📊 InsightGPT – AI Data Analyst (Phase 3)")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

def get_ai_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Ask Questions")

    question = st.text_input("Type your question")

    # -----------------------------
    # AI CHAT
    # -----------------------------
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
- short explanation
"""

        with st.spinner("Thinking..."):
            answer = get_ai_response(prompt)

        st.subheader("AI Response")
        st.write(answer)

    # -----------------------------
    # AI INSIGHTS BUTTON
    # -----------------------------
    st.subheader("📌 Auto Insights")

    if st.button("Generate Insights"):
        sample = df.head(50).to_csv(index=False)

        insight_prompt = f"""
You are a senior data analyst.

Dataset:
{sample}

Task:
Generate key insights:
- trends
- anomalies
- top performers
- patterns
- business interpretation

Keep it structured and concise.
"""

        with st.spinner("Generating insights..."):
            insights = get_ai_response(insight_prompt)

        st.write(insights)

    # -----------------------------
    # AUTO CHART GENERATOR
    # -----------------------------
    st.subheader("📊 Auto Chart Generator")

    columns = df.columns.tolist()

    col1, col2 = st.columns(2)

    x_axis = col1.selectbox("X-axis", columns)
    y_axis = col2.selectbox("Y-axis (numeric)", columns)

    chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Scatter"])

    if st.button("Generate Chart"):
        if chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis)
        elif chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis)
        else:
            fig = px.scatter(df, x=x_axis, y=y_axis)

        st.plotly_chart(fig, use_container_width=True)