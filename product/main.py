from fastapi import FastAPI, status, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
import schemas
from models import ProductModel
from schemas import ProductSchema, SellerSchema
from typing import List
from database import Base, engine, get_db
from hashed_password import pwd_context

app = FastAPI()

# create the database tables defined in your models.s
Base.metadata.create_all(bind=engine)


@app.post('/product', status_code=status.HTTP_201_CREATED,tags =["Product"])
def add(request: ProductSchema, db: Session = Depends(get_db)):
    new_product = models.ProductModel(
        name=request.name,
        description=request.description,
        price=request.price
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.post('/seller', status_code=status.HTTP_201_CREATED,tags =["Seller"])
def create_seller(request: SellerSchema, db: Session = Depends(get_db)):
    # hashed_password = pwd_context.hash(request.password)
    new_seller = models.SellerModel(
        username=request.username,
        email=request.email,
        password=pwd_context.hash(request.password)  # hashed the password.
    )
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    return new_seller


# response_model= DisplayProduct --> response body formatted in own way.
# @app.get('/products', response_model=List[schemas.DisplayProduct],tags =["Product"])
@app.get('/products',tags =["Product"])
def products_get_all(db: Session = Depends(get_db)):
    products = db.query(models.ProductModel).all()
    return products


# # response_model= schemas.DisplayProduct --> response body formatted in own way.
@app.get('/products/{id}', response_model=schemas.DisplayProduct,tags =["Product"])
def product_get(id: int, db: Session = Depends(get_db)):
    product = db.query(models.ProductModel).filter(models.ProductModel.id == id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='PRODUCT NOT FOUND')

    else:
        return product


@app.delete('/products/{id}',tags =["Product"])
def product_delete(id: int, db: Session = Depends(get_db)):
    product = db.query(models.ProductModel).filter(models.ProductModel.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail='product not found')

    else:
        db.delete(product)
        db.commit()
        return {"product is deleted": product}


@app.put('/products/{id}',tags =["Product"])
def product(request: schemas.ProductSchema, id: int, db: Session = Depends(get_db)):
    product = db.query(models.ProductModel).filter(models.ProductModel.id == id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    else:
        ProductModel.name = request.name
        ProductModel.description = request.description
        ProductModel.price = request.price
        db.commit()

        # Re-query the database for the updated product
        updated_product = db.query(models.ProductModel).filter(models.ProductModel.id == id).first()

        return {"product is successfully updated": updated_product}


"""
@app.post('/product',status_code =200) or @app.post('/product',status_code=status.HTTP_201_CREATED)---> if at all wanted to mention expected status code explicitly the use this way.   
"""
