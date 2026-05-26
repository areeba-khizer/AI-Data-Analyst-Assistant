import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="InsightGPT", layout="wide")

st.title("📊 InsightGPT – AI Data Analyst (Gemini Powered)")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Ask Questions About Your Data")

    question = st.text_input("Type your question here")

    def get_ai_response(question, df):
        data_sample = df.head(25).to_csv(index=False)

        prompt = f"""
You are a senior data analyst AI.

You are given a dataset sample:

{data_sample}

User question:
{question}

Instructions:
- Give clear insights
- Use reasoning like a data analyst
- If needed, suggest calculations or trends
- Be concise but insightful
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    if question:
        with st.spinner("Analyzing with Gemini..."):
            answer = get_ai_response(question, df)

        st.subheader("AI Response")
        st.write(answer)