from fastapi import APIRouter, Depends, HTTPException
from app.api.scanner.service import create_scan_task_to_queue
from app.api.scanner.schemas import ScanRequest
from app.core.redis_queue import RedisClient
from app.core.middleware import require_owner, protect
from sqlalchemy.orm import Session
from app.db.base import get_db
import json
from app.db.models import ScanResult, User

redis_client = RedisClient()

router = APIRouter(prefix='/scanner', tags=["scanner"])

@router.post("/register-scan-task")
async def register_scan_task(
    request: ScanRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_owner)
):
    target = request.domain
    domain = target.strip().lower()
    org_id = user.org_id
    return create_scan_task_to_queue(db, domain, org_id)

@router.get("/scanresult")
def get_scan_result(
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    scan = db.query(ScanResult).filter(
        ScanResult.org_id == current_user.org_id
    ).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/scan-history")
def get_scan_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    scan = db.query(ScanResult).filter(
        ScanResult.org_id == current_user.org_id
    ).first()

    if not scan:
        return []

    return [
        {
            "domain": scan.domain,
            "time": scan.time.isoformat() if scan.time else None,
        }
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
