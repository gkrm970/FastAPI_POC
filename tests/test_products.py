from app.models.product import Product
from app.repositories import product as product_repository
from app.schemas.product import ProductCreate
from app.services import product as product_service


def test_create_and_get_product(db_session):
    data = ProductCreate(name="Laptop", description="Business laptop", price=1200)

    created = product_service.create_product(db_session, data)

    assert created.id is not None
    assert created.name == "Laptop"
    assert product_repository.get_by_id(db_session, created.id) == created


def test_update_and_delete_product(db_session):
    created = product_repository.create(
        db_session,
        Product(name="Keyboard", description="USB keyboard", price=25),
    )
    updated_data = ProductCreate(
        name="Keyboard",
        description="Wireless keyboard",
        price=30,
    )

    updated = product_service.update_product(db_session, created, updated_data)
    assert updated.description == "Wireless keyboard"
    assert updated.price == 30

    product_repository.delete(db_session, updated)
    assert product_repository.get_by_id(db_session, updated.id) is None
