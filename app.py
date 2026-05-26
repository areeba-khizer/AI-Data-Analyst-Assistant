import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="InsightGPT",
    page_icon="📊",
    layout="wide"
)

st.title("📊 InsightGPT – AI Data Analyst Assistant")

st.write("Upload a CSV file and start analyzing your data with AI.")

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Dataset Information")

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())