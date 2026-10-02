from ml.churn.predict import predict_churn


def test_predict_churn():
    result = predict_churn(
        recency=200,
        frequency=2,
        monetary=500,
        total_quantity=100,
        avg_order_value=250
    )

    assert "churn_probability" in result
    assert "churn_prediction" in result
    assert "risk_level" in result

    assert 0.0 <= result["churn_probability"] <= 1.0
    assert result["churn_prediction"] in [0, 1]
    assert result["risk_level"] in ["Low", "Medium", "High"]
