from fastapi import HTTPException, status


class OrderNotFoundError(Exception):

    def __init__(self, order_id: int):
        self.order_id = order_id


def order_not_found(order_id: int):

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Order with id : {order_id} not found"
    )