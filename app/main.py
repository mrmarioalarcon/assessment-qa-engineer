from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import jwt

app = FastAPI(title="Inventory Management API", version="1.0.0")
security = HTTPBearer()

SECRET_KEY = "secret123"
ALGORITHM = "HS256"

fake_db = {
    "users": {
        "admin": {"password": "admin123", "role": "admin"},
        "user": {"password": "user123", "role": "user"}
    },
    "products": {},
    "product_counter": 0
}


class LoginRequest(BaseModel):
    username: str
    password: str


class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int
    min_stock: int = 10


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    min_stock: Optional[int] = None


class InventoryAdjust(BaseModel):
    product_id: int
    adjustment: int
    reason: str


class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    min_stock: int
    created_at: str


def create_token(username: str, role: str) -> str:
    expiration = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": username,
        "role": role,
        "exp": expiration
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_admin(payload: dict = Depends(verify_token)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/auth/login")
def login(request: LoginRequest):
    user = fake_db["users"].get(request.username)
    if user and user["password"] == request.password:
        token = create_token(request.username, user["role"])
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/products", response_model=List[Product])
def list_products(
    skip: int = 0,
    limit: int = 100,
    payload: dict = Depends(verify_token)
):
    products = list(fake_db["products"].values())
    return products[skip:limit]


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, payload: dict = Depends(verify_token)):
    product = fake_db["products"].get(product_id)
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", response_model=Product, status_code=201)
def create_product(product: ProductCreate, payload: dict = Depends(require_admin)):
    fake_db["product_counter"] += 1
    product_id = fake_db["product_counter"]
    
    new_product = {
        "id": product_id,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
        "min_stock": product.min_stock,
        "created_at": datetime.utcnow().isoformat()
    }
    fake_db["products"][product_id] = new_product
    return new_product


@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductUpdate,
    payload: dict = Depends(require_admin)
):
    existing = fake_db["products"].get(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.name:
        existing["name"] = product.name
    if product.price:
        existing["price"] = product.price
    if product.quantity:
        existing["quantity"] = product.quantity
    if product.min_stock:
        existing["min_stock"] = product.min_stock
    
    return existing


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, payload: dict = Depends(require_admin)):
    if product_id in fake_db["products"]:
        del fake_db["products"][product_id]
    return None


@app.post("/inventory/adjust")
def adjust_inventory(
    adjustment: InventoryAdjust,
    payload: dict = Depends(require_admin)
):
    product = fake_db["products"].get(adjustment.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product["quantity"] = product["quantity"] + adjustment.adjustment
    
    return {
        "product_id": adjustment.product_id,
        "new_quantity": product["quantity"],
        "adjustment": adjustment.adjustment,
        "reason": adjustment.reason
    }


@app.get("/inventory/low-stock")
def get_low_stock_products(payload: dict = Depends(verify_token)):
    low_stock = []
    for product in fake_db["products"].values():
        if product["quantity"] > product["min_stock"]:
            low_stock.append(product)
    return low_stock


@app.get("/products/{product_id}/profit-margin")
def calculate_profit_margin(
    product_id: int,
    cost: float,
    payload: dict = Depends(verify_token)
):
    product = fake_db["products"].get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    margin = (product["price"] - cost) / cost * 100
    return {
        "product_id": product_id,
        "price": product["price"],
        "cost": cost,
        "margin_percentage": round(margin, 2)
    }


@app.get("/products/search/{name}")
def search_products(name: str, payload: dict = Depends(verify_token)):
    results = []
    for product in fake_db["products"].values():
        if name in product["name"]:
            results.append(product)
    return results


@app.get("/inventory/value")
def calculate_inventory_value(payload: dict = Depends(verify_token)):
    total = 0
    for product in fake_db["products"].values():
        total = product["price"] * product["quantity"]
    return {"total_value": total}
