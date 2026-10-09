"""Product business logic."""

from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate


class ProductService:
    """Coordinate product business operations."""

    def __init__(self, repository: ProductRepository) -> None:
        """Initialize the service with a product repository."""
        self.repository = repository

    def create_product(self, db: Session, data: ProductCreate) -> Product:
        """Create a new product in the database."""
        return self.repository.create(db, Product(**data.model_dump()))

    def update_product(self, db: Session, product: Product, data: ProductCreate) -> Product:
        """Update an existing product in the database."""
        return self.repository.update(db, product, data.name, data.description, data.price)
