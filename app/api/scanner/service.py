import uuid
from app.api.scanner.schemas import RequestScanTask
from app.core.redis_queue import RedisClient
from sqlalchemy.orm import Session
from app.db.models import ScanResult

redis_client = RedisClient()


def create_scan_task_to_queue(
    db: Session,
    data: RequestScanTask
):
    scan_id = str(uuid.uuid4())

    new_scan = ScanResult(
        # user_id=data.user_id,
        scan_id=scan_id,
        domain=data.target,
        results={"status": "pending", "progress": 0}
    )

    db.add(new_scan)
    db.commit()

    scan_job = {
        # "user_id": data.user_id,
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