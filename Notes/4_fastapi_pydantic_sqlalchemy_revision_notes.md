# FastAPI + Pydantic + SQLAlchemy — Short Revision Notes

## 1. API JSON Flow

### Request
`JSON → FastAPI → Pydantic → Python object → Router → SQLAlchemy → Database`

### Response
`Database → SQLAlchemy object → Pydantic → FastAPI → JSON → Client`

- JSON is the common input/output format of the HTTP API.
- Pydantic validates and shapes API data.
- FastAPI handles the HTTP request/response flow.

---

## 2. Pydantic Schemas

**Purpose:** Define and validate the data that crosses the API boundary.

### Request schema
Example:
```python
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int
```

Client JSON:
```json
{
  "product_id": 1,
  "quantity": 2
}
```

FastAPI/Pydantic gives the router a Python object:
```python
cart_item_create.product_id
cart_item_create.quantity
```

### Response schema
Example:
```python
class CartResponse(BaseModel):
    cart_id: int | None
    customer_id: int
    cart_items: list[CartItemResponse]
    total_amount: float
```

It defines the shape of the API response.

---

## 3. SQLAlchemy Models

**Purpose:** Represent database tables and relationships as Python classes/objects.

Example:
```python
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
```

Think:

`SQLAlchemy Model ↔ Database Table`

SQLAlchemy lets us work with the database using Python objects and expressions instead of writing raw SQL for every operation.

---

## 4. `mapped_column()`

`mapped_column()` describes a database column in a SQLAlchemy model.

Example:
```python
unit_price: Mapped[float] = mapped_column(Float, nullable=False)
```

- `Mapped[float]` → Python-side type annotation.
- `mapped_column(Float, ...)` → database column configuration.
- `primary_key=True` → primary key.
- `nullable=False` → `NULL` is not allowed.
- `unique=True` → values must be unique.

---

## 5. Model vs Schema

### SQLAlchemy Model
Answers:

> How is this data stored in the database?

### Pydantic Schema
Answers:

> What data should the API accept or return?

Example:

```text
Client JSON
    ↓
Pydantic Schema
    ↓
Router / Business Logic
    ↓
SQLAlchemy Model
    ↓
Database
```

Do not confuse them:

```python
db.add(models.Cart(...))     # Correct
db.add(CartCreate(...))      # Wrong
```

`CartCreate` is an API schema, not a database-mapped object.

---

## 6. `from_attributes=True`

Used when Pydantic needs to create a schema from an object such as a SQLAlchemy model.

```python
class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    unit_price: float
```

It allows Pydantic to read attributes like:

```python
product.id
product.name
product.unit_price
```

instead of expecting only dictionary data.

---

## 7. Nested Pydantic Schemas

Example:

```python
class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    unit_price: float


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: int
    product: ProductSummary
```

SQLAlchemy relationship:

```text
CartItem
   ↓
product → Product
```

API response:

```text
CartItemResponse
   ↓
product → ProductSummary
```

`ProductSummary` is a smaller API representation of a Product.

It can expose only:
- `id`
- `name`
- `unit_price`

instead of the full Product fields.

### Important
Schema field names should match the attributes available on the SQLAlchemy object when using `from_attributes=True`.

For example:

```python
product: ProductSummary
```

matches:

```python
cart_item.product
```

---

## 8. SQLAlchemy Relationships

Think in terms of cardinality:

```text
Customer 1 ─── 1 Cart
Cart     1 ─── many CartItems
Product  1 ─── many CartItems

Customer 1 ─── many Orders
Order    1 ─── many OrderItems
Product  1 ─── many OrderItems
```

`unique=True` should only be used when the relationship requires a value to appear only once.

Example:

```python
Cart.customer_id = unique=True
```

because one customer has one cart.

But:

```python
CartItem.cart_id
```

should not be unique because one cart can contain many cart items.

---

## 9. Cart Business Logic

### Add Cart Item — POST

POST means:

> Add this product/quantity to the cart.

If product already exists:

```text
existing quantity + incoming quantity
```

If it doesn't exist:

```text
create CartItem
```

Typical flow:

```text
Validate Customer
→ Validate Product
→ Validate Stock
→ Get/Create Cart
→ Find CartItem
→ Update or Create CartItem
→ Calculate Total
→ Commit
→ Return Cart
```

### PATCH

PATCH means:

> Change the existing quantity to a specific value.

Example:

```text
Current quantity = 5
PATCH quantity = 2
Result = 2
```

This is different from POST, where adding `2` could mean:

```text
5 + 2 = 7
```

### DELETE

Typical flow:

```text
Validate Customer
→ Validate Cart
→ Validate CartItem
→ Delete Item
→ Recalculate Total
→ Commit
→ Return/finish
```

---

## 10. `commit()`, `flush()`, `refresh()`

### `db.commit()`
Saves the transaction to the database.

### `db.flush()`
Sends pending SQL to the database without committing the whole transaction.

Useful when you need a generated ID before committing.

### `db.refresh(obj)`
Reloads the object from the database.

---

## 11. Common Errors We Debugged

### `UnmappedInstanceError`

Usually means you passed a Pydantic schema to a SQLAlchemy operation.

Wrong:
```python
db.add(CartCreate(...))
```

Correct:
```python
db.add(models.Cart(...))
```

---

### `NOT NULL constraint failed`

A required database column received `None`.

Example:
```text
Cart.total_amount = NULL
```

while the model has:
```python
nullable=False
```

---

### `UNIQUE constraint failed`

The database has a unique constraint and you attempted to insert a duplicate value.

Important: changing `models.py` does not automatically modify an existing SQLite table.

---

### `no such column`

Your SQLAlchemy model contains a column that the existing database table doesn't have.

For a learning SQLite project, deleting/recreating the database can reset the schema.

For real projects, use database migrations such as Alembic.

---

### Pydantic `Field required`

Your response data does not contain a field required by the response schema.

Always compare:

```text
What the schema requires
        VS
What your endpoint returns
```

---

## 12. Best Mental Model

Remember these four lines:

> **Pydantic = API data validation and shape**

> **SQLAlchemy = Python interface to the database**

> **Router = application/business logic**

> **FastAPI = connects HTTP requests/responses with your application**

---

## 13. Deep Learning Rule

Don't focus on framework internals yet.

Focus on being able to answer:

1. What data comes into my API?
2. Which Pydantic schema validates it?
3. What business logic should happen?
4. Which SQLAlchemy models/tables are involved?
5. What should be saved?
6. What should the API return?
7. Which response schema defines that output?
