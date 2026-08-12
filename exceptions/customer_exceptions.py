

from fastapi import HTTPException , status


class EmailAlreadyExistError(Exception):
    pass

class CustomerNotFound(Exception):
    pass


def email_already_exists(email : str):
    raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = f"{email} : This email id already exist"
        )

def incorrect_email_or_password():
    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = " incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"}
    )

def customer_not_found(customer_id : int):
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f"Customer with  id : {customer_id} not found"
        )

def customer_not_authorized(not_authorized_to : str):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = f"Not authorized to {not_authorized_to} this user"
        )
    