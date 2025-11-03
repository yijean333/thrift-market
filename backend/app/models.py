from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    String, Text, Enum, ForeignKey, DateTime, Numeric
)
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

# -----------------------
# users
# -----------------------
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("buyer", "seller", "admin", name="role_enum"),
        default="buyer",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "banned", name="user_status_enum"),
        default="active",
        nullable=False,
    )


# -----------------------
# products
# -----------------------
class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)  # 放大以避免長網址
    status: Mapped[str] = mapped_column(
        Enum("available", "sold", "under_review", name="product_status_enum"),
        default="available",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    # 關聯（可選）
    seller: Mapped[User] = relationship(
        "User",
        primaryjoin=seller_id == User.user_id,
        lazy="joined",
        viewonly=True,
    )


# -----------------------
# orders
# -----------------------
class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)

    order_status: Mapped[str] = mapped_column(
        Enum("pending", "paid", "shipped", "completed", "cancelled", name="order_status_enum"),
        default="pending",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    # 連 product（清單/詳情用）
    product: Mapped[Product] = relationship(
        Product,
        primaryjoin=product_id == Product.product_id,
        lazy="joined",
        viewonly=True,
    )
