# 📦 Product Service API

```text
fastapi-product-service/
├── app/
│   ├── config/
│   │   └── database.py
│   └── main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 📄 README.md

# Product Service API

Backend CRUD Product Service menggunakan **FastAPI + PostgreSQL + Raw SQL**.

## 🚀 Features

* Create Product
* Get All Products
* Get Product By ID
* Update Product
* Delete Product (Soft Delete)
* Swagger Documentation

---

## 🛠 Tech Stack

* Python 3.12
* FastAPI
* PostgreSQL
* Psycopg2
* Uvicorn
* WSL Ubuntu

---

## 📌 Prerequisites

Pastikan sudah install:

* Python 3.12+
* PostgreSQL
* Git
* WSL Ubuntu (Recommended)

Cek versi:

```bash
python3 --version
psql --version
git --version
```

---

## ⚙️ Setup & Installation

```bash
# Clone repository
git clone https://github.com/ganaryamuhammad/fastapi-product-service

# Masuk folder project
cd fastapi-product-service

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install dependency
pip install -r requirements.txt
```

---

## 🐘 PostgreSQL Setup

```bash
# Start PostgreSQL
sudo service postgresql start

# Login PostgreSQL
sudo -u postgres psql
```

```sql
-- Create database
CREATE DATABASE product_service;

-- Masuk database
\c product_service

-- Enable UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(12,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exit PostgreSQL
\q
```

---

## 🔐 Environment Variables

Buat file `.env`

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=product_service
DB_USER=postgres
DB_PASSWORD=(your_pw)
```

---

## ▶️ Run Application

```bash
uvicorn app.main:app --reload
```

---

## 📚 Swagger Docs

Buka browser:

```text
http://127.0.0.1:8000/docs
```

---

## 🌐 API Endpoints

| Method | Endpoint       | Description       |
| ------ | -------------- | ----------------- |
| GET    | /              | Home              |
| GET    | /db-test       | Database Test     |
| POST   | /products      | Create Product    |
| GET    | /products      | Get All Products  |
| GET    | /products/{id} | Get Product By ID |
| PUT    | /products/{id} | Update Product    |
| DELETE | /products/{id} | Delete Product    |

---

## 📥 Example Request

```json
{
  "sku": "SKU001",
  "name": "Laptop Lenovo",
  "description": "Gaming Laptop",
  "price": 12000000,
  "stock": 5
}
```

---

## 📝 Notes

* Delete menggunakan soft delete (`is_active = false`)
* UUID digunakan sebagai primary key
* Raw SQL digunakan tanpa ORM

---

## 👨‍💻 Author

Muhammad Ganarya Nirwana
