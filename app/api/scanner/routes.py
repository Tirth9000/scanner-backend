from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from app.api.scanner.service import create_scan_task_to_queue
from app.api.scanner.schemas import ScanRequest as ScanReqSchema
from app.core.redis_queue import RedisClient
from app.core.middleware import require_owner, protect
from sqlalchemy.orm import Session
from app.db.base import get_db
import json
from app.db.models import ScanResult, ScanRequest, ScanSummary, User

redis_client = RedisClient()

router = APIRouter(prefix='/scanner', tags=["scanner"])

@router.post("/register-scan-task")
async def register_scan_task(
    request: ScanReqSchema,
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

@router.get("/scanlist")
async def get_scan_list():
    data = redis_client.redis.lrange("scan_queue", 0, -1)
    return  [json.loads(item) for item in data]

@router.get("/clear")
async def clear_scan_queue(): 
    redis_client.redis.delete("scan_queue")
    return {"message": "Scan queue cleared"}

@router.get("/scan-result")
def get_scan_result_by_id(
    scan_id: str,
    db: Session = Depends(get_db)
):
    scan = db.query(ScanResult).filter(
        ScanResult.scan_id == scan_id
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan.results

@router.get("/scan-history")
@router.get("/history")
def get_scan_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    org_id = current_user.org_id
    org_user_ids = [
        u.user_id for u in
        db.query(User.user_id).filter(User.org_id == org_id).all()
    ]

    scans = db.query(ScanRequest).filter(
        ScanRequest.user_id.in_(org_user_ids),
        (ScanRequest.data.op("->>")("type") == "regular") |
        (ScanRequest.data.is_(None))
    ).order_by(desc(ScanRequest.time)).all()

    history = []
    for s in scans:
        scan_result = db.query(ScanResult).filter(
            ScanResult.scan_id == s.scan_id
        ).first()

        results = scan_result.results if scan_result else {}
        status = results.get("status", "Pending")
        
        summary = db.query(ScanSummary).filter(
            ScanSummary.domain == s.domain,
            ScanSummary.org_id == org_id
        ).first()
        domain_score = summary.domain_score if summary and summary.domain_score is not None else 0

        if status == "pending":
            display_status = "Pending"
        elif status == "failed":
            display_status = "Failed"
        elif status == "completed":
            display_status = "Completed"
        else:
            display_status = status.capitalize() if isinstance(status, str) else "Pending"

        history.append({
            "scan_id": s.scan_id,
            "domain": s.domain,
            "time": s.time.isoformat() if s.time else None,
            "status": display_status,
            "score": domain_score,
        })

    return history
