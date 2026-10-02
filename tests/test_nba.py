from ml.nba.predict import get_customer_recommendation


def test_customer_recommendation():
    result = get_customer_recommendation(
        recency=66,
        frequency=2,
        monetary=500,
        total_quantity=100,
        avg_order_value=250
    )

    assert "customer_profile" in result
    assert "next_best_action" in result

    action = result["next_best_action"]

    assert "action" in action
    assert "priority" in action
    assert "reason" in action
    assert "rule_name" in action
