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
        title="Ganarya Enterprise API",
        swagger_favicon_url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    ).body.decode("utf-8")

    corporate = """
    <style>
    body {
        background: #f4f7fb !important;
        font-family: Arial, sans-serif;
    }

    .topbar {
        display:none !important;
    }

    .swagger-ui .wrapper {
        max-width: 1400px;
    }

    .swagger-ui .info {
        background: linear-gradient(90deg,#003366,#00509d);
        padding: 28px;
        border-radius: 14px;
        color: white !important;
        box-shadow: 0 8px 20px rgba(0,0,0,.12);
        margin-bottom: 30px;
    }

    .swagger-ui .info .title {
        color: white !important;
        font-size: 42px !important;
        font-weight: 700;
    }

    .swagger-ui .info .title::after {
        content: " Enterprise Edition";
        font-size: 16px;
        margin-left: 10px;
        background: #ffcc00;
        color: #003366;
        padding: 4px 10px;
        border-radius: 20px;
        vertical-align: middle;
    }

    .swagger-ui .info::before {
        content:"Banking Grade API Documentation";
        display:block;
        margin-bottom:10px;
        font-size:14px;
        opacity:.9;
    }

    .swagger-ui .scheme-container {
        background:white !important;
        border-radius:12px;
        box-shadow:0 3px 10px rgba(0,0,0,.08);
    }

    .swagger-ui .opblock {
        border-radius:12px !important;
        margin-bottom:18px !important;
        box-shadow:0 2px 10px rgba(0,0,0,.06);
        border:none !important;
    }

    .swagger-ui .opblock-summary {
        font-size:15px;
        font-weight:600;
    }

    .swagger-ui .btn.execute {
        background:#00509d !important;
        border:none !important;
        color:white !important;
        border-radius:8px;
        font-weight:bold;
    }

    .swagger-ui .models {
        background:white;
        border-radius:12px;
        box-shadow:0 2px 10px rgba(0,0,0,.05);
    }

    .swagger-ui input,
    .swagger-ui textarea {
        border-radius:8px !important;
        border:1px solid #d1d5db !important;
    }

    .footer-note{
        text-align:center;
        margin:20px;
        color:#64748b;
        font-size:13px;
    }
    </style>

    <div class="footer-note">
       🚀 Powered by Ganarya Technology • FastAPI • PostgreSQL • Jenkins CI/CD
    </div>
    """

    html = html.replace("</head>", corporate + "</head>")
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
