"""Deterministic token-hash embeddings.

They are not semantically meaningful, but shared words produce shared
dimensions, so retrieval and citation tests work without downloading a model.
"""

import hashlib
import math
import re


class FakeEmbedder:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = re.findall(r"[a-z0-9]+", text.lower())

        for token in tokens:
            # A tiny stemmer keeps "avoid" and "avoids" in the same bucket.
            if len(token) > 3 and token.endswith("s"):
                token = token[:-1]
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:8], "big") % self.dimension
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            vector[0] = 1.0
            return vector
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)
