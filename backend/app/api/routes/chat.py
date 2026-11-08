"""Grounded question answering over the user's documents."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.llm.factory import get_llm_provider
from app.rag.prompt import build_prompt
from app.rag.retriever import retrieve
from app.schemas.chat import ChatRequest, ChatResponse, Citation

router = APIRouter()

NO_CONTEXT_ANSWER = (
    "I could not find anything relevant in your documents. "
    "Try uploading a document or rephrasing the question."
)


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    provider_key: Annotated[str | None, Header(alias="X-Provider-Key")] = None,
) -> ChatResponse:
    chunks = retrieve(db, user.id, payload.question, payload.top_k)
    if not chunks:
        return ChatResponse(answer=NO_CONTEXT_ANSWER, citations=[])

    prompt = build_prompt(payload.question, chunks)
    answer = get_llm_provider().generate(prompt, api_key=provider_key or None)

    citations = [
        Citation(
            document_id=result.document.id,
            filename=result.document.filename,
            chunk_id=result.chunk.id,
            chunk_index=result.chunk.index,
            score=round(result.score, 4),
            snippet=result.chunk.content.strip()[:320],
        )
        for result in chunks
    ]
    return ChatResponse(answer=answer, citations=citations)
