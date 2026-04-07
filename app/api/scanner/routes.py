from fastapi import APIRouter, Depends, HTTPException
from app.api.scanner.service import create_scan_task_to_queue
from app.core.redis_queue import RedisClient
from app.core.middleware import protect
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.base import get_db
import json
from app.db.models import ScanResult, ScanRequest, User, Organization
from app.api.scanner.schemas import ScanTaskRequest, ScanHistoryRequest

redis_client = RedisClient()

router = APIRouter(prefix='/scanner', tags=["scanner"])

@router.post("/register-scan-task")
async def register_scan_task(
    domain: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(protect)
):
    # Domain is taken directly from the user's registered domain in DB
    domain = domain
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
    db: Session = Depends(get_db)
):
    user = db.query(User).first()
    current_user = {"domain": user.domain, "user_id": user.user_id, "organization_id": user.organization_id}
    # Scope by organization — all org members see the same data
    org_id = current_user["organization_id"]
    org_user_ids = [
        u.user_id for u in
        db.query(User.user_id).filter(User.organization_id == org_id).all()
    ]

    scan = db.query(ScanResult).filter(
        ScanResult.scan_id == scan_id,
        ScanResult.user_id.in_(org_user_ids)
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan.results


@router.post("/scan-history")
def get_scan_history(
    db: Session = Depends(get_db),
):
    """Return all scans"""
    scans = (
        db.query(ScanRequest)
        .order_by(desc(ScanRequest.time))
        .all()
    )
    req: ScanHistoryRequest,
    db: Session = Depends(get_db)
):
    """Return all scans belonging to the organization (all members see the same data)."""
    org_id = req.org_id
    org_user_ids = [
        u.user_id for u in
        db.query(User.user_id).filter(User.organization_id == org_id).all()
    ]

    scans = db.query(ScanRequest).filter(
        ScanRequest.user_id.in_(org_user_ids)
    ).order_by(ScanRequest.time.desc()).all()

    return [
        {
            "scan_id": s.scan_id,
            "domain": s.domain,
            "time": s.time.isoformat() if s.time else None,
        }
        for s in scans
    ]