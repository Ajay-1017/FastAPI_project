from typing import Annotated


from datetime import UTC , datetime , timedelta

import jwt
from fastapi import Depends , HTTPException , status
from fastapi.security import OAuth2PasswordBearer 
from pwdlib import PasswordHash

from config import settings

from sqlalchemy import select  
from sqlalchemy.orm import Session 
from database import get_db
import models

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/customers/token")

def hash_password(password : str) -> str : 
    return password_hash.hash(password)


def verify_password(plain_password : str , hashed_password : str ) -> bool :
    return password_hash.verify(plain_password,hashed_password)

def create_access_token(data : dict , expires_delta : timedelta | None = None) -> str :

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )

    to_encode.update({"exp" : expire})

    encoded_jwt = jwt.encode(
        payload = to_encode,
        key = settings.secret_key.get_secret_value(),
        algorithm = settings.algorithm
    )

    return encoded_jwt

def verify_access_token(token : str) -> str | None :

    try :
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms = [settings.algorithm],
            options = {"require" : ["exp", "sub"]},
        )

    except jwt.InvalidTokenError:
        return None

    else:
        return payload.get("sub")



def get_current_customer(
    token : Annotated[str , Depends(oauth2_scheme)],
    db : Annotated[Session , Depends(get_db)]
) -> models.Customer :

    customer_id = verify_access_token(token)

    if customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        customer_id = int(customer_id)

    except (TypeError , ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = db.execute(
        select(models.Customer)
        .where(models.Customer.id == customer_id)
    )

    customer = result.scalars().first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return customer


CurrentCustomer = Annotated[models.Customer, Depends(get_current_customer)]
