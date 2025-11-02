from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import get_db
from .schemas import OrderCreateIn, OrderConfirmIn, OrderFinishIn, OrderCancelIn, OrderOut
from . import crud

from fastapi import Query
from .schemas import ProductOut, ProductListOut
from .crud import list_products as _list_products

from .schemas import OrderOut, OrderListOut
from .crud import list_orders as _list_orders

from .schemas import ProductCreate, ProductOut
from .crud import create_product as _create_product

app = FastAPI(title="Thrift Market - Order API", version="0.1.0")

# 開發階段先全開 CORS，前端（github.io / ngrok）比較好測
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/order/create", response_model=OrderOut)
def create_order(payload: OrderCreateIn, db: Session = Depends(get_db)):
    order = crud.create_order(db, buyer_id=payload.buyer_id, product_id=payload.product_id)
    return OrderOut(
        id=order.id, buyer_id=order.buyer_id, seller_id=order.seller_id,
        product_id=order.product_id, status=order.status
    )

@app.put("/api/order/confirm", response_model=OrderOut)
def confirm_order(payload: OrderConfirmIn, db: Session = Depends(get_db)):
    order = crud.confirm_order(db, order_id=payload.order_id, seller_id=payload.seller_id)
    return OrderOut(
        id=order.id, buyer_id=order.buyer_id, seller_id=order.seller_id,
        product_id=order.product_id, status=order.status
    )

@app.put("/api/order/finish", response_model=OrderOut)
def finish_order(payload: OrderFinishIn, db: Session = Depends(get_db)):
    order = crud.finish_order(db, order_id=payload.order_id, by_user_id=payload.by_user_id)
    return OrderOut(
        id=order.id, buyer_id=order.buyer_id, seller_id=order.seller_id,
        product_id=order.product_id, status=order.status
    )

# 取消訂單
@app.put("/api/order/cancel", response_model=OrderOut)
def cancel_order(payload: OrderCancelIn, db: Session = Depends(get_db)):
    order = crud.cancel_order(db, order_id=payload.order_id, by_user_id=payload.by_user_id)

@app.get("/api/products", response_model=ProductListOut)
def get_products(
    q: str | None = Query(default=None, description="關鍵字（title/description LIKE）"),
    status: str | None = Query(default=None, description="onsale/sold/archived"),
    seller_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, rows = _list_products(db, q=q, status=status, seller_id=seller_id, limit=limit, offset=offset)
    items = [
        ProductOut(
            id=r.id, seller_id=r.seller_id, title=r.title,
            description=r.description, price=float(r.price),
            status=r.status, cover_image_url=r.cover_image_url
        ) for r in rows
    ]
    return {"total": total, "items": items}
    return OrderOut(
        id=order.id, buyer_id=order.buyer_id, seller_id=order.seller_id,
        product_id=order.product_id, status=order.status
    )

@app.get("/api/orders", response_model=OrderListOut)
def get_orders(
    buyer_id: int | None = Query(default=None),
    seller_id: int | None = Query(default=None),
    status: str | None = Query(default=None, description="pending/confirmed/completed/cancelled"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, pairs = _list_orders(db, buyer_id=buyer_id, seller_id=seller_id, status=status, limit=limit, offset=offset)
    items = []
    for o, p in pairs:
        items.append(OrderOut(
            id=o.id, buyer_id=o.buyer_id, seller_id=o.seller_id,
            product_id=o.product_id, status=o.status,
            product_title=p.title if p else None,
            product_price=float(p.price) if p and p.price is not None else None,
            product_cover=p.cover_image_url if p else None,
        ))
    return {"total": total, "items": items}

@app.post("/api/product/create", response_model=ProductOut, status_code=201)
def create_product_api(payload: ProductCreate, db: Session = Depends(get_db)):
    p = _create_product(
        db,
        seller_id=payload.seller_id,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        status=payload.status,
        cover_image_url=payload.cover_image_url,
    )
    return ProductOut(
        id=p.id,
        seller_id=p.seller_id,
        title=p.title,
        description=p.description,
        price=float(p.price),
        status=p.status,
        cover_image_url=p.cover_image_url,
    )

