import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
import json
from collections import defaultdict
from app.core.redis_queue import RedisClient
from app.db.models import ScanResult

redis_client = RedisClient()


def create_scan_task_to_queue(db: Session, domain: str, user_id: str):
    _id = str(uuid.uuid4())
    try:
        new_result = ScanResult(
            user_id=user_id,
            domain=domain,
            results={
                "status": "pending"
            }
        )
        db.add(new_result)
        db.commit()

        scan_job = {
            "user_id": user_id,
            "target": domain
        }

        redis_client.PushToQueue(data=scan_job)
        return {
            "message": "Scan task registered successfully"
        }
    except Exception as e:
        db.rollback()
        raise e