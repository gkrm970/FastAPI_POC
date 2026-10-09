from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories import product as product_repository
from app.schemas.product import ProductCreate


def create_product(db: Session, data: ProductCreate) -> Product:
    return product_repository.create(db, Product(**data.model_dump()))


def update_product(db: Session, product: Product, data: ProductCreate) -> Product:
    return product_repository.update(db, product, data.name, data.description, data.price)
