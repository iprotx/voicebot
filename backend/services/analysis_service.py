from __future__ import annotations

from datetime import datetime
import math

from backend.services.feature_service import FeatureExtractor
from backend.services.risk_service import compute_risk_score, risk_level


class AnalysisService:
    def __init__(self) -> None:
        self.extractor = FeatureExtractor()

    def compare_accounts(
        self,
        texts_a: list[str],
        timestamps_a: list[datetime],
        texts_b: list[str],
        timestamps_b: list[datetime],
        scam_pattern_score: float = 0.0,
    ) -> dict[str, float | str | bool]:
        features_a = self.extractor.extract(texts_a, timestamps_a)
        features_b = self.extractor.extract(texts_b, timestamps_b)

        style_similarity = self._cosine(features_a.style_vector, features_b.style_vector)
        activity_similarity = self._cosine(features_a.activity_vector, features_b.activity_vector)

        score = compute_risk_score(style_similarity, activity_similarity, scam_pattern_score)
        return {
            "style_similarity": round(style_similarity, 4),
            "activity_similarity": round(activity_similarity, 4),
            "risk_score": score,
            "risk_level": risk_level(score),
            "is_related": (style_similarity + activity_similarity) / 2 >= 0.9,
        }

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return max(0.0, min(dot / (norm_a * norm_b), 1.0))
