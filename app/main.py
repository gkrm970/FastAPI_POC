"""Application entry point and root health endpoint."""

from fastapi import FastAPI

from app.api.routes import products, sellers
from app.core.telemetry import configure_telemetry
from app.db import base  # noqa: F401
from app.db.database import Base, engine

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(title="Product API", version="1.0.0")

# Configure telemetry for the application
configure_telemetry(app)

# Include routers for products and sellers
app.include_router(products.router)
app.include_router(sellers.router)

# Define a health check endpoint
@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return the current application health status."""
    return {"status": "ok"}
