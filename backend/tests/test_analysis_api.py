from datetime import datetime, timezone


def test_similarity_endpoint(client) -> None:
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "account_a": {"texts": ["hello!!!", "buy now"], "timestamps": [now, now]},
        "account_b": {"texts": ["hello!!", "buy now!!!"], "timestamps": [now, now]},
        "scam_pattern_score": 0.8,
    }

    res = client.post("/analysis/similarity", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert 0 <= body["style_similarity"] <= 1
    assert 0 <= body["activity_similarity"] <= 1
    assert 0 <= body["risk_score"] <= 100
    assert body["risk_level"] in {"low", "suspicious", "high"}
