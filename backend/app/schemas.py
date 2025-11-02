from pydantic import BaseModel, conint
from typing import Optional, Literal, List

OrderStatus = Literal['pending','confirmed','completed','cancelled']

class OrderCreateIn(BaseModel):
    buyer_id: int
    product_id: int

class OrderConfirmIn(BaseModel):
    order_id: int
    seller_id: int   # 驗證是該商品賣家在確認

class OrderFinishIn(BaseModel):
    order_id: int
    by_user_id: int  # 允許買/賣任一方完成（之後可改策略）

class OrderCancelIn(BaseModel):
    order_id: int
    by_user_id: int  # 誰提出取消都先允許（之後可加限制）

class OrderOut(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    product_id: int
    status: OrderStatus

class ProductOut(BaseModel):
    id: int
    seller_id: int
    title: str
    description: Optional[str] = None
    price: float
    status: Literal["onsale","sold","archived"]
    cover_image_url: Optional[str] = None

class ProductListOut(BaseModel):
    total: int
    items: List[ProductOut]
