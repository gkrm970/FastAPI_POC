"""Product HTTP endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product
from app.repositories import product as product_repository
from app.schemas.product import ProductCreate, ProductResponse
from app.services import product as product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db)) -> Product:
    """Create and return a product."""
    return product_service.create_product(db, data)


@router.get("", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    """Return all products."""
    return product_repository.get_all(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    """Return a product by its identifier."""
    product = product_repository.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
) -> Product:
    """Update and return an existing product."""
    product = product_repository.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product_service.update_product(db, product, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a product and return an empty response."""
    product = product_repository.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product_repository.delete(db, product)
