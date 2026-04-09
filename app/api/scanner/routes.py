from fastapi import APIRouter, Depends, HTTPException
from app.api.scanner.service import create_scan_task_to_queue
from app.core.redis_queue import RedisClient
from app.core.middleware import protect
from sqlalchemy.orm import Session
from app.db.base import get_db
import json
from app.db.models import ScanResult, User
from app.api.scanner.schemas import ScanRequest

redis_client = RedisClient()

router = APIRouter(prefix='/api/scanner', tags=["scanner"])

@router.post("/register-scan-task")
async def register_scan_task(
    request:ScanRequest,
    db: Session = Depends(get_db),
    user: User = Depends(protect)
):
    target = request.domain
    domain = target.strip().lower()
    user_id = user.user_id
    # print("user_id:",user_id)
    # print(type(user_id))
    return create_scan_task_to_queue(db, domain, user_id)

@router.get("/scanresult")
def get_scan_result(
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    scan = db.query(ScanResult).filter(
        ScanResult.user_id == current_user.user_id
    ).all()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/scan-history")
def get_scan_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    scans = db.query(ScanResult).filter(
        ScanResult.user_id == current_user.user_id
    ).order_by(ScanResult.time.desc()).all()

    return [
        {
            "domain": s.domain,
            "time": s.time.isoformat() if s.time else None,
        }
        for s in scans
    ]




# for testing purpose only, to check the scan queue in redis
@router.get("/scanlist")
async def get_scan_list():
    data = redis_client.redis.lrange("scan_queue", 0, -1)
    return  [json.loads(item) for item in data]

@router.get("/clear")
async def clear_scan_queue(): 
    redis_client.redis.delete("scan_queue")
    return {"message": "Scan queue cleared"}
