"""Seller database access operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.seller import Seller


class SellerRepository:
    """Encapsulate database operations for sellers."""

    def create(self, db: Session, seller: Seller) -> Seller:
        """Persist and return a seller."""
        db.add(seller)
        db.commit()
        db.refresh(seller)
        return seller

    def get_all(self, db: Session) -> list[Seller]:
        """Return all sellers."""
        return list(db.scalars(select(Seller)).all())
