from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=250)
    description: str = Field(min_length=1, max_length=250)
    price: int = Field(ge=0)


class ProductResponse(ProductCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
