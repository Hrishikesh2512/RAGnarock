"""Cosine-similarity retrieval over a user's chunks."""

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.embeddings.factory import get_embedder


@dataclass
class RetrievedChunk:
    chunk: Chunk
    document: Document
    score: float


def retrieve(
    session: Session,
    user_id: uuid.UUID,
    query: str,
    top_k: int | None = None,
    min_score: float | None = None,
) -> list[RetrievedChunk]:
    settings = get_settings()
    limit = top_k or settings.retrieval_top_k
    threshold = settings.retrieval_min_score if min_score is None else min_score
    vector = get_embedder().embed_query(query)

    distance = Chunk.embedding.cosine_distance(vector)
    statement = (
        select(Chunk, Document, distance.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .where(
            Document.user_id == user_id,
            Document.status == "ready",
            distance <= 1.0 - threshold,
        )
        .order_by(distance)
        .limit(limit)
    )

    return [
        RetrievedChunk(chunk=chunk, document=document, score=1.0 - float(row_distance))
        for chunk, document, row_distance in session.execute(statement)
    ]
