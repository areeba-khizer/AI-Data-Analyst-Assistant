def test_chart_plan_regex_parsing():

    response = """
x_axis: tenure
y_axis: MonthlyCharges
chart_type: scatter
"""

    assert "x_axis" in response
    assert "y_axis" in response
    assert "chart_type" in response