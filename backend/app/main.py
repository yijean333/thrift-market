from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import get_db
from .schemas import OrderCreateIn, OrderConfirmIn, OrderFinishIn, OrderCancelIn, OrderOut
from . import crud

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

#（加碼）取消訂單
@app.put("/api/order/cancel", response_model=OrderOut)
def cancel_order(payload: OrderCancelIn, db: Session = Depends(get_db)):
    order = crud.cancel_order(db, order_id=payload.order_id, by_user_id=payload.by_user_id)
    return OrderOut(
        id=order.id, buyer_id=order.buyer_id, seller_id=order.seller_id,
        product_id=order.product_id, status=order.status
    )

