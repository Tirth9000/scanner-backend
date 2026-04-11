import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
import json
from collections import defaultdict
from app.core.redis_queue import RedisClient
from app.db.models import ScanResult

redis_client = RedisClient()


def create_scan_task_to_queue(db: Session, domain: str, org_id: str):
    try:
        # Check if scan result already exists for this org (upsert)
        existing = db.query(ScanResult).filter(
            ScanResult.org_id == org_id
        ).first()

        if existing:
            existing.domain = domain
            existing.results = {"status": "pending"}
        else:
            new_result = ScanResult(
                org_id=org_id,
                domain=domain,
                results={
                    "status": "pending"
                }
            )
            db.add(new_result)

        db.commit()

        scan_job = {
            "scan_id": org_id,
            "org_id": org_id,
            "target": domain
        }

        redis_client.PushToQueue(data=scan_job)
        return {
            "message": "Scan task registered successfully"
        }
    except Exception as e:
        db.rollback()
        raise e