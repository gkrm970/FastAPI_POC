"""Application entry point and root health endpoint."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.routes import products, sellers
from app.core.telemetry import configure_telemetry
from app.db import base  # noqa: F401
from app.db.database import Base, engine
from app.middleware import register_middleware

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create database tables when the application starts."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

# Initialize FastAPI application
app = FastAPI(title="Product API", version="1.0.0", lifespan=lifespan)

# Configure telemetry for the application
configure_telemetry(app)

# Register CORS and request context middleware
register_middleware(app)

# Include routers for products and sellers
app.include_router(products.router)
app.include_router(sellers.router)

# Define a health check endpoint
@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return the current application health status."""
    return {"status": "ok"}
