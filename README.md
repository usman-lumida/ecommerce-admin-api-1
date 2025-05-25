E-commerce Admin API
This is a FastAPI-based back-end API for an e-commerce admin dashboard, providing endpoints for sales analysis, revenue tracking, inventory management, and product registration.
Setup Instructions

Clone the Repository:
git clone https://github.com/UsmanSiddiqui786/ecommerce-admin-api.git
cd ecommerce-admin-api


Install Dependencies:Ensure Python 3.8+ is installed. Install required packages:
pip install fastapi uvicorn sqlalchemy mysql-connector-python pydantic


Set Up MySQL Database:

Install MySQL and create a database named ecommerce.
Update the database connection string in main.py with your MySQL credentials:SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://your_username:your_password@localhost:3306/ecommerce"


Run the schema script:mysql -u your_username -p < schema.sql




Populate Demo Data:Run the demo data script to populate the database:
python populate_db.py


Run the Application:Start the FastAPI server:
uvicorn main:app --reload

The API will be available at http://localhost:8000.


Dependencies

Python 3.8+
FastAPI
Uvicorn
SQLAlchemy
mysql-connector-python
Pydantic

API Endpoints

POST /products/: Register a new product.
Request: { "name": "string", "category_id": int, "price": float }
Response: Created product details.


GET /sales/: Retrieve sales data, filterable by start_date, end_date, product_id, or category_id.
Example: /sales/?start_date=2025-01-01&end_date=2025-05-01
Response: List of sales with id, product_id, quantity, sale_date, total_amount.


GET /revenue/{period}: Get revenue for a period (daily, weekly, monthly, yearly).
Example: /revenue/monthly
Response: List of periods with total revenue.


GET /inventory/: View inventory status, filterable by low_stock_threshold.
Example: /inventory/?low_stock_threshold=10
Response: List of inventory records.


PUT /inventory/{product_id}: Update inventory quantity for a product.
Request: { "quantity": int }
Response: Confirmation message.



Database
The database schema is defined in schema.sql and includes tables for categories, products, sales, and inventory. Refer to database_documentation.tex for detailed schema documentation.
