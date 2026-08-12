
class ProductNotExistsError(Exception):
    pass


def product_exist_or_not(id):
    if id == 1:
        raise ProductNotExistsError()
    else:
        print("product exist")

product_exist_or_not(1)
