from fastapi import APIRouter, Depends
from app.api.scanner.service import create_scan_task_to_queue
from app.api.scanner.schemas import RequestScanTask
from app.core.redis_queue import RedisClient
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import ScanResult
import uuid, json


router = APIRouter(prefix='/api/scanner', tags=["scanner"])

@router.post("/register-scan-task")
async def register_scan_task(
    request: RequestScanTask,
    db: Session = Depends(get_db)
):
    result = await create_scan_task_to_queue(request)
    scan_id = result["scan_id"]
    new_scan = ScanResult(
        user_id=request.user_id,
        scan_id=scan_id,
        domain=request.target,
        results={"status": "pending"}
    )

    db.add(new_scan)
    db.commit()

    return result


@router.get("/scanlist")
def get_scan_list():
    redis_client = RedisClient() 
    data = redis_client.redis.lrange("scan_queue", 0, -1)
    return  [json.loads(item) for item in data]
    # return [item for item in data]

@router.get("/clear")
def clear_scan_queue():
    redis_client = RedisClient() 
    redis_client.redis.delete("scan_queue")
    return {"message": "Scan queue cleared"}