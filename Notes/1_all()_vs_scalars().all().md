
# SQLAlchemy `result.all()` vs `result.scalars().all()`

## `result.all()`

Returns every row as a tuple (Row object).

Example:

```python
result = db.execute(select(Product))
print(result.all())
```

Output:

```python
[
    (<Product object>,),
    (<Product object>,)
]
```

Use when selecting **multiple columns**.

Example:

```python
select(Product.id, Product.product_name)
```

Output:

```python
[
    (1, "Mouse"),
    (2, "Keyboard")
]
```

---

## `result.scalars().all()`

Extracts the **first column** from every row.

Example:

```python
result = db.execute(select(Product))
products = result.scalars().all()
```

Output:

```python
[
    <Product object>,
    <Product object>
]
```

If selecting a single column:

```python
select(Product.product_name)
```

Output:

```python
[
    "Mouse",
    "Keyboard"
]
```

---

## Rule to Remember


| Query                                      | Method            |
| -------------------------------------------- | ------------------- |
| `select(Product)`                          | `scalars().all()` |
| `select(Product.product_name)`             | `scalars().all()` |
| `select(Product.id, Product.product_name)` | `all()`           |

---

## Mental Model

```
db.execute()
      │
      ▼
   Result Object
      │
      ├── all()
      │      ▼
      │   List of Rows (tuples)
      │
      └── scalars()
              ▼
      First column only
              ▼
           all()
              ▼
      One-dimensional list
```
