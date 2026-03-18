import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
import json
from collections import defaultdict
from app.api.scanner.schemas import RequestScanTask
from app.core.redis_queue import RedisClient
from app.db.models import ScanResult, ScanRequest

redis_client = RedisClient()


def create_scan_task_to_queue(db: Session, data: RequestScanTask):

    try:
        scan_id = str(uuid.uuid4())

        new_request = ScanRequest(
            scan_id=scan_id,
            domain=data.target
        )

        new_result = ScanResult(
            scan_id=scan_id,
            domain=data.target,
            results={
                "status": "pending",
                "progress": 0
            }
        )

        db.add_all([new_request, new_result])
        db.commit()

        scan_job = {
            "scan_id": scan_id,
            "target": data.target,
            "status": "pending",
            "progress": 0
        }

        redis_client.PushToQueue(data=scan_job)

        return {
            "message": "Scan task registered successfully",
            "scan_id": scan_id
        }

    except Exception as e:
        db.rollback()
        raise e