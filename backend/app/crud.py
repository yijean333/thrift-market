from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select, and_, or_, func
from . import models
from .models import Product

def get_product(db: Session, product_id: int) -> models.Product | None:
    return db.scalar(select(models.Product).where(models.Product.id == product_id))

def get_order(db: Session, order_id: int) -> models.Order | None:
    return db.scalar(select(models.Order).where(models.Order.id == order_id))

def create_order(db: Session, buyer_id: int, product_id: int) -> models.Order:
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    if product.status != "onsale":
        raise HTTPException(400, "Product not available for sale")

    order = models.Order(
        buyer_id=buyer_id,
        seller_id=product.seller_id,
        product_id=product_id,
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def confirm_order(db: Session, order_id: int, seller_id: int) -> models.Order:
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "pending":
        raise HTTPException(400, "Only pending orders can be confirmed")
    if order.seller_id != seller_id:
        raise HTTPException(403, "Only the seller can confirm")

    product = get_product(db, order.product_id)
    if not product:
        raise HTTPException(500, "Product missing")
    if product.status != "onsale":
        raise HTTPException(400, "Product is not available")

    order.status = "confirmed"
    product.status = "sold"
    db.commit()
    db.refresh(order)
    return order

def finish_order(db: Session, order_id: int, by_user_id: int) -> models.Order:
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "confirmed":
        raise HTTPException(400, "Only confirmed orders can be finished")
    if by_user_id not in (order.buyer_id, order.seller_id):
        raise HTTPException(403, "Not part of this order")

    order.status = "completed"
    db.commit()
    db.refresh(order)
    return order

def cancel_order(db: Session, order_id: int, by_user_id: int) -> models.Order:
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status in ("completed", "cancelled"):
        raise HTTPException(400, "Order is already finalized")
    if by_user_id not in (order.buyer_id, order.seller_id):
        raise HTTPException(403, "Not part of this order")

    order.status = "cancelled"

    product = get_product(db, order.product_id)
    if product and product.status == "sold":
        product.status = "onsale"

    db.commit()
    db.refresh(order)
    return order

def list_products(
    db: Session,
    q: str | None = None,
    status: str | None = None,
    seller_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
):
    stmt = select(Product)
    conds = []
    if status:
        conds.append(Product.status == status)
    if seller_id:
        conds.append(Product.seller_id == seller_id)
    if q:
        like = f"%{q}%"
        conds.append(or_(Product.title.like(like), Product.description.like(like)))
    if conds:
        stmt = stmt.where(and_(*conds))
    # 先依 id 由新到舊
    stmt = stmt.order_by(Product.id.desc()).limit(limit).offset(offset)

    items = list(db.scalars(stmt))
    # total（簡易做法：重跑 count）
    count_stmt = select(func.count()).select_from(Product)
    if conds:
        count_stmt = count_stmt.where(and_(*conds))
    total = db.scalar(count_stmt) or 0
    return total, items
