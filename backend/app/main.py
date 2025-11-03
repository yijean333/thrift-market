from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from .db import get_db
from .schemas import (
    ProductCreate, ProductOut, ProductListOut,
    OrderCreate, OrderOut, OrderListOut
)
from .crud import (
    create_product as _create_product,
    list_products as _list_products,
    create_order as _create_order,
    list_orders as _list_orders,
    update_order_status as _update_order_status,
)

app = FastAPI()

# CORS（GitHub Pages / ngrok）
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或 ["https://yijean333.github.io"]
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"ok": True}

# ---- Products ----
@app.post("/api/product/create", response_model=ProductOut, status_code=201)
def create_product_api(payload: ProductCreate, db: Session = Depends(get_db)):
    p = _create_product(
        db,
        seller_id=payload.seller_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        category=payload.category,
        image_url=payload.image_url,
        status=payload.status,
    )
    return ProductOut(
        product_id=p.product_id, seller_id=p.seller_id, name=p.name,
        description=p.description, price=float(p.price), category=p.category,
        image_url=p.image_url, status=p.status
    )

@app.get("/api/products", response_model=ProductListOut)
def get_products(
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    seller_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, rows = _list_products(db, q=q, status=status, seller_id=seller_id, limit=limit, offset=offset)
    items = [
        ProductOut(
            product_id=r.product_id, seller_id=r.seller_id, name=r.name,
            description=r.description, price=float(r.price), category=r.category,
            image_url=r.image_url, status=r.status
        ) for r in rows
    ]
    return {"total": total, "items": items}

# ---- Orders ----
@app.post("/api/order/create", response_model=OrderOut)
def create_order_api(payload: OrderCreate, db: Session = Depends(get_db)):
    o = _create_order(db, buyer_id=payload.buyer_id, product_id=payload.product_id)
    p = o.product
    return OrderOut(
        order_id=o.order_id, buyer_id=o.buyer_id, product_id=o.product_id, order_status=o.order_status,
        product_name=p.name if p else None, product_price=float(p.price) if p else None, product_image=p.image_url if p else None
    )

@app.get("/api/orders", response_model=OrderListOut)
def get_orders(
    buyer_id: int | None = Query(default=None),
    seller_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, pairs = _list_orders(db, buyer_id=buyer_id, seller_id=seller_id, status=status, limit=limit, offset=offset)
    items = []
    for o, p in pairs:
        items.append(OrderOut(
            order_id=o.order_id, buyer_id=o.buyer_id, product_id=o.product_id, order_status=o.order_status,
            product_name=p.name if p else None, product_price=float(p.price) if p else None, product_image=p.image_url if p else None
        ))
    return {"total": total, "items": items}

# 狀態更新（示範：賣家確認→我們用 paid 代表已收單/已付款；若你想維持 confirmed 也可）
from pydantic import BaseModel
class OrderStatusIn(BaseModel):
    order_id: int
    new_status: str

@app.put("/api/order/status", response_model=OrderOut)
def update_order_status_api(payload: OrderStatusIn, db: Session = Depends(get_db)):
    o = _update_order_status(db, order_id=payload.order_id, new_status=payload.new_status)
    p = o.product
    return OrderOut(
        order_id=o.order_id, buyer_id=o.buyer_id, product_id=o.product_id, order_status=o.order_status,
        product_name=p.name if p else None, product_price=float(p.price) if p else None, product_image=p.image_url if p else None
    )
