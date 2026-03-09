from __future__ import annotations

import hashlib


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model = None

    def _lazy_load(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        except Exception:
            self._model = False

    def embed(self, text: str) -> list[float]:
        self._lazy_load()
        if self._model:
            return self._model.encode(text).tolist()

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [b / 255 for b in digest[:32]]
