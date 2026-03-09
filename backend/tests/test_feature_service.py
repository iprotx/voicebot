from datetime import datetime, timezone

from backend.services.feature_service import FeatureExtractor


def test_feature_extractor_vectors_shapes() -> None:
    extractor = FeatureExtractor()
    features = extractor.extract(
        texts=["hello!!!", "buy now 💰"],
        timestamps=[
            datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 10, 0, 30, tzinfo=timezone.utc),
        ],
    )

    assert len(features.style_vector) == 3
    assert len(features.emoji_vector) == 2
    assert len(features.punctuation_vector) == 6
    assert len(features.activity_vector) == 2
