import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Engine (connection pool handled automatically)
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
    pool_recycle=3600,
    pool_timeout=30
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
