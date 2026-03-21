from .base import engine
from .models import Base
from sqlalchemy import text


def init_tables():
    Base.metadata.create_all(bind=engine)
    
    # Ensure new columns exist on existing tables (lightweight migration)
    with engine.connect() as conn:
        # Add 'ips' column to scan_summary if it doesn't exist
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='scan_summary' AND column_name='ips'"
        ))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE scan_summary ADD COLUMN ips JSONB"))
            conn.commit()
            print("Added 'ips' column to scan_summary table")