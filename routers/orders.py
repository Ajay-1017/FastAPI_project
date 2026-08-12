from typing import Annotated

from database import get_db

from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from schemas import OrderResponse

from services import order_service

from exceptions import order_exceptions

from exceptions.order_exceptions import (
    OrderNotFoundError
)


router = APIRouter()


#====================================================================================================
# get all orders
#====================================================================================================

@router.get(
    "",
    response_model=list[OrderResponse]
)
def get_orders(
    db: Annotated[Session, Depends(get_db)]
):

    return order_service.get_orders(db)


#====================================================================================================
# get order
#====================================================================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,
    db: Annotated[Session, Depends(get_db)]
):

    try:

        order = order_service.get_order(
            db,
            order_id
        )

    except OrderNotFoundError as exc:

        order_exceptions.order_not_found(
            exc.order_id
        )

    return order