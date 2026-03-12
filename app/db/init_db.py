from .base import engine
from .models import Base


def init_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")