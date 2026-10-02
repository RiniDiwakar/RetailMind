from ml.segmentation.predict import predict_segment


def test_predict_segment():
    result = predict_segment(
        recency=20,
        frequency=10,
        monetary=3000
    )

    assert "cluster" in result
    assert "segment" in result
    assert result["cluster"] in [0, 1, 2]
    assert result["segment"] in [
        "Active / Regular",
        "Inactive / At Risk",
        "VIP / High Value"
    ]
