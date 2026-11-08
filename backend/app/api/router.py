"""Aggregated router for application endpoints.

Feature routers are included here with the ``/api`` prefix. Root-level probes
live in ``app.api.routes.health``.
"""

from fastapi import APIRouter

from app.api.routes import auth, chat, documents, search

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(chat.router, tags=["chat"])
