"""Local CPU embeddings using BAAI/bge-small-en-v1.5."""

import threading

from app.embeddings.base import EmbeddingProvider


class LocalEmbedder(EmbeddingProvider):
    """Lazy, thread-safe wrapper around a sentence-transformers model."""

    def __init__(self, model_name: str, dimension: int, batch_size: int) -> None:
        from sentence_transformers import SentenceTransformer

        self.dimension = dimension
        self._batch_size = batch_size
        self._lock = threading.Lock()
        self._model = SentenceTransformer(model_name, device="cpu")

        dimension_getter = getattr(self._model, "get_embedding_dimension", None)
        actual = (
            dimension_getter()
            if dimension_getter is not None
            else self._model.get_sentence_embedding_dimension()
        )
        if actual != dimension:
            raise RuntimeError(f"EMBEDDING_DIM={dimension} does not match {model_name} ({actual}).")

    def _encode(self, texts: list[str]) -> list[list[float]]:
        with self._lock:
            vectors = self._model.encode(
                texts,
                batch_size=self._batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        return [vector.tolist() for vector in vectors]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._encode([text])[0]
