from sqlalchemy import Column, Integer, String, Text, DECIMAL, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .db import Base

# users
class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum("buyer","seller","admin", name="role_enum"), default="buyer")
    created_at: Mapped = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    status: Mapped[str] = mapped_column(Enum("active","banned", name="user_status_enum"), default="active")

# products
class Product(Base):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)  # 放大至 1024，避免 URL 過長
    status: Mapped[str] = mapped_column(Enum("available","sold","under_review", name="product_status_enum"), default="available")
    created_at: Mapped = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

# orders
class Order(Base):
    __tablename__ = "orders"
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    buyer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id"), nullable=False)
    order_status: Mapped[str] = mapped_column(
        Enum("pending","paid","shipped","completed","cancelled", name="order_status_enum"),
        default="pending"
    )
    created_at: Mapped = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    # 關聯（可選）
    product = relationship(Product, primaryjoin=product_id == Product.product_id, lazy="joined")
