
try :

except Exception:
    

class ProductAlreadyExistsError(Exception):
    pass


def product_Exist(stg):
    if stg == "exist":
        raise ProductAlreadyExistsError
    else:
        print("product created")
product_Exist("exist")