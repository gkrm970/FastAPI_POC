from app.core.security import hash_password, pwd_context
from app.repositories.seller import SellerRepository
from app.schemas.seller import SellerCreate
from app.services.seller import SellerService


def test_create_seller_hashes_password(db_session):
    repository = SellerRepository()
    service = SellerService(repository)
    data = SellerCreate(
        username="alice",
        email="alice@example.com",
        password="strong-pass-123",
    )

    seller = service.create_seller(db_session, data)

    assert seller.password != data.password
    assert pwd_context.verify(data.password, seller.password)
    assert repository.get_all(db_session) == [seller]


def test_password_hash_can_be_verified():
    password = "strong-pass-123"

    assert pwd_context.verify(password, hash_password(password))
