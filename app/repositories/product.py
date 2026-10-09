"""Product database access operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    """Encapsulate database operations for products."""

    def create(self, db: Session, product: Product) -> Product:
        """Persist and return a product."""
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def get_all(self, db: Session) -> list[Product]:
        """Return all products."""
        return list(db.scalars(select(Product)).all())

    def get_by_id(self, db: Session, product_id: int) -> Product | None:
        """Return a product by identifier."""
        return db.get(Product, product_id)

    def update(
        self,
        db: Session,
        product: Product,
        name: str,
        description: str,
        price: int,
    ) -> Product:
        """Update and return a product."""
        product.name = name
        product.description = description
        product.price = price
        db.commit()
        db.refresh(product)
        return product

    def delete(self, db: Session, product: Product) -> None:
        """Delete a product."""
        db.delete(product)
        db.commit()
