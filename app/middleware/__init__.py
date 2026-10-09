"""Application middleware registration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.middleware.request_context import RequestContextMiddleware


def register_middleware(app: FastAPI) -> None:
    """Register middleware; the last one added runs first."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials="*" not in settings.cors_allow_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            RequestContextMiddleware.request_id_header,
            RequestContextMiddleware.process_time_header,
        ],
    )
    app.add_middleware(RequestContextMiddleware)
