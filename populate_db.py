from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

# Database setup
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/ecommerce"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sample data
categories = [
    {"id": 1, "name": "Electronics"},
    {"id": 2, "name": "Clothing"},
    {"id": 3, "name": "Home & Kitchen"}
]

products = [
    {"id": 1, "name": "Smartphone", "category_id": 1, "price": 599.99},
    {"id": 2, "name": "T-Shirt", "category_id": 2, "price": 19.99},
    {"id": 3, "name": "Blender", "category_id": 3, "price": 49.99}
]

def populate_data():
    db = SessionLocal()
    try:
        # Insert categories
        db.execute("INSERT INTO categories (id, name) VALUES (:id, :name)", categories)
        
        # Insert products
        db.execute("INSERT INTO products (id, name, category_id, price) VALUES (:id, :name, :category_id, :price)", products)
        
        # Insert sales
        sales = []
        for i in range(100):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            sale_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 120))
            sales.append({
                "product_id": product["id"],
                "quantity": quantity,
                "sale_date": sale_date,
                "total_amount": product["price"] * quantity
            })
        db.execute("INSERT INTO sales (product_id, quantity, sale_date, total_amount) VALUES (:product_id, :quantity, :sale_date, :total_amount)", sales)
        
        # Insert inventory
        inventory = [{"product_id": p["id"], "quantity": random.randint(5, 50), "last_updated": datetime.utcnow()} for p in products]
        db.execute("INSERT INTO inventory (product_id, quantity, last_updated) VALUES (:product_id, :quantity, :last_updated)", inventory)
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    populate_data()