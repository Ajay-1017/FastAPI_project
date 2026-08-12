
# SQLAlchemy Relationship Flow (Focus on `back_populates`)

```text
================================================================================
STEP 1 : DATABASE CONNECTION
================================================================================

customers table                    orders table

+-------------+                   +----------------------+
| id (PK)     |◄──────────────┐   | id (PK)              |
| name        |               │   | customer_id (FK)     |
| email       |               │   | total_amount         |
+-------------+               │   +----------------------+
                              │
                              │
                  ForeignKey("customers.id")
                              │
                              ▼

ForeignKey creates ONLY the DATABASE connection.

================================================================================
STEP 2 : SQLALCHEMY BUILDS PYTHON OBJECTS
================================================================================

Customer Object

Customer
│
├── id
├── name
└── orders   (relationship)


Order Object

Order
│
├── id
├── customer_id
└── customer   (relationship)

relationship() creates Python attributes.

================================================================================
CASE 1 : WITHOUT back_populates
================================================================================

Customer.orders                 Order.customer

      │                               │
      │                               │
      ▼                               ▼

Relationship A                 Relationship B

These are TWO DIFFERENT relationship objects.

SQLAlchemy DOES NOT know they represent
the same relationship.

---------------------------------------------------

Python Memory

customer = Customer()

order = Order()

Memory

Customer
│
└── orders
      │
      ▼
      []

Order
│
└── customer
      │
      ▼
     None

---------------------------------------------------

Now execute

customer.orders.append(order)

Memory becomes

Customer
│
└── orders
      │
      ▼
     [Order]

Order
│
└── customer
      │
      ▼
     None

WHY?

Because SQLAlchemy updated ONLY

Customer.orders

It does NOT know that

Order.customer

should also change.

---------------------------------------------------

Now execute

order.customer = customer

Memory becomes

Customer
│
└── orders
      │
      ▼
      []

Order
│
└── customer
      │
      ▼
   Customer

Again

Customer.orders

did NOT change.

Both sides are independent.

================================================================================
CASE 2 : WITH back_populates
================================================================================

class Customer

orders = relationship(
    back_populates="customer"
)

----------------------------

class Order

customer = relationship(
    back_populates="orders"
)

Now SQLAlchemy sees

Customer.orders

        ▲
        │
        │ SAME RELATIONSHIP
        ▼

Order.customer

These two attributes are now linked together.

================================================================================
PYTHON MEMORY
================================================================================

customer = Customer()

order = Order()

Memory

Customer
│
└── orders
      │
      ▼
      []

Order
│
└── customer
      │
      ▼
     None

---------------------------------------------------

Execute

customer.orders.append(order)

Immediately SQLAlchemy internally performs

customer.orders.append(order)

AND

order.customer = customer

Memory becomes

Customer
│
└── orders
      │
      ▼
     [Order]
        │
        │
        ▼

Order
│
└── customer
      │
      ▼
   Customer

Both sides are synchronized.

================================================================================

Now execute

order.customer = customer

Immediately SQLAlchemy internally performs

order.customer = customer

AND

customer.orders.append(order)

Memory becomes

Customer
│
└── orders
      │
      ▼
     [Order]
        ▲
        │
        │
Order.customer
      │
      ▼
   Customer

Again

Both sides are synchronized.

================================================================================
WHEN db.commit() HAPPENS
================================================================================

Python Memory

Customer
│
└── orders
      │
      ▼
     [Order]
        │
        ▼
Order.customer
      │
      ▼
Customer

            │
            │
            ▼

SQLAlchemy writes ONLY ONE THING
to the database

orders.customer_id = customer.id

The database NEVER stores

customer.orders

It only stores

orders.customer_id

================================================================================
MENTAL MODEL
================================================================================

                DATABASE

ForeignKey
     │
     ▼
Creates the road between tables.

--------------------------------------------

                PYTHON

relationship()
     │
     ▼
Creates navigation attributes.

customer.orders

order.customer

--------------------------------------------

back_populates
     │
     ▼
Connects BOTH relationship attributes.

Without it

Customer.orders    ❌──────❌    Order.customer

Independent

With it

Customer.orders    ◄──────►    Order.customer

One relationship

Update one side
        │
        ▼
Other side updates automatically.

================================================================================
ONE-LINE INTERVIEW ANSWER
================================================================================

ForeignKey creates the relationship in the database.

relationship() lets Python navigate that relationship.

back_populates tells SQLAlchemy that both relationship
attributes represent the SAME relationship, so whenever
one side changes in Python memory, the other side is
automatically synchronized before the data is written
to the database.
```
