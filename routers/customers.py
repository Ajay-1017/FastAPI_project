from typing import Annotated    

from database import get_db 
from fastapi import (
    APIRouter,
    status,
    Depends
)

from sqlalchemy.orm import Session 
from fastapi.security import OAuth2PasswordRequestForm

from schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerPublic,
    CustomerPrivate,
    Token,
    OrderResponse
)

from auth import (
    CurrentCustomer
    )

from services import customer_service


from exceptions import (
    customer_exceptions, 
)

from exceptions.customer_exceptions import(
    EmailAlreadyExistError,
    CustomerNotFound
)



router = APIRouter()



#====================================================================================================
# create customer
#====================================================================================================

@router.post("",response_model = CustomerPrivate ,status_code = status.HTTP_201_CREATED)
def create_customer(customer_create : CustomerCreate , db : Annotated[Session , Depends(get_db)]):

    try:
        customer = customer_service.create_customer(db,customer_create)

    except EmailAlreadyExistError:
        customer_exceptions.email_already_exists(customer_create.email)

    return customer

#====================================================================================================
# create  access_token
#====================================================================================================

@router.post("/token",response_model=Token)
def login_for_access_token(
        form_data : Annotated[OAuth2PasswordRequestForm , Depends()],
        db : Annotated[Session ,Depends(get_db) ]
):
    token = customer_service.login_for_access_token(db,form_data)

    if token is None:
        customer_exceptions.incorrect_email_or_password()

    return token

#====================================================================================================
# get customer
#====================================================================================================

@router.get("/me",response_model=CustomerPrivate)
def get_current_customer(current_customer : CurrentCustomer):
    return current_customer

#====================================================================================================
# get customers
#====================================================================================================


@router.get("",response_model=list[CustomerPublic])
def get_customers(db : Annotated[Session , Depends(get_db)]):
    return customer_service.get_customers(db)

#====================================================================================================
# get customer
#====================================================================================================

@router.get("/{customer_id}" , response_model=CustomerPublic)
def get_customer( customer_id : int ,  db : Annotated[Session , Depends(get_db)]):

    try:
        customer = customer_service.get_customer(db,customer_id)

    except CustomerNotFound:
        customer_exceptions.customer_not_found(customer_id)

    return customer

#====================================================================================================
# update customer
#====================================================================================================


@router.patch("/{customer_id}" , response_model=CustomerPrivate)
def update_customer( 
    customer_id : int , 
    customer_update : CustomerUpdate , 
    current_customer : CurrentCustomer,
    db : Annotated[Session , Depends(get_db)]
):
    if customer_id != current_customer.id:
            customer_exceptions.customer_not_authorized(
                not_authorized_to = "update"
                )
    try : 
        updated_customer = customer_service.update_customer(
            db ,
            customer_update,
            current_customer
        )

    except EmailAlreadyExistError: 
        customer_exceptions.email_already_exists(customer_update.email)

    return updated_customer

#====================================================================================================
# get customer orders
#====================================================================================================

@router.get("/{customer_id}/orders" , response_model=list[OrderResponse])
def get_customer_orders(
    customer_id : int , 
    current_customer : CurrentCustomer, 
    db : Annotated[Session , Depends(get_db)]
):
    if customer_id != current_customer.id:
            customer_exceptions.customer_not_authorized(
                not_authorized_to = "get orders from"
                )
    try :   
        orders = customer_service.get_customer_orders(db , customer_id)

    except CustomerNotFound:
        customer_exceptions.customer_not_found(customer_id)
        
    return orders

#====================================================================================================
# delete customer
#====================================================================================================

@router.delete("/{customer_id}" ,status_code= status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id : int, 
    current_customer : CurrentCustomer,
    db : Annotated[Session , Depends(get_db)]
):
    if customer_id != current_customer.id:
            customer_exceptions.customer_not_authorized(
                not_authorized_to = "delete"
                )
    try:
        deleted_customer = customer_service.delete_customer(db , customer_id)

    except CustomerNotFound:
        customer_exceptions.customer_not_found(customer_id)

    return deleted_customer