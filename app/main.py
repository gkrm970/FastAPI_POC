from fastapi import FastAPI

from app.api.routes import products, sellers
from app.db.database import Base, engine
from app.db import base  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product API", version="1.0.0")

app.include_router(products.router)
app.include_router(sellers.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok"}
