import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app, lifespan


@pytest.fixture
async def client():
    async with lifespan(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac


async def test_health_check(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_product_not_found(client: AsyncClient):
    response = await client.get("/products/999999")
    assert response.status_code == 404


async def test_create_and_get_product(client: AsyncClient):
    payload = {"name": "Widget", "description": "A test widget", "price": 10}
    created = await client.post("/products", json=payload)
    assert created.status_code == 201
    product_id = created.json()["id"]

    fetched = await client.get(f"/products/{product_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Widget"

    deleted = await client.delete(f"/products/{product_id}")
    assert deleted.status_code == 204
