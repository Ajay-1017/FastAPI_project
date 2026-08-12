
from fastapi import HTTPException,status


class CartNotFoundError(Exception):
    pass

class CartItemNotFoundError(Exception):
    pass

def cart_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f"cart not exists"
        )

def cart_item_not_found( cart_item_id : int):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f"cartItem id : {cart_item_id} not exists"
        )
