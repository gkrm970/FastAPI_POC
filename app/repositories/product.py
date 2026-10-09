"""Product database access operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    """Encapsulate database operations for products."""

    async def create(self, db: AsyncSession, product: Product) -> Product:
        """Persist and return a product."""
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    async def get_all(self, db: AsyncSession) -> list[Product]:
        """Return all products."""
        result = await db.scalars(select(Product))
        return list(result.all())

    async def get_by_id(self, db: AsyncSession, product_id: int) -> Product | None:
        """Return a product by identifier."""
        return await db.get(Product, product_id)

    async def update(
        self,
        db: AsyncSession,
        product: Product,
        name: str,
        description: str,
        price: int,
    ) -> Product:
        """Update and return a product."""
        product.name = name
        product.description = description
        product.price = price
        await db.commit()
        await db.refresh(product)
        return product

    async def delete(self, db: AsyncSession, product: Product) -> None:
        """Delete a product."""
        await db.delete(product)
        await db.commit()
