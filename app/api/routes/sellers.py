"""Seller HTTP endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.seller import Seller
from app.repositories.seller import SellerRepository
from app.schemas.seller import SellerCreate, SellerResponse
from app.services.seller import SellerService

router = APIRouter(prefix="/sellers", tags=["Sellers"])
seller_repository = SellerRepository()
seller_service = SellerService(seller_repository)


@router.post("", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
def add_seller(data: SellerCreate, db: Session = Depends(get_db)) -> Seller:
    """Create a seller with a securely hashed password."""
    try:
        return seller_service.create_seller(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        ) from None


@router.get("", response_model=list[SellerResponse])
def list_sellers(db: Session = Depends(get_db)) -> list[Seller]:
    """Return all sellers without exposing their passwords."""
    return seller_repository.get_all(db)
