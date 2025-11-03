import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import ssl

# 允許 .env （沒有也不影響）
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Put it in backend/.env or export it.")

# Aiven MySQL 要求 SSL；我們已在 URL 加了 ssl_mode=REQUIRED
ssl_args = {
    "ssl": {
        "ca": "/home/s12350106/ca.pem"
    }
}

engine = create_engine(
    DATABASE_URL,
    connect_args=ssl_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
