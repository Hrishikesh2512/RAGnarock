"""Retrieval without generation, for the inspector and debugging."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.rag.retriever import retrieve
from app.schemas.chat import SearchRequest, SearchResponse, SearchResult

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(
    payload: SearchRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> SearchResponse:
    chunks = retrieve(db, user.id, payload.query, payload.top_k)
    return SearchResponse(
        query=payload.query,
        results=[
            SearchResult(
                document_id=result.document.id,
                filename=result.document.filename,
                chunk_id=result.chunk.id,
                chunk_index=result.chunk.index,
                score=round(result.score, 4),
                content=result.chunk.content,
            )
            for result in chunks
        ],
    )
