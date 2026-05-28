import re
import pandas as pd
import plotly.express as px

from utils.ai import safe_generate


def get_chart_plan(question: str, columns: list[str]) -> dict | None:
    """Generate chart plan from AI."""

    prompt = f"""
You are a data visualization assistant.

User question:
{question}

Available columns:
{columns}

Return ONLY:

x_axis: column_name
y_axis: column_name
chart_type: line | bar | scatter
"""

    result = safe_generate(prompt)

    try:
        x_axis = re.search(r"x_axis:\\s*(.*)", result).group(1).strip()
        y_axis = re.search(r"y_axis:\\s*(.*)", result).group(1).strip()
        chart_type = re.search(r"chart_type:\\s*(.*)", result).group(1).strip().lower()

        return {
            "x_axis": x_axis,
            "y_axis": y_axis,
            "chart_type": chart_type
        }

    except (AttributeError, ValueError):
        return None


def fallback_chart(df: pd.DataFrame):
    """Generate fallback scatter chart."""

    numeric_columns = df.select_dtypes(include=["number"]).columns

    if len(numeric_columns) >= 2:
        return px.scatter(
            df,
            x=numeric_columns[0],
            y=numeric_columns[1]
        )

    return None