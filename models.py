from __future__ import annotations
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import Integer , String , DateTime ,Float , ForeignKey

from database import Base
from datetime import UTC , datetime 

# concepts :

# ForeignKey
#       │
#       ▼
# Creates the connection
# inside the database.

# relationship()
#       │
#       ▼
# Uses that connection
# to navigate between
# Python objects.



#=========================================================================================================
# Products Table
#=========================================================================================================

class Product(Base):

    __tablename__ = "products"

    id : Mapped[int] = mapped_column(Integer, primary_key=True , index=True)

    name : Mapped[str] = mapped_column(String, unique=True , nullable=False)

    category  : Mapped[str] = mapped_column(String, nullable=False )   
    
    unit_price : Mapped[float] = mapped_column(Float, nullable=False)

    no_of_stocks : Mapped[int] = mapped_column(Integer, nullable=False) 

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone= True) , default=lambda : datetime.now(UTC))

#-----------------------------------------------------------------------------------------------------------
# one -> many relationship
#-----------------------------------------------------------------------------------------------------------
    
    # one product -> many order items
    order_items: Mapped[list[OrderItem]] = relationship(
        back_populates="product"
    )

    # one -> many relationship
    # (one product -> many order items)
    cart_items : Mapped[list[CartItem]]  = relationship(
         back_populates="product"
    )
#=========================================================================================================
# Customers Table
#=========================================================================================================
class Customer(Base): 
    
    __tablename__ = "customers"

    id : Mapped[int] = mapped_column(Integer, primary_key=True , index = True)

    name : Mapped[str] = mapped_column(String(50), nullable=False)

    email : Mapped[str] = mapped_column(String(120), unique=True , nullable=False)

    password_hash : Mapped[str] = mapped_column(String(200), nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default= lambda : datetime.now(UTC))


#-----------------------------------------------------------------------------------------------------------
# one -> many relationship 
#-----------------------------------------------------------------------------------------------------------
    
    # one customer -> many orders
    orders : Mapped[list[Order]] = relationship(
        back_populates= "customer"
    )
#-----------------------------------------------------------------------------------------------------------
# one -> one relationship 
#-----------------------------------------------------------------------------------------------------------
    # one customer -> one cart
    cart : Mapped[Cart | None] = relationship(
        back_populates="customer"
    )

#=========================================================================================================
# Orders Table
#=========================================================================================================

class Order(Base): 
    __tablename__ = "orders"

    id : Mapped[int] = mapped_column(Integer , primary_key=True )

    # The "many" side stores the foreign key of the "one" side.
    customer_id : Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index = True
        )
    
    total_amount : Mapped[float] = mapped_column(Float , nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default= lambda : datetime.now(UTC))

#-----------------------------------------------------------------------------------------------------------
# many -> one relationship 
#-----------------------------------------------------------------------------------------------------------
    
    # many orders -> one customer
    customer : Mapped[Customer] = relationship(
        back_populates= "orders"
    )

#-----------------------------------------------------------------------------------------------------------
# one -> many relationship 
#-----------------------------------------------------------------------------------------------------------
    
   # one order -> many order_items
    order_items: Mapped[list[OrderItem]] = relationship(
        back_populates="order"
    )

#=========================================================================================================
# OrderItem Table
#=========================================================================================================


class OrderItem(Base):

    __tablename__ = "order_items"

    id : Mapped[int] = mapped_column(Integer , primary_key=True )

    order_id : Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index = True
    )

    product_id : Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index = True
    )

    quantity : Mapped[int] = mapped_column(Integer , nullable=False)

    unit_price : Mapped[float] = mapped_column(Float , nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default= lambda : datetime.now(UTC))


#-----------------------------------------------------------------------------------------------------------
# many -> one relationship
#-----------------------------------------------------------------------------------------------------------
    
    # many -> one relationship (Many order_items -> one order)
    order : Mapped[Order] = relationship(
        back_populates="order_items"
    )

    # many -> one relationship (Many order_items -> one product)
    product : Mapped[Product] = relationship(
        back_populates="order_items"
    )


#=========================================================================================================
# Carts Table
#=========================================================================================================

class Cart(Base):
    __tablename__ = "carts"

    id : Mapped[int] = mapped_column(Integer , primary_key=True )

    customer_id : Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        unique=True,
        index = True
    )

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) , default= lambda : datetime.now(UTC))

#-----------------------------------------------------------------------------------------------------------
# one -> one relationship 
#-----------------------------------------------------------------------------------------------------------
    # one cart -> one customer
    customer : Mapped[Customer] = relationship(
        back_populates= "cart"
    )
#-----------------------------------------------------------------------------------------------------------
# one -> many relationship 
#-----------------------------------------------------------------------------------------------------------
    # one cart -> many cartItems
    cart_items: Mapped[list[CartItem]] = relationship(
        back_populates="cart"
    )

class CartItem(Base):

    __tablename__ = "cart_items"

    id : Mapped[int] = mapped_column(Integer , primary_key=True )

    cart_id : Mapped[int] = mapped_column(
        ForeignKey("carts.id"),
        nullable=False,
        index = True
    )

    product_id : Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index = True
    )

    quantity : Mapped[int] = mapped_column(Integer , nullable=False)

#-----------------------------------------------------------------------------------------------------------
# many -> one relationship
#-----------------------------------------------------------------------------------------------------------
    
    # many -> one relationship (Many cart_items -> one cart)
    cart : Mapped[Cart] = relationship(
        back_populates="cart_items"
    )

    # many -> one relationship (Many cart_items -> one product)
    product : Mapped[Product] = relationship(
        back_populates="cart_items"
    )
