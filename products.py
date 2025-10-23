from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select

app = FastAPI()

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    price: float
    in_stock: bool

def validate_price(product : Product):
    if product.price < 0:
        raise HTTPException(status_code=400, detail="Цена товара не может быть меньше 0")
    return product

engine = create_engine("sqlite:///products.db")
SQLModel.metadata.create_all(engine)

@app.post("/products", tags=["Добавить"], summary="Добавить продукт")
def add_product(product : Product = Depends(validate_price)):
    with Session(engine) as s:
        s.add(product)
        s.commit()
        s.refresh(product)
        return {"message" : f"Товар '{product.name}' успешно добавлен"}

@app.put("/products/{product_id}", tags=["Изменить"], summary="Изменить по id")
def change_by_id(product_id : int, updated : Product = Depends(validate_price)):
    with Session(engine) as s:
        product = s.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Продукт с id: '{product_id}' не найден")
        
        product.name = updated.name
        product.price = updated.price
        product.in_stock = updated.in_stock

        s.add(product)
        s.commit()
        s.refresh(product)

        return {"message" : f"Товар '{product.name}' успешно изменен"}

@app.delete("/products/{product_id}", tags=["Удалить"], summary="Удалить по id")
def delete_by_id(product_id : int):
    with Session(engine) as s:
        product = s.get(Product, product_id)
        if not product:
             raise HTTPException(status_code=404, detail=f"Продукт с id: '{product_id}' не найден")
        
        s.delete(product)
        s.commit()

        return {"message" : "Продукт успешно удален"}
