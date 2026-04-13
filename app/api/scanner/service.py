import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
import json
from collections import defaultdict
from app.core.redis_queue import RedisClient
from app.db.models import ScanResult, ScanRequest

redis_client = RedisClient()


def create_scan_task_to_queue(db: Session, domain: str, org_id: str):
    try:
        # 1. Update/Upsert the latest scan status in ScanResult
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
                results={"status": "pending"}
            )
            db.add(new_result)

        # 2. Add entry to ScanRequest (History)
        new_history = ScanRequest(
            org_id=org_id,
            domain=domain,
            data={"type": "regular", "status": "pending"}
        )
        db.add(new_history)

        db.commit()

        scan_job = {
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