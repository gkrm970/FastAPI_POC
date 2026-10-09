from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories import seller as seller_repository
from app.schemas.seller import SellerCreate, SellerResponse
from app.services.seller import create_seller

router = APIRouter(prefix="/sellers", tags=["Sellers"])


@router.post("", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
def add_seller(data: SellerCreate, db: Session = Depends(get_db)):
    try:
        return create_seller(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        ) from None


@router.get("", response_model=list[SellerResponse])
def list_sellers(db: Session = Depends(get_db)):
    return seller_repository.get_all(db)
