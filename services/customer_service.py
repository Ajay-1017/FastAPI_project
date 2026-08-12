from config import settings
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

from schemas import CustomerCreate , Token ,  CustomerUpdate
from sqlalchemy import select ,func
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    hash_password,
    verify_password,
    CurrentCustomer
)

from exceptions.customer_exceptions import(
    EmailAlreadyExistError,
    CustomerNotFound
)


import models

#====================================================================================================
# create customer
#====================================================================================================

def create_customer(
        db : Session,
        customer_create : CustomerCreate,
):  
    result = db.execute(
        select(models.Customer)
        .where(func.lower(models.Customer.email) == customer_create.email.lower())
    )

    existing_email  = result.scalars().first()

    if existing_email:
        raise  EmailAlreadyExistError()

    new_customer = models.Customer(
        name = customer_create.name,
        email = customer_create.email.lower(),
        password_hash = hash_password(customer_create.password)
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer

#====================================================================================================
# create  access_token
#====================================================================================================

def login_for_access_token(
        db : Session,
        form_data : OAuth2PasswordRequestForm,       
):
    result = db.execute(
            select(models.Customer)
            .where(func.lower(models.Customer.email) == form_data.username.lower())
        )
    
    customer  = result.scalars().first()
    
    if not customer or not verify_password(form_data.password , customer.password_hash):
        return None

    access_token_expires = timedelta(minutes = settings.access_token_expire_minutes)

    access_token = create_access_token(
        data = {"sub" : str(customer.id)},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")



#====================================================================================================
# get customers
#====================================================================================================

def get_customers(
        db : Session , 
):

    result = db.execute(
        select(models.Customer)
    )

    customers = result.scalars().all()
    
    return customers


#====================================================================================================
# get customer
#====================================================================================================

def get_customer(
        db : Session,
        customer_id : int
):
    
    result = db.execute(
        select(models.Customer).where( models.Customer.id == customer_id )
    )

    customer = result.scalars().first()

    if not customer:
        raise CustomerNotFound()

    return customer


#====================================================================================================
# update customer
#====================================================================================================

def update_customer(
        db : Session,
        customer_update : CustomerUpdate , 
        current_customer : CurrentCustomer,
):
    
    if customer_update.email is not None  and  customer_update.email.lower()!= current_customer.email.lower():

        result = db.execute(
        select(models.Customer)
        .where(func.lower(models.Customer.email) == customer_update.email.lower() )
    )

        existing_email = result.scalars().first()

        if existing_email:
            raise EmailAlreadyExistError()

    update_customer = customer_update.model_dump(exclude_unset=True)

    for field , value in update_customer.items():
        if field == "email":
            value : str = value.lower()
        setattr(current_customer , field, value )

    db.commit()
    db.refresh(current_customer)

    return current_customer

#====================================================================================================
# get customer orders
#====================================================================================================

def get_customer_orders(
        db : Session,
        customer_id : int
):
    result = db.execute(
            select(models.Customer).where( models.Customer.id == customer_id )
        )
    
    customer = result.scalars().first()

    if not customer:
        raise CustomerNotFound()

    return customer.orders


#====================================================================================================
# delete customer
#====================================================================================================

def delete_customer(
        db : Session,
        customer_id : int

):
    result = db.execute(
                select(models.Customer).where( models.Customer.id == customer_id )
            )
        
    customer = result.scalars().first()
    
    if not customer:
        raise CustomerNotFound()

    # --------------------------------------------------
    # Delete customer's cart
    # --------------------------------------------------

    if customer.cart is not None:

        cart = customer.cart

        # Delete all cart items first
        for cart_item in cart.cart_items:
            db.delete(cart_item)

        # Delete cart
        db.delete(cart)


    db.delete(customer)
    db.commit()

    return customer
  