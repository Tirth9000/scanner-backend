from sqlalchemy import inspect, text

from .base import engine
from .models import Base


def _migrate_malware_scan_results():
    """Drop and recreate malware_scan_results if its schema is outdated."""
    inspector = inspect(engine)
    if "malware_scan_results" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("malware_scan_results")}
    # New schema uses composite PK (org_id, domain) and has no id/scan_id columns.
    if "id" not in columns and "scan_id" not in columns:
        return

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE malware_scan_results CASCADE"))


def init_tables():
    _migrate_malware_scan_results()
    Base.metadata.create_all(bind=engine)
