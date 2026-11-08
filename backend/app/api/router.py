"""Aggregated router for application endpoints.

Feature routers (documents, chat, search, ...) are included here with the
``/api`` prefix. Root-level probes live in ``app.api.routes.health``.
"""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api")
