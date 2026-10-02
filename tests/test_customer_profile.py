from ml.customer_profile import create_customer_profile


def test_create_customer_profile():
    result = create_customer_profile(
        recency=200,
        frequency=2,
        monetary=500,
        total_quantity=100,
        avg_order_value=250
    )

    assert "segment" in result
    assert "cluster" in result
    assert "churn_probability" in result
    assert "churn_prediction" in result
    assert "risk_level" in result

    assert result["cluster"] in [0, 1, 2]
    assert 0.0 <= result["churn_probability"] <= 1.0
    assert result["churn_prediction"] in [0, 1]
    assert result["risk_level"] in ["Low", "Medium", "High"]
