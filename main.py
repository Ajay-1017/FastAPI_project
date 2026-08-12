
from fastapi import FastAPI
import logging
from database import engine , Base 
import models
import logging_config

app = FastAPI()

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind = engine)

from routers import products , customers , orders , carts

app.include_router(products.router , prefix = '/api/products' , tags=["Products"])
app.include_router(customers.router , prefix = '/api/customers', tags =["Customers"])
app.include_router(orders.router , prefix = "/api/orders", tags=["Orders"])
app.include_router(carts.router, prefix="/api/customers", tags=["Carts"])

@app.get("/home")
@app.get("/")
def home():

    logger.info("Home endpoint was called")

    return {
        "message" : "Welocome to  ecommerce db !!"
    }


