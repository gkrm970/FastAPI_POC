from app.core.security import hash_password, pwd_context
from app.repositories.seller import SellerRepository
from app.schemas.seller import SellerCreate
from app.services.seller import SellerService


class TestSellerService:
    """Test seller business operations with async database access."""

    def setup_method(self) -> None:
        """Create the repository and service under test."""
        self.repository = SellerRepository()
        self.service = SellerService(self.repository)

    async def test_create_seller_hashes_password(self, db_session) -> None:
        """Create a seller without storing the plain-text password."""
        data = SellerCreate(
            username="alice",
            email="alice@example.com",
            password="strong-pass-123",
        )

        seller = await self.service.create_seller(db_session, data)

        assert seller.password != data.password
        assert pwd_context.verify(data.password, seller.password)
        assert await self.repository.get_all(db_session) == [seller]

    def test_password_hash_can_be_verified(self) -> None:
        """Verify that password hashing and verification work."""
        password = "strong-pass-123"

        assert pwd_context.verify(password, hash_password(password))
