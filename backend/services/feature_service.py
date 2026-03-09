from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
import re

EMOJI_PATTERN = re.compile("[\U0001F300-\U0001FAFF]")
PUNCTUATION = ",.!?;:"
STOPWORDS = {"the", "a", "an", "and", "or", "to", "of", "in", "is", "on", "for"}


@dataclass
class FeatureVectors:
    style_vector: list[float]
    emoji_vector: list[float]
    punctuation_vector: list[float]
    activity_vector: list[float]


class FeatureExtractor:
    def extract(self, texts: list[str], timestamps: list[datetime]) -> FeatureVectors:
        joined = " ".join(texts)
        avg_length = (sum(len(t) for t in texts) / len(texts)) if texts else 0.0
        tokens = [t.lower() for text in texts for t in text.split()]
        stopword_ratio = (sum(1 for t in tokens if t in STOPWORDS) / len(tokens)) if tokens else 0.0
        typo_ratio = (sum(1 for t in tokens if any(ch.isdigit() for ch in t)) / len(tokens)) if tokens else 0.0

        emoji_count = len(EMOJI_PATTERN.findall(joined))
        emoji_density = emoji_count / max(len(joined), 1)

        punct_counter = Counter(ch for ch in joined if ch in PUNCTUATION)
        punctuation_total = sum(punct_counter.values())
        punctuation_vector = [
            punct_counter.get(ch, 0) / max(punctuation_total, 1) for ch in PUNCTUATION
        ]

        hours = [ts.hour for ts in timestamps]
        active_hour_mean = (sum(hours) / len(hours)) if hours else 0.0
        burstiness = self._burstiness(timestamps)

        return FeatureVectors(
            style_vector=[avg_length, stopword_ratio, typo_ratio],
            emoji_vector=[emoji_count, emoji_density],
            punctuation_vector=punctuation_vector,
            activity_vector=[active_hour_mean, burstiness],
        )

    @staticmethod
    def _burstiness(timestamps: list[datetime]) -> float:
        if len(timestamps) < 2:
            return 0.0
        sorted_ts = sorted(timestamps)
        deltas = [
            (sorted_ts[idx] - sorted_ts[idx - 1]).total_seconds()
            for idx in range(1, len(sorted_ts))
        ]
        mean_delta = sum(deltas) / len(deltas)
        if mean_delta == 0:
            return 1.0
        under_minute = sum(1 for d in deltas if d <= 60)
        return under_minute / len(deltas)
