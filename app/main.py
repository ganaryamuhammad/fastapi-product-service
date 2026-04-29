from fastapi import FastAPI
from pydantic import BaseModel
from app.config.database import get_connection

app = FastAPI(
    title="Product Service GANARYA COOOL",
    version="1.0.0"
)


# =========================
# Request Schema
# =========================
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str
    price: float
    stock: int
class ProductUpdate(BaseModel):
    sku: str
    name: str
    description: str
    price: float
    stock: int

# =========================
# Home
# =========================
@app.get("/")
def home():
    return {
        "success": True,
        "message": "Product Service Running"
    }


# =========================
# Database Test
# =========================
@app.get("/db-test")
def db_test():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT version();")
    version = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "success": True,
        "database": version[0]
    }


# =========================
# Create Product
# =========================
@app.post("/products")
def create_product(product: ProductCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO products (sku, name, description, price, stock)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        product.sku,
        product.name,
        product.description,
        product.price,
        product.stock
    ))

    product_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {
        "success": True,
        "message": "Product created successfully",
        "id": str(product_id)
    }


# =========================
# Get All Products
# =========================
@app.get("/products")
def get_products():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, sku, name, description, price, stock
        FROM products
        WHERE is_active = true
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()

    products = []

    for row in rows:
        products.append({
            "id": str(row[0]),
            "sku": row[1],
            "name": row[2],
            "description": row[3],
            "price": float(row[4]),
            "stock": row[5]
        })

    cur.close()
    conn.close()

    return {
        "success": True,
        "data": products
    }
@app.get("/products/{product_id}")
def get_product_by_id(product_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, sku, name, description, price, stock
        FROM products
        WHERE id = %s AND is_active = true
    """, (product_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {
            "success": False,
            "message": "Product not found"
        }

    return {
        "success": True,
        "data": {
            "id": str(row[0]),
            "sku": row[1],
            "name": row[2],
            "description": row[3],
            "price": float(row[4]),
            "stock": row[5]
        }
    }
@app.put("/products/{product_id}")
def update_product(product_id: str, product: ProductUpdate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE products
        SET sku = %s,
            name = %s,
            description = %s,
            price = %s,
            stock = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND is_active = true
    """, (
        product.sku,
        product.name,
        product.description,
        product.price,
        product.stock,
        product_id
    ))

    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return {
            "success": False,
            "message": "Product not found"
        }

    cur.close()
    conn.close()

    return {
        "success": True,
        "message": "Product updated successfully"
    }
@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE products
        SET is_active = false,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND is_active = true
    """, (product_id,))

    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()

        return {
            "success": False,
            "message": "Product not found"
        }

    cur.close()
    conn.close()

    return {
        "success": True,
        "message": "Product deleted successfully"
    }
