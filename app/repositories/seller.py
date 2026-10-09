"""Seller database access operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seller import Seller


class SellerRepository:
    """Encapsulate database operations for sellers."""

    async def create(self, db: AsyncSession, seller: Seller) -> Seller:
        """Persist and return a seller."""
        db.add(seller)
        await db.commit()
        await db.refresh(seller)
        return seller

    async def get_all(self, db: AsyncSession) -> list[Seller]:
        """Return all sellers."""
        result = await db.scalars(select(Seller))
        return list(result.all())
