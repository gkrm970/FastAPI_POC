from sqlalchemy import Column, Integer, String
from database import Base


class ProductModel(Base):
    __tablename__ = 'product'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    name = Column(String(length=250))
    description = Column(String(length=250))
    price = Column(Integer)


class SellerModel(Base):
    __tablename__ = 'seller'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    username = Column(String(length=250))
    email = Column(String(length=250))
    password = Column(String(length=250))
