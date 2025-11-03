from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException
from .models import Product, Order

# 產品：建立
def create_product(
    db: Session,
    seller_id: int,
    name: str,
    description: str | None,
    price: float,
    category: str | None,
    image_url: str | None,
    status: str = "available",
) -> Product:
    if status not in ("available","sold","under_review"):
        raise HTTPException(400, "invalid product status")
    p = Product(
        seller_id=seller_id, name=name, description=description,
        price=price, category=category, image_url=image_url, status=status
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

# 產品：列表
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
    if status: conds.append(Product.status == status)
    if seller_id: conds.append(Product.seller_id == seller_id)
    if q:
        like = f"%{q}%"
        conds.append(or_(Product.name.like(like), Product.description.like(like)))
    if conds: stmt = stmt.where(and_(*conds))
    stmt = stmt.order_by(Product.product_id.desc()).limit(limit).offset(offset)
    items = list(db.scalars(stmt))

    count_stmt = select(func.count()).select_from(Product)
    if conds: count_stmt = count_stmt.where(and_(*conds))
    total = db.scalar(count_stmt) or 0
    return total, items

# 訂單：建立（最小流程：pending）
def create_order(db: Session, buyer_id: int, product_id: int) -> Order:
    # 檢查商品存在且可售
    prod = db.get(Product, product_id)
    if not prod:
        raise HTTPException(404, "product not found")
    if prod.status != "available":
        raise HTTPException(400, "product not available")

    o = Order(buyer_id=buyer_id, product_id=product_id, order_status="pending")
    # 標記商品成 sold（或你想走 under_review 也可）
    prod.status = "sold"
    db.add(o)
    db.commit()
    db.refresh(o)
    return o

# 訂單：列表（買家/賣家/狀態）
def list_orders(
    db: Session,
    buyer_id: int | None = None,
    seller_id: int | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    conds = []
    if buyer_id: conds.append(Order.buyer_id == buyer_id)
    if seller_id:  # 透過 join product 的 seller_id 篩
        conds.append(Product.seller_id == seller_id)
    if status:
        conds.append(Order.order_status == status)

    base = select(Order, Product).join(Product, Product.product_id == Order.product_id)
    if conds: base = base.where(and_(*conds))
    base = base.order_by(Order.order_id.desc()).limit(limit).offset(offset)

    rows = db.execute(base).all()
    items = [(r[0], r[1]) for r in rows]

    count_stmt = select(func.count()).select_from(Order)
    if status: count_stmt = count_stmt.where(Order.order_status == status)
    if buyer_id: count_stmt = count_stmt.where(Order.buyer_id == buyer_id)
    # seller_id 的 count 需要 join
    if seller_id:
        count_stmt = select(func.count()).select_from(Order).join(Product, Product.product_id == Order.product_id).where(Product.seller_id == seller_id)
    total = db.scalar(count_stmt) or 0
    return total, items

# 訂單：狀態流轉
def update_order_status(db: Session, order_id: int, new_status: str) -> Order:
    if new_status not in ("pending","paid","shipped","completed","cancelled"):
        raise HTTPException(400, "invalid order_status")
    o = db.get(Order, order_id)
    if not o: raise HTTPException(404, "order not found")
    o.order_status = new_status
    db.commit()
    db.refresh(o)
    return o
