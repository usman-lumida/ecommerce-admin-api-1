from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uvicorn

# Database setup
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/ecommerce"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(Float, nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)

# Pydantic Models
class ProductCreate(BaseModel):
    name: str
    category_id: int
    price: float

class SaleResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    sale_date: datetime
    total_amount: float

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    last_updated: datetime

class RevenueResponse(BaseModel):
    period: str
    total_revenue: float

# FastAPI App
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.post("/products/", response_model=ProductCreate)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, category_id=product.category_id, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return product

@app.get("/sales/", response_model=List[SaleResponse])
def get_sales(start_date: Optional[str] = None, end_date: Optional[str] = None, product_id: Optional[int] = None, category_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Sale)
    if start_date:
        query = query.filter(Sale.sale_date >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        query = query.filter(Sale.sale_date <= datetime.strptime(end_date, "%Y-%m-%d"))
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if category_id:
        query = query.join(Product).filter(Product.category_id == category_id)
    return query.all()

@app.get("/revenue/{period}")
def get_revenue(period: str, db: Session = Depends(get_db)):
    from sqlalchemy.sql import func
    if period not in ["daily", "weekly", "monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid period")
    if period == "daily":
        result = db.query(func.date(Sale.sale_date).label("period"), func.sum(Sale.total_amount).label("total_revenue")).group_by(func.date(Sale.sale_date)).all()
    elif period == "weekly":
        result = db.query(func.week(Sale.sale_date).label("period"), func.sum(Sale.total_amount).label("total_revenue")).group_by(func.week(Sale.sale_date)).all()
    elif period == "monthly":
        result = db.query(func.month(Sale.sale_date).label("period"), func.sum(Sale.total_amount).label("total_revenue")).group_by(func.month(Sale.sale_date)).all()
    else:
        result = db.query(func.year(Sale.sale_date).label("period"), func.sum(Sale.total_amount).label("total_revenue")).group_by(func.year(Sale.sale_date)).all()
    return [{"period": str(r.period), "total_revenue": r.total_revenue} for r in result]

@app.get("/inventory/", response_model=List[InventoryResponse])
def get_inventory(low_stock_threshold: Optional[int] = 10, db: Session = Depends(get_db)):
    query = db.query(Inventory)
    query = query.filter(Inventory.quantity <= low_stock_threshold)
    return query.all()

@app.put("/inventory/{product_id}")
def update_inventory(product_id: int, quantity: int, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    inventory.quantity = quantity
    inventory.last_updated = datetime.utcnow()
    db.commit()
    return {"message": "Inventory updated"}

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8000)