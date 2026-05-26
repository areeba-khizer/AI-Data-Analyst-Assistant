# 📊 InsightGPT – AI Data Analyst SaaS

InsightGPT is an AI-powered data analytics application that allows users to upload CSV files and interact with their data using natural language. It generates insights, charts, and executive reports using Gemini 2.5 Flash.

---

## 🚀 Features

### 🧠 AI Data Chat
Ask questions like:
- "What are the trends in this dataset?"
- "Why do customers churn?"
- "Which category performs best?"

### 📊 Autonomous Chart Generator
- AI automatically selects:
  - X-axis
  - Y-axis
  - Chart type (line, bar, scatter)

### 📌 AI Insights Engine
- Detects:
  - trends
  - anomalies
  - risks
  - opportunities

### 📄 Executive Report Generator
- Business-ready summary
- Risks + recommendations
- PDF export

### 🧯 Production-Grade Stability
- Retry + exponential backoff
- Fallback reporting system
- Safe error handling (no crashes)

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Google Gemini 2.5 Flash API
- ReportLab (PDF generation)
- Regex-based AI parsing (robust fallback system)

---

## ⚙️ Architecture

User → Streamlit UI → Gemini AI → Data Processing → Visualization Engine → Report Generator

---

## 📦 Installation

```bash
git clone https://github.com/your-username/insightgpt
cd insightgpt
pip install -r requirements.txt