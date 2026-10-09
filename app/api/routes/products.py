"""Product HTTP endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

product_repository = ProductRepository()
product_service = ProductService(product_repository)


async def _get_product_or_404(db: AsyncSession, product_id: int) -> Product:
    product = await product_repository.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate, db: AsyncSession = Depends(get_db)
) -> Product:
    """Create and return a product."""
    return await product_service.create_product(db, data)


@router.get("", response_model=list[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)) -> list[Product]:
    """Return all products."""
    return await product_repository.get_all(db)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)) -> Product:
    """Return a product by its identifier."""
    return await _get_product_or_404(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> Product:
    """Update and return an existing product."""
    product = await _get_product_or_404(db, product_id)
    return await product_service.update_product(db, product, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a product and return an empty response."""
    product = await _get_product_or_404(db, product_id)
    await product_repository.delete(db, product)
