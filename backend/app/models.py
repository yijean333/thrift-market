from sqlalchemy import (
    Column, BigInteger, Integer, String, Text, Enum, DECIMAL,
    TIMESTAMP, ForeignKey, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum('buyer','seller','admin'), nullable=False, default='buyer')
    status: Mapped[str] = mapped_column(Enum('active','suspended'), nullable=False, default='active')

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price = mapped_column(DECIMAL(10,2), nullable=False)
    status: Mapped[str] = mapped_column(Enum('onsale','sold','archived'), nullable=False, default='onsale')
    cover_image_url: Mapped[str | None] = mapped_column(String(255))

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    buyer_id: Mapped[int]  = mapped_column(BigInteger, ForeignKey("users.id",    onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    seller_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id",    onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    product_id: Mapped[int]= mapped_column(BigInteger, ForeignKey("products.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str]    = mapped_column(Enum('pending','confirmed','completed','cancelled'), nullable=False, default='pending')

    __table_args__ = (
        Index("idx_orders_status", "status"),
        Index("idx_orders_parties", "buyer_id", "seller_id"),
    )

