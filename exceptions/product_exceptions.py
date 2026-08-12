
from fastapi import HTTPException,status
import models

class ProductAlreadyExistsError(Exception):
    pass

class ProductNotFoundError(Exception):

    def __init__(self,product_id: int):
        self.product_id = product_id

class ProductOutOfStockError(Exception):
    def __init__(self,product: models.Product):
        self.product = product



def product_name_exception():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= "Product already exists"
    )

def product_id_exception(product_id : int):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f"product id {product_id} not exists"
        )

def out_of_stock(product : models.Product):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.no_of_stocks} items available in stock."
        )