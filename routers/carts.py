from typing import Annotated
from database import get_db 
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends
)
from sqlalchemy import select , func
from sqlalchemy.orm import Session 

from schemas import (
    CartResponse,
    CartItemCreate,
    CartItemUpdate,
    OrderResponse

)

from exceptions.product_exceptions import (
    ProductNotFoundError,
    ProductOutOfStockError
)
from exceptions.cart_exceptions import (
    CartNotFoundError,
    CartItemNotFoundError
)
from exceptions import cart_exceptions

import models

router = APIRouter()

from auth import CurrentCustomer

from exceptions import customer_exceptions , product_exceptions

from services import cart_service

#----------------------------------------------------------------------------------------------
# Create Cart 
#----------------------------------------------------------------------------------------------

# Validate Customer
#         │
#         ▼
# Validate Product
#         │
#         ▼
# Does Cart Exist?
#         │
#    ┌────┴────┐
#    │         │
#   No        Yes
#    │         │
# Create Cart  │
#    │         ▼
#    │   Does Product Already Exist?
#    │         │
#    │    ┌────┴────┐
#    │    │         │
#    │   No        Yes
#    │    │         │
#    │ Create    Calculate
#    │ CartItem  Final Quantity
#    │              │
#    │              ▼
#    │     Final Quantity <= Stock?
#    │         │
#    │    ┌────┴────┐
#    │    │         │
#    │   No        Yes
#    │    │         │
#    │  Reject   Update Quantity
#    │
#    └───────────────┐
#                    ▼
#           Return Updated Cart

#====================================================================================================
# create cart
#====================================================================================================

@router.post("/{customer_id}/cart/items", response_model=CartResponse)
def create_cart(
    db: Annotated[Session, Depends(get_db)],
    cart_item_create: CartItemCreate,
    customer_id: int,
    current_customer : CurrentCustomer,
    
):
    
    if customer_id != current_customer.id:
        customer_exceptions.customer_not_authorized(
            not_authorized_to="create cart item for"
        )    

    try :
        cart = cart_service.create_cart(
                        db,
                        cart_item_create,
                        current_customer
                    )

    except ProductNotFoundError as exc:
        product_exceptions.product_name_exception(exc.product_id)

    except ProductOutOfStockError as exc:
        product_exceptions.out_of_stock(exc.product)

    return cart


#====================================================================================================
# get Cart items
#====================================================================================================

@router.get("/{customer_id}/cart", response_model=CartResponse)
def get_cart_items(
    db: Annotated[Session, Depends(get_db)],
    customer_id: int,
    current_customer : CurrentCustomer
): 

    if customer_id != current_customer.id:
            customer_exceptions.customer_not_authorized(
                not_authorized_to="get cart item from"
            )  
    cart = cart_service.get_cart_items(
                        db,
                        current_customer
                    )
    return cart


#====================================================================================================
# update cartItem
#====================================================================================================
       

@router.patch("/{customer_id}/cart/items/{cart_item_id}" ,response_model = CartResponse)
def cart_update(
    db: Annotated[Session, Depends(get_db)],
    customer_id: int,
    cart_item_update : CartItemUpdate,
    cart_item_id : int ,
    current_customer : CurrentCustomer,
):

    if customer_id != current_customer.id:
        customer_exceptions.customer_not_authorized(
            not_authorized_to="update"
        )
    try :
        updated_cart = cart_service.cart_update(
            db,
            cart_item_update,
            cart_item_id,
            current_customer
        )

    except CartNotFoundError:
        cart_exceptions.cart_not_found()

    except CartItemNotFoundError:
        cart_exceptions.cart_item_not_found(cart_item_id)

    except ProductOutOfStockError as exc:
        product_exceptions.out_of_stock(exc.product)

    return updated_cart


#====================================================================================================
# delete cartItem
#====================================================================================================

@router.delete("/{customer_id}/cart/items/{cart_item_id}", response_model=CartResponse)
def delete_cart_item(
    customer_id: int,
    cart_item_id: int,
    current_customer : CurrentCustomer,
    db: Annotated[Session, Depends(get_db)]
):

    if customer_id != current_customer.id:
        customer_exceptions.customer_not_authorized(
            not_authorized_to="delete"
        )

    try :
        deleted_cart_item = cart_service.delete_cart_item(
            db,
            cart_item_id,
            current_customer
        )

    except CartNotFoundError:
        cart_exceptions.cart_not_found()

    except CartItemNotFoundError:
        cart_exceptions.cart_item_not_found(cart_item_id)

    return deleted_cart_item


#====================================================================================================
# checkout
#====================================================================================================

@router.post(
    "/{customer_id}/cart/checkout",
    response_model=OrderResponse
)
def checkout(
    customer_id: int,
    current_customer: CurrentCustomer,
    db: Annotated[Session, Depends(get_db)]
):

    # --------------------------------------------------
    # Authorization
    # --------------------------------------------------

    if customer_id != current_customer.id:
        customer_exceptions.customer_not_authorized(
            not_authorized_to="checkout"
        )

    # --------------------------------------------------
    # Business logic
    # --------------------------------------------------

    try:

        order = cart_service.checkout(
            db,
            current_customer
        )

    except CartNotFoundError:
        cart_exceptions.cart_not_found()

    except ProductOutOfStockError as exc:
        product_exceptions.out_of_stock(exc.product)

    return order

