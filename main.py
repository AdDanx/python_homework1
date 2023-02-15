import uvicorn
import datetime
from datetime import datetime, date, time
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  Column, Integer, String, VARCHAR, Table, ForeignKey, Float, DATETIME
from sqlalchemy.orm import relationship, backref
from fastapi import FastAPI
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from databases import Database

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
database = Database('sqlite:///./sql_app.db')

Base = declarative_base()

app = FastAPI()

if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, host='127.0.0.1')
    
class item(Base):
    __tablename__ = "item"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR)
    price = Column(Integer)
    
class store(Base):
    __tablename__ = "store"
 
    id = Column(Integer, primary_key=True, index=True)
    address = Column(VARCHAR)
    
class sales(Base):
    __tablename__ = "sales"
 
    id = Column(Integer, primary_key=True, index=True)
    sale_time = Column(DATETIME)
    item_id = Column(Integer, ForeignKey('item.id'))
    store_id = Column(Integer, ForeignKey('store.id'))
    
    
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

## Заполнение базы какими-то данными
Iphone1 = item(name = "Iphone 13", price =100000)
Iphone2 = item(name = "Iphone 14", price =150000)

Store1 = store(address = "г. Городов ул. Улочная д. 1")
Store2 = store(address = "г. Айфонов ул. Яблочная д. 1")

db.add_all([Iphone1,Iphone2, Store1, Store2])
db.commit()

Sales_add = sales(item_id = 1, store_id = 1, sale_time=datetime.now())
db.add(Sales_add)
db.commit()
#### Конец заполнения базы

@app.get("/items/")
async def get_item(db: Session = Depends(get_db)):
    return db.query(item).all()

@app.get("/stores/")
async def get_stpre(db: Session = Depends(get_db)):
    return db.query(store).all()


@app.get("/stores/top")
async def get_store_top():
    await database.connect()
    data = await database.fetch_all("SELECT DISTINCT sales.store_id, store.address, sum(item.price) AS 'Total cash' FROM sales, store JOIN item ON item.id == sales.item_id WHERE sales.sale_time BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') GROUP BY store_id ORDER BY sum(item.price) DESC LIMIT 10")
    return data

@app.get("/items/top")
async def get_item_top():
    await database.connect()
    data = await database.fetch_all("SELECT DISTINCT count(sales.item_id) AS 'Total sales', item.name, item.price, sum(price) AS 'Total cash' FROM sales JOIN item ON item.id == sales.item_id GROUP BY item_id ORDER BY count(sales.item_id) DESC LIMIT 10")
    return data

@app.post("/sales/")
async def create_sales(data = Body(), db: Session = Depends(get_db)):
    sales_add = sales(item_id=data["item_id"], store_id=data["store_id"], sale_time=datetime.now())
    items_id = db.query(item).filter(item.id == data["item_id"]).first()
    store_id = db.query(store).filter(store.id == data["store_id"]).first()
    if (items_id==None and store_id==None):  
        return JSONResponse(status_code=404, content={ "message": "Item  and Store Not found"})      
    if items_id==None:  
        return JSONResponse(status_code=404, content={ "message": "Item  Not found"})  
    if store_id==None:  
        return JSONResponse(status_code=404, content={ "message": "Store  Not found"})      
    db.add(sales_add)
    db.commit()
    db.refresh(sales_add)
    return sales_add