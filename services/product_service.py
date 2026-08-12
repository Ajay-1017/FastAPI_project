
from sqlalchemy import select
from sqlalchemy.orm import Session

from exceptions.product_exceptions import (
    ProductAlreadyExistsError,
    ProductNotFoundError
)

from schemas import ProductCreate,ProductUpdate

import models


#====================================================================================================
# create product 
#====================================================================================================

def create_product(
    db: Session,
    product_create : ProductCreate
):
    result = db.execute(
        select(models.Product).where(models.Product.name == product_create.name)
    )

    product = result.scalars().first()

    if product: # check if the product is already exist or not
        raise ProductAlreadyExistsError()

    new_product = models.Product(
        name = product_create.name,
        category = product_create.category,
        unit_price = product_create.unit_price,
        no_of_stocks = product_create.no_of_stocks

    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)


    return new_product




#====================================================================================================
# get products
#====================================================================================================

def get_products(
        db : Session
):
    result = db.execute(select(models.Product))
    products = result.scalars().all()

    return products


#====================================================================================================
# get product 
#====================================================================================================

def get_product(
        db : Session,
        product_id : int
):
    
    result = db.execute(
        select(models.Product).where(models.Product.id  == product_id)
    )

    product = result.scalars().first() 

    if not product:
        raise ProductNotFoundError(product_id)

    return product

#====================================================================================================
# update product 
#====================================================================================================

def update_product(
        db : Session,
        user_update : ProductUpdate,
        product : models.Product
):
    
    if user_update.name is not None and product.name!= user_update.name :

        result = db.execute(
            select(models.Product).where(models.Product.name == user_update.name)
        )

        existing_product = result.scalars().first()

        if existing_product:
            raise ProductAlreadyExistsError()
            
    update_product = user_update.model_dump(exclude_unset=True)

    for field , value in update_product.items():
        setattr(product , field , value)


    db.commit()
    db.refresh(product)

    return product
    

#====================================================================================================
# delete product 
#====================================================================================================

def delete_product(
    db : Session,
    product_id : int
):
    result = db.execute(
            select(models.Product).where(models.Product.id  == product_id)
        )
    
    product = result.scalars().first()

    if not product:
        raise ProductNotFoundError(product_id)
        
    db.delete(product)
    db.commit()

    return product