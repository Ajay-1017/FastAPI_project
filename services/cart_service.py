
from schemas import CartItemCreate , CartItemUpdate
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from auth import CurrentCustomer


from exceptions.cart_exceptions import (
    CartNotFoundError,
    CartItemNotFoundError
)
from exceptions.product_exceptions import (
    ProductNotFoundError,
    ProductOutOfStockError
)
from schemas import CartResponse 

import models


#====================================================================================================
# create cart
#====================================================================================================
def create_cart(
    db: Session,
    cart_item_create: CartItemCreate,
    current_customer : CurrentCustomer,
):
    # Validate Product
    result = db.execute(
        select(models.Product).where(
            models.Product.id == cart_item_create.product_id
        )
    )

    product = result.scalars().first()

    if not product:
        raise ProductNotFoundError(cart_item_create.product_id)

    # Validate Requested Quantity
    if cart_item_create.quantity > product.no_of_stocks:
        raise ProductOutOfStockError(product)


    # Get Existing Cart or Create One
    if current_customer.cart is None:

        cart = models.Cart(
            customer_id=current_customer.id
        )

        db.add(cart)
        db.flush()     # Generates cart.id

    else:
        cart = current_customer.cart

    # Check whether product already exists in cart
    result = db.execute(
        select(models.CartItem).where(
            models.CartItem.cart_id == cart.id,
            models.CartItem.product_id == cart_item_create.product_id
        )
    )

    cart_item = result.scalars().first()

    # Product already exists
    if cart_item:

        new_quantity = cart_item.quantity + cart_item_create.quantity

        if new_quantity > product.no_of_stocks:
            raise ProductOutOfStockError(product)
        cart_item.quantity = new_quantity

    # New product
    else:
        cart_item = models.CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity = cart_item_create.quantity
        )

        db.add(cart_item)

    # Save all changes
    db.commit()

    # Reload latest cart with relationships
    db.refresh(cart)

    # Calculate cart total
    total_amount = sum(
        item.product.unit_price * item.quantity
        for item in cart.cart_items
    )

    # Return response
    cart =  CartResponse(
        id=cart.id,
        customer_id=cart.customer_id,
        cart_items=cart.cart_items,
        total_amount=total_amount
    )

    return cart

#====================================================================================================
# get Cart items
#====================================================================================================

def get_cart_items(
    db : Session,
    current_customer : CurrentCustomer,
    
): 

    cart = current_customer.cart

    if cart is None :
        return CartResponse(
        id=None,
        customer_id=current_customer.id,
        cart_items=[],
        total_amount=0
    )

    # Calculate cart total
    total_amount = sum(
        item.product.unit_price * item.quantity
        for item in cart.cart_items
    )

    # Return response
    cart =  CartResponse(
        id=cart.id,
        customer_id=cart.customer_id,
        cart_items=cart.cart_items,
        total_amount=total_amount
    )

    return cart

#====================================================================================================
# update cart
#====================================================================================================
       
def cart_update(
    db: Session,
    cart_item_update : CartItemUpdate,
    cart_item_id : int ,
    current_customer : CurrentCustomer,
):  
    
    cart = current_customer.cart
    
    if cart is None :
        raise CartNotFoundError()

    result = db.execute(
        select(models.CartItem)
        .where(models.CartItem.id == cart_item_id,
                models.CartItem.cart_id == cart.id
                )
    )

    cart_item = result.scalars().first()

    if not cart_item:
        raise CartItemNotFoundError()
    
    product = cart_item.product

    if cart_item_update.quantity > product.no_of_stocks:
        raise ProductOutOfStockError(product)

    cart_item.quantity = cart_item_update.quantity

    db.commit()
    db.refresh(cart)    


    # Calculate cart total
    total_amount = sum(
            item.product.unit_price * item.quantity
            for item in cart.cart_items
        )

    # Return response
    cart =  CartResponse(
        id=cart.id,
        customer_id=cart.customer_id,
        cart_items=cart.cart_items,
        total_amount=total_amount
    )

    return cart



#====================================================================================================
# delete cartItem
#====================================================================================================

def delete_cart_item(
    db: Session,
    cart_item_id: int,
    current_customer : CurrentCustomer,
    
):

    # Validate Cart
    cart = current_customer.cart

    if cart is None:
        raise CartNotFoundError()

    # Validate Cart Item
    result = db.execute(
        select(models.CartItem).where(
            models.CartItem.id == cart_item_id,
            models.CartItem.cart_id == cart.id
        )
    )

    cart_item = result.scalars().first()

    if not cart_item:
        raise CartItemNotFoundError()

    # Delete Cart Item
    db.delete(cart_item)
    db.commit()
    db.refresh(cart)

    # Calculate Cart Total
    total_amount = sum(
        item.product.unit_price * item.quantity
        for item in cart.cart_items
    )

    # Return Updated Cart
    return CartResponse(
        id=cart.id,
        customer_id=cart.customer_id,
        cart_items=cart.cart_items,
        total_amount=total_amount
    )

#====================================================================================================
# checkout
#====================================================================================================

def checkout(
    db: Session,
    current_customer: CurrentCustomer,
):
    
    # --------------------------------------------------
    # 1. Validate Cart
    # --------------------------------------------------

    cart = current_customer.cart

    if cart is None:
        raise CartNotFoundError()

    # --------------------------------------------------
    # 2. Validate Cart is not empty
    # --------------------------------------------------

    if not cart.cart_items:
        raise CartNotFoundError()

    # --------------------------------------------------
    # 3. Validate stock for ALL products first
    # --------------------------------------------------

    for cart_item in cart.cart_items:

        product = cart_item.product

        if cart_item.quantity > product.no_of_stocks:
            raise ProductOutOfStockError(product)

    # --------------------------------------------------
    # 4. Calculate total
    # --------------------------------------------------

    total_amount = sum(
        cart_item.quantity * cart_item.product.unit_price
        for cart_item in cart.cart_items
    )

    # --------------------------------------------------
    # 5. Create Order
    # --------------------------------------------------

    order = models.Order(
        customer_id=current_customer.id,
        total_amount=total_amount
    )

    db.add(order)

    # Generate order.id
    db.flush()

    # --------------------------------------------------
    # 6. Create OrderItems + Update Stock
    # --------------------------------------------------

    for cart_item in cart.cart_items:

        product = cart_item.product

        order_item = models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            unit_price=product.unit_price
        )

        db.add(order_item)

        # Reduce product stock
        product.no_of_stocks -= cart_item.quantity

    # --------------------------------------------------
    # 7. Remove all CartItems
    # --------------------------------------------------

    for cart_item in list(cart.cart_items):
        db.delete(cart_item)

    # --------------------------------------------------
    # 8. Commit everything together
    # --------------------------------------------------

    db.commit()

    # --------------------------------------------------
    # 9. Reload order
    # --------------------------------------------------

    db.refresh(order)

    return order

