from backend.services.risk_service import compute_risk_score, risk_level


def test_risk_score_and_level() -> None:
    score = compute_risk_score(0.95, 0.7, 0.8)
    assert score == 83.0
    assert risk_level(score) == "high"
