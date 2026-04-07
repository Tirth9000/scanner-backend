from fastapi import APIRouter, Depends, HTTPException
from app.api.scanner.service import create_scan_task_to_queue
from app.core.redis_queue import RedisClient
from app.core.middleware import protect
from sqlalchemy.orm import Session
from app.db.base import get_db
import json
from app.db.models import ScanResult, ScanRequest

redis_client = RedisClient()

router = APIRouter(prefix='/api/scanner', tags=["scanner"])

@router.post("/register-scan-task")
async def register_scan_task(
    domain: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(protect)
):
    # Domain is taken directly from the user's registered domain in DB
    domain = domain.strip().lower()
    return create_scan_task_to_queue(db, domain, current_user["user_id"])


# for testing purpose only, to check the scan queue in redis
@router.get("/scanlist")
async def get_scan_list():
    data = redis_client.redis.lrange("scan_queue", 0, -1)
    return  [json.loads(item) for item in data]

@router.get("/clear")
async def clear_scan_queue(): 
    redis_client.redis.delete("scan_queue")
    return {"message": "Scan queue cleared"}

@router.get("/scan-result")
def get_scan_result(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(protect)
):
    scan = db.query(ScanResult).filter(
        ScanResult.scan_id == scan_id,
        ScanResult.user_id == current_user["user_id"]
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan.results


@router.get("/scan-history")
def get_scan_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(protect)
):
    """Return all scans belonging to the logged-in user."""
    scans = db.query(ScanRequest).filter(
        ScanRequest.user_id == current_user["user_id"]
    ).order_by(ScanRequest.time.desc()).all()

    return [
        {
            "scan_id": s.scan_id,
            "domain": s.domain,
            "time": s.time.isoformat() if s.time else None,
        }
        for s in scans
    ]