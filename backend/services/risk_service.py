def compute_risk_score(style_similarity: float, activity_overlap: float, scam_pattern_score: float) -> float:
    raw = 100 * (0.4 * style_similarity + 0.3 * activity_overlap + 0.3 * scam_pattern_score)
    return round(max(0.0, min(raw, 100.0)), 2)


def risk_level(score: float) -> str:
    if score < 30:
        return "low"
    if score < 60:
        return "suspicious"
    return "high"
