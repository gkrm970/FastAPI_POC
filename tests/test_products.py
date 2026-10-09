import pytest

from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate
from app.services.product import ProductService


class TestProductService:
    """Test product business operations with async database access."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Create the repository and service under test."""
        self.repository = ProductRepository()
        self.service = ProductService(self.repository)

    async def test_create_and_get_product(self, db_session) -> None:
        """Create a product and retrieve it by identifier."""
        data = ProductCreate(name="Laptop", description="Business laptop", price=1200)

        created = await self.service.create_product(db_session, data)

        assert created.id is not None
        assert created.name == "Laptop"
        assert await self.repository.get_by_id(db_session, created.id) == created

    async def test_update_and_delete_product(self, db_session) -> None:
        """Update and delete a product."""
        created = await self.repository.create(
            db_session,
            Product(name="Keyboard", description="USB keyboard", price=25),
        )
        updated_data = ProductCreate(
            name="Keyboard",
            description="Wireless keyboard",
            price=30,
        )

        updated = await self.service.update_product(db_session, created, updated_data)
        assert updated.description == "Wireless keyboard"
        assert updated.price == 30

        await self.repository.delete(db_session, updated)
        assert await self.repository.get_by_id(db_session, updated.id) is None
