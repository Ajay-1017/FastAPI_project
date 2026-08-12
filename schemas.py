# Pydantic sits at the boundary of your application.

# Incoming data → Pydantic validates it.
# Outgoing data → Pydantic formats and validates it before sending it back.

from pydantic import (
    BaseModel,     # Defines a schema and validates input/output data.
    Field,         # Adds validation rules and metadata for model fields.
    ConfigDict,    # Configures Pydantic model behavior (e.g., from_attributes=True allows creating models from object attributes instead of only dictionaries).
    EmailStr       # Validates that a field contains a valid email address.
)

from datetime import datetime 

#=======================================================================================
# products table I/O Schema
#=======================================================================================
class ProductBase(BaseModel):
    name : str = Field(min_length=1 , max_length=50)
    category : str = Field(min_length=1 , max_length=50)
    unit_price : float = Field(gt = 0)
    no_of_stocks : int = Field(ge = 0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name : str | None = Field(default=None, min_length=1 , max_length=50)
    category : str | None = Field(default=None,min_length=1 , max_length=50)
    unit_price : float | None = Field(default=None , gt=0)
    no_of_stocks : int | None = Field(default=None , ge=0 )

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id : int
    created_at : datetime

class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    unit_price: float

#=======================================================================================
# customers table I/O Schema
#=======================================================================================
class CustomerBase(BaseModel):
    name : str = Field(min_length=1 , max_length=50)
    email : EmailStr = Field(max_length = 120)

class CustomerCreate(CustomerBase):
    password : str = Field(min_length=8)

class CustomerUpdate(BaseModel):
    name : str | None = Field( default=None , min_length=1 , max_length=50)
    email : EmailStr | None = Field(default= None , max_length = 120)

class Token(BaseModel):
    access_token : str
    token_type : str

class CustomerPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    name : str

class CustomerPrivate(CustomerPublic):
    email : EmailStr


#=======================================================================================
# Orders table I/O Schema
#=======================================================================================

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product: ProductSummary
    quantity: int
    unit_price: float

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id : int
    total_amount: float
    created_at: datetime

    order_items: list[OrderItemResponse]


#=======================================================================================
# cart table I/O Schema
#=======================================================================================


class CartItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity : int =  Field(gt=0)

class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product: ProductSummary
    quantity : int
    
class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)
    
class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int | None
    customer_id : int
    cart_items : list[CartItemResponse]
    total_amount: float