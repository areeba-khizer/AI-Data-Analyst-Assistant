import pandas as pd


def build_fallback_report(df: pd.DataFrame) -> str:
    """Generate fallback report if AI fails."""

    return f"""
BUSINESS REPORT (FALLBACK MODE)

Summary:
Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.

Insights:
- Dataset uploaded successfully
- AI service temporarily unavailable
- Fallback reporting activated

Recommendation:
Retry report generation in a few seconds.
"""