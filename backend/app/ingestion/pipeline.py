"""Parse, chunk, embed, and store an uploaded document."""

import uuid

import structlog

from app.db.models import Chunk, Document
from app.db.session import SessionLocal
from app.embeddings.factory import get_embedder
from app.ingestion.chunker import chunk_text
from app.storage.local import get_storage

logger = structlog.get_logger(__name__)


def ingest_document(document_id: uuid.UUID) -> None:
    """Run ingestion in a background task with its own database session."""
    with SessionLocal() as session:
        document = session.get(Document, document_id)
        if document is None:
            return

        document.status = "processing"
        document.error = None
        session.commit()

        try:
            raw = get_storage().read(document.storage_key)
            text = raw.decode("utf-8", errors="replace")
            chunks = chunk_text(text)
            if not chunks:
                raise ValueError("The document contains no readable text.")

            vectors = get_embedder().embed_documents(chunks)
            if len(vectors) != len(chunks):
                raise RuntimeError("The embedding provider returned the wrong count.")

            session.add_all(
                [
                    Chunk(
                        document_id=document.id,
                        index=index,
                        content=content,
                        token_count=max(1, len(content) // 4),
                        embedding=vector,
                    )
                    for index, (content, vector) in enumerate(zip(chunks, vectors, strict=True))
                ]
            )
            document.status = "ready"
            document.chunk_count = len(chunks)
            document.error = None
            session.commit()
            logger.info(
                "document_ingested",
                document_id=str(document.id),
                chunks=len(chunks),
            )
        except Exception as exc:
            session.rollback()
            document = session.get(Document, document_id)
            if document is not None:
                document.status = "failed"
                document.error = str(exc)[:500]
                session.commit()
            logger.exception("document_ingestion_failed", document_id=str(document_id))
