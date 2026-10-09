"""Seller business logic."""

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.seller import Seller
from app.repositories.seller import SellerRepository
from app.schemas.seller import SellerCreate


class SellerService:
    """Coordinate seller business operations."""

    def __init__(self, repository: SellerRepository) -> None:
        """Initialize the service with a seller repository."""
        self.repository = repository

    def create_seller(self, db: Session, data: SellerCreate) -> Seller:
        """Create a seller with a hashed password."""
        seller = Seller(
            username=data.username,
            email=str(data.email),
            password=hash_password(data.password),
        )
        return self.repository.create(db, seller)
