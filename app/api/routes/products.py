"""Product HTTP endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


class ProductController:
    """Handle HTTP operations for products."""

    def __init__(self, repository: ProductRepository, service: ProductService) -> None:
        self.repository = repository
        self.service = service

    async def create_product(
        self, data: ProductCreate, db: AsyncSession = Depends(get_db)
    ) -> Product:
        """Create and return a product."""
        return await self.service.create_product(db, data)

    async def list_products(self, db: AsyncSession = Depends(get_db)) -> list[Product]:
        """Return all products."""
        return await self.repository.get_all(db)

    async def get_product(
        self, product_id: int, db: AsyncSession = Depends(get_db)
    ) -> Product:
        """Return a product by its identifier."""
        return await self._get_product_or_404(db, product_id)

    async def update_product(
        self,
        product_id: int,
        data: ProductCreate,
        db: AsyncSession = Depends(get_db),
    ) -> Product:
        """Update and return an existing product."""
        product = await self._get_product_or_404(db, product_id)
        return await self.service.update_product(db, product, data)

    async def delete_product(
        self, product_id: int, db: AsyncSession = Depends(get_db)
    ) -> None:
        """Delete a product and return an empty response."""
        product = await self._get_product_or_404(db, product_id)
        await self.repository.delete(db, product)

    async def _get_product_or_404(
        self, db: AsyncSession, product_id: int
    ) -> Product:
        product = await self.repository.get_by_id(db, product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return product


product_repository = ProductRepository()
product_controller = ProductController(
    repository=product_repository,
    service=ProductService(product_repository),
)

router.add_api_route(
    "",
    product_controller.create_product,
    methods=["POST"],
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "",
    product_controller.list_products,
    methods=["GET"],
    response_model=list[ProductResponse],
)
router.add_api_route(
    "/{product_id}",
    product_controller.get_product,
    methods=["GET"],
    response_model=ProductResponse,
)
router.add_api_route(
    "/{product_id}",
    product_controller.update_product,
    methods=["PUT"],
    response_model=ProductResponse,
)
router.add_api_route(
    "/{product_id}",
    product_controller.delete_product,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
)
