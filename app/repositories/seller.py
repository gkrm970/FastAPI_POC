from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.seller import Seller


def create(db: Session, seller: Seller) -> Seller:
    db.add(seller)
    db.commit()
    db.refresh(seller)
    return seller


def get_all(db: Session) -> list[Seller]:
    return list(db.scalars(select(Seller)).all())
