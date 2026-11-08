"""Liveness and build-information endpoints.

These live at the site root rather than under ``/api`` so that container
healthchecks and the edge proxy can reach them without authentication.
"""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__
from app.core.config import get_settings

router = APIRouter(tags=["meta"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


class VersionResponse(BaseModel):
    name: str
    version: str
    environment: str


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/version", response_model=VersionResponse, summary="Build information")
def version() -> VersionResponse:
    settings = get_settings()
    return VersionResponse(
        name=settings.app_name,
        version=__version__,
        environment=settings.app_env,
    )
