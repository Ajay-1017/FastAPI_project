# Pydantic Components

## BaseModel

```text
BaseModel
│
├── Defines the schema
├── Validates incoming data
├── Converts data to appropriate Python types
└── Creates Python model objects
```

### Purpose

- Defines the structure (schema) of your data.
- Validates input and output data.
- Automatically converts compatible data types.
- Creates Python objects that FastAPI can work with.

---

## Field

```text
Field
│
└── Adds validation rules
    ├── gt (greater than)
    ├── ge (greater than or equal)
    ├── lt (less than)
    ├── le (less than or equal)
    ├── min_length
    ├── max_length
    ├── pattern (regex)
    └── default values & metadata
```

### Purpose

- Adds validation constraints to individual fields.
- Provides extra metadata for documentation (Swagger).

---

## ConfigDict

```text
ConfigDict
│
└── Changes how Pydantic behaves
     │
     └── from_attributes=True
             │
             ├── Read object attributes
             │      user.name
             │      user.email
             │
             └── Instead of only dictionaries
                    user["name"]
                    user["email"]
```

### Purpose

- Configures the behavior of a Pydantic model.
- `from_attributes=True` allows Pydantic to create models directly from ORM objects (e.g., SQLAlchemy models).

---

## EmailStr

```text
EmailStr
│
└── Specialized data type
     │
     └── Validates email format
```

### Purpose

- Ensures that a value is a valid email address.
- Raises a validation error for invalid email formats.

---

# Quick Revision

| Component            | Purpose                                                                      |
| -------------------- | ---------------------------------------------------------------------------- |
| **BaseModel**  | Defines schema, validates data, converts types, creates Python model objects |
| **Field**      | Adds validation rules and metadata for individual fields                     |
| **ConfigDict** | Configures Pydantic behavior (e.g.,`from_attributes=True`)                 |
| **EmailStr**   | Validates that a value is a properly formatted email address                 |
