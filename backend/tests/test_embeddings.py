import math

from app.embeddings.fake import FakeEmbedder


def test_fake_embeddings_are_deterministic_and_normalized() -> None:
    embedder = FakeEmbedder(384)

    first = embedder.embed_query("hello world")
    second = embedder.embed_documents(["hello world"])[0]

    assert first == second
    assert len(first) == 384
    assert math.isclose(math.sqrt(sum(value * value for value in first)), 1.0, rel_tol=1e-6)


def test_different_text_produces_different_vectors() -> None:
    embedder = FakeEmbedder(384)

    assert embedder.embed_query("alpha") != embedder.embed_query("beta")


def test_shared_words_are_more_similar() -> None:
    embedder = FakeEmbedder(384)
    query = embedder.embed_query("which project avoids Redis")
    related = embedder.embed_query("the project deliberately avoids Redis and Celery")
    unrelated = embedder.embed_query("completely different vocabulary here")

    related_score = sum(a * b for a, b in zip(query, related, strict=True))
    unrelated_score = sum(a * b for a, b in zip(query, unrelated, strict=True))

    assert related_score > unrelated_score
