from typing import Annotated

import logging
import logging_config

from fastapi import (
    APIRouter,
    status, 
    Depends, 
)


from sqlalchemy.orm import Session
from schemas import (
    ProductCreate, 
    ProductResponse,
    ProductUpdate
)

from exceptions import product_exceptions
from exceptions.product_exceptions import (
    ProductAlreadyExistsError,
    ProductNotFoundError 
)

from services import product_service


from database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

#====================================================================================================
# create product 
#====================================================================================================

@router.post("" , response_model = ProductResponse ,  status_code= status.HTTP_201_CREATED)
def create_product(product_create : ProductCreate , db : Annotated[Session , Depends(get_db)]):

    try :
        new_product = product_service.create_product(db,product_create)

    except ProductAlreadyExistsError:
        logger.warning("Product creation rejected : Product %s already exists", product_create.name)
        product_exceptions.product_name_exception()

    logger.info(
    "Product '%s' successfully created",
    new_product.name
    )

    return new_product



#====================================================================================================
# get products
#====================================================================================================

@router.get("" , response_model= list[ProductResponse])
def get_products(db : Annotated[Session , Depends(get_db)]):

    products = product_service.get_products(db)
    return products


#====================================================================================================
# get product 
#====================================================================================================

@router.get("/{product_id}" , response_model=ProductResponse)
def get_product(product_id : int , db : Annotated[Session , Depends(get_db)]):

    try:
        product = product_service.get_product(db,product_id)

    except ProductNotFoundError as exc:
        logger.warning(" Get Product rejected : Product id: %s not exists ", product_id )
        product_exceptions.product_id_exception(exc.product_id)

    return product


#====================================================================================================
# update product 
#====================================================================================================

@router.patch("/{product_id}" , response_model=ProductResponse)
def update_product(product_update : ProductUpdate, product_id : int , db : Annotated[Session , Depends(get_db)]):

    try:
        product = product_service.get_product(db,product_id)

    except ProductNotFoundError as exc:
        logger.warning("Product updation rejected : Product id: %s not exists ", product_id )
        product_exceptions.product_id_exception(exc.product_id)

    try:  
        updated_product = product_service.update_product(db,product_update,product)

    except ProductAlreadyExistsError:
        logger.warning(" Product updation rejected : Product %s already exists", product_update.name)
        product_exceptions.product_name_exception()

    logger.info(
    "Product '%s' successfully updated",
    product_update.name
    )
    
    return updated_product

#====================================================================================================
# delete product 
#====================================================================================================

@router.delete("/{product_id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id : int , db : Annotated[Session , Depends(get_db)]):

    try :
        product = product_service.delete_product(db,product_id)

    except ProductNotFoundError as exc:
        logger.warning("Product deletion rejected : Product id: %s not exists ", product_id )
        product_exceptions.product_id_exception(exc.product_id)

    logger.info(
    "Product '%s' successfully deleted",
    product.name
    )
    