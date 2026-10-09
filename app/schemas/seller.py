from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SellerCreate(BaseModel):
    username: str = Field(min_length=1, max_length=250)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SellerResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
