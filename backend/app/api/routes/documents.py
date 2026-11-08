"""Document upload and inspection."""

import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import ApiError
from app.core.config import get_settings
from app.db.models import Chunk, Document, User
from app.db.session import get_db
from app.ingestion.pipeline import ingest_document
from app.schemas.documents import ChunkRead, DocumentRead
from app.storage.local import get_storage

router = APIRouter()


def _suffix_for(content_type: str) -> str:
    return ".md" if content_type == "text/markdown" else ".txt"


@router.post("", response_model=DocumentRead, status_code=status.HTTP_202_ACCEPTED)
def upload_document(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Document:
    settings = get_settings()
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in settings.allowed_mime_types:
        raise ApiError(
            415,
            "unsupported_media_type",
            f"Unsupported file type. Allowed: {', '.join(settings.allowed_mime_types)}.",
        )

    limit = settings.max_upload_mb * 1024 * 1024
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise ApiError(
            413,
            "payload_too_large",
            f"Files must be at most {settings.max_upload_mb} MB.",
        )
    if not data:
        raise ApiError(400, "empty_file", "The uploaded file is empty.")

    storage_key = f"{uuid.uuid4().hex}{_suffix_for(content_type)}"
    get_storage().save(storage_key, data)

    safe_name = (file.filename or "document.txt").replace("\\", "/").rsplit("/", 1)[-1]
    document = Document(
        user_id=user.id,
        filename=(safe_name.strip() or "document.txt")[:255],
        content_type=content_type,
        size_bytes=len(data),
        storage_key=storage_key,
        status="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(ingest_document, document.id)
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[Document]:
    statement = (
        select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())
    )
    return list(db.scalars(statement))


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.user_id != user.id:
        raise ApiError(404, "document_not_found", "Document not found.")
    return document


@router.get("/{document_id}/chunks", response_model=list[ChunkRead])
def list_chunks(
    document_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[Chunk]:
    document = db.get(Document, document_id)
    if document is None or document.user_id != user.id:
        raise ApiError(404, "document_not_found", "Document not found.")

    statement = select(Chunk).where(Chunk.document_id == document.id).order_by(Chunk.index)
    return list(db.scalars(statement))


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    document = db.get(Document, document_id)
    if document is None or document.user_id != user.id:
        raise ApiError(404, "document_not_found", "Document not found.")

    storage_key = document.storage_key
    db.delete(document)
    db.commit()
    get_storage().delete(storage_key)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
