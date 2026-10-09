from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.seller import Seller
from app.repositories import seller as seller_repository
from app.schemas.seller import SellerCreate


def create_seller(db: Session, data: SellerCreate) -> Seller:
    seller = Seller(
        username=data.username,
        email=data.email,
        password=hash_password(data.password),
    )
    return seller_repository.create(db, seller)
