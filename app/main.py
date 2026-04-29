from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from app.config.database import get_connection

app = FastAPI(
    title="Ganarya Product Service API",
    version="1.0.0",
    docs_url="/ganarya-docs",          # disable docs bawaan
    redoc_url="/ganarya-redoc"
)

# =========================
# Custom Swagger UI
# =========================
@app.get("/ganarya-docs", include_in_schema=False)
async def custom_swagger():

    html = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Ganarya API Documentation",
        swagger_favicon_url="https://cdn-icons-png.flaticon.com/512/5968/5968350.png"
    ).body.decode("utf-8")

    custom_css = """
    <style>
        body {
            background: linear-gradient(135deg, #0f172a, #111827);
        }

        .topbar {
            display: none !important;
        }

        .swagger-ui .info {
            margin: 30px 0;
            padding: 25px;
            background: rgba(255,255,255,0.04);
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .swagger-ui .info .title {
            color: #00ff99 !important;
            font-size: 42px;
            font-weight: bold;
        }

        .swagger-ui .info p {
            color: #cbd5e1 !important;
        }

        .swagger-ui .scheme-container {
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 15px;
        }

        .swagger-ui .opblock {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0,0,0,0.25);
        }

        .swagger-ui .opblock-summary-path {
            color: white !important;
            font-weight: bold;
        }

        .swagger-ui .btn.execute {
            background: #00ff99 !important;
            color: black !important;
            font-weight: bold;
            border-radius: 8px;
        }

        .swagger-ui .response-col_status {
            color: #00ff99 !important;
        }

        .ganarya-banner {
            text-align:center;
            color:white;
            font-size:18px;
            margin-top:20px;
            margin-bottom:10px;
            letter-spacing:2px;
        }
    </style>

    <div class="ganarya-banner">
        🚀 Powered by GANARYA • FastAPI • PostgreSQL • Docker • Jenkins
    </div>
    """

    html = html.replace("</head>", custom_css + "</head>")

    return HTMLResponse(html)

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
        "message": "Ganarya Product Service Running 🚀"
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
