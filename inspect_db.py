from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # try the one from docker-compose if env not loaded
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/scanner_db"

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("Columns in scan_summary:")
for column in inspector.get_columns("scan_summary"):
    print(f"- {column['name']}: {column['type']}")
