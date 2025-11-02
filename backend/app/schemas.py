from pydantic import BaseModel, conint, Field, validator
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

class OrderOut(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    product_id: int
    status: Literal["pending","confirmed","completed","cancelled"]
    # 附帶商品資訊（精簡）
    product_title: Optional[str] = None
    product_price: Optional[float] = None
    product_cover: Optional[str] = None

class OrderListOut(BaseModel):
    total: int
    items: List[OrderOut]

class ProductCreate(BaseModel):
    seller_id: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=2000)
    price: float = Field(..., gt=0)
    status: Literal["onsale", "sold", "archived"] = "onsale"
    cover_image_url: Optional[str] = None

    @validator("title")
    def strip_title(cls, v):
        v2 = v.strip()
        if not v2:
            raise ValueError("title cannot be empty")
        return v2
