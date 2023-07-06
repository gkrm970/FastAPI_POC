# from product.model import Product
from pydantic import BaseModel, validator


class ProductSchema(BaseModel):
    name: str
    description: str
    price: int


# this class will be used when the requirements like selected field should be present in response, then you should
# use this class.
class DisplayProduct(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class SellerSchema(BaseModel):
    username: str
    email: str
    password: str


# this class will be used when the requirements like selected field should be present in response, then you should
# use this class.
class DisplaySeller(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True
