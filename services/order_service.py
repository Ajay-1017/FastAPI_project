from sqlalchemy import select
from sqlalchemy.orm import Session

import models

from exceptions.order_exceptions import (
    OrderNotFoundError
)


#====================================================================================================
# get all orders
#====================================================================================================

def get_orders(
    db: Session
):

    result = db.execute(
        select(models.Order)
    )

    orders = result.scalars().all()

    return orders


#====================================================================================================
# get order
#====================================================================================================

def get_order(
    db: Session,
    order_id: int
):

    result = db.execute(
        select(models.Order)
        .where(models.Order.id == order_id)
    )

    order = result.scalars().first()

    if not order:
        raise OrderNotFoundError(order_id)

    return order