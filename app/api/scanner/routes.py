from fastapi import APIRouter, Depends, HTTPException
from app.api.scanner.service import create_scan_task_to_queue
from app.api.scanner.schemas import ScanRequest
from app.core.redis_queue import RedisClient
from app.core.middleware import require_owner, protect
from sqlalchemy.orm import Session
from app.db.base import get_db
import json
<<<<<<< HEAD
<<<<<<< HEAD
from app.db.models import ScanResult, ScanRequest, ScanSummary
=======
from app.db.models import ScanResult, ScanRequest, User, Organization
from app.api.scanner.schemas import ScanTaskRequest, ScanHistoryRequest
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)
=======
from app.db.models import ScanResult, User
<<<<<<< HEAD
from app.api.scanner.schemas import ScanRequest
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
=======
>>>>>>> f2b3fc1 (member feature plus some route changes)

redis_client = RedisClient()

router = APIRouter(prefix='/scanner', tags=["scanner"])

@router.post("/register-scan-task")
<<<<<<< HEAD
<<<<<<< HEAD
async def register_scan_task(
<<<<<<< HEAD
    payload: RequestScanTask,
    db: Session = Depends(get_db),
    current_user: dict = Depends(protect)
):
    domain = (payload.target or "").strip().lower()[:255]
    if not domain:
        raise HTTPException(status_code=400, detail="target domain is required")
    # Minimal validation (frontend also validates); keep backend resilient.
    if "://" in domain or "/" in domain or " " in domain:
        raise HTTPException(status_code=400, detail="target must be a bare domain like example.com")
    return create_scan_task_to_queue(db, domain, current_user["user_id"])
=======
    request: ScanTaskRequest,
    db: Session = Depends(get_db)
):
    domain = request.domain
    user_id = request.user_id
    return create_scan_task_to_queue(db, domain, user_id)
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)

=======
async def register_scan_task(domain: str,
    db: Session = Depends(get_db)
):
    return create_scan_task_to_queue(db,domain)
>>>>>>> f4a690b (Refactor scanner API routes and schemas; remove user_id dependency from scan tasks)
=======
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



<<<<<<< HEAD
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)

=======
>>>>>>> f2b3fc1 (member feature plus some route changes)
# for testing purpose only, to check the scan queue in redis
@router.get("/scanlist")
async def get_scan_list():
    data = redis_client.redis.lrange("scan_queue", 0, -1)
    return  [json.loads(item) for item in data]

@router.get("/clear")
async def clear_scan_queue(): 
    redis_client.redis.delete("scan_queue")
    return {"message": "Scan queue cleared"}
<<<<<<< HEAD

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
<<<<<<< HEAD
        ScanResult.scan_id == scan_id,
        ScanResult.user_id.in_(org_user_ids)
=======
        ScanResult.scan_id == scan_id
>>>>>>> f4a690b (Refactor scanner API routes and schemas; remove user_id dependency from scan tasks)
    ).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan.results


<<<<<<< HEAD
@router.get("/scan-history")
@router.get("/history")
=======
@router.post("/scan-history")
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)
def get_scan_history(
<<<<<<< HEAD
    req: ScanHistoryRequest,
    db: Session = Depends(get_db)
):
<<<<<<< HEAD
    """Return all regular scans (non-malware) belonging to the logged-in user."""
    scans = db.query(ScanRequest).filter(
        ScanRequest.user_id == current_user["user_id"],
        (ScanRequest.data.op("->>")("type") == "regular") |
        (ScanRequest.data.is_(None))
=======
    """Return all scans belonging to the organization (all members see the same data)."""
    org_id = req.org_id
    org_user_ids = [
        u.user_id for u in
        db.query(User.user_id).filter(User.organization_id == org_id).all()
    ]

    scans = db.query(ScanRequest).filter(
        ScanRequest.user_id.in_(org_user_ids)
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)
    ).order_by(ScanRequest.time.desc()).all()

    history = []
    for s in scans:
        scan_result = db.query(ScanResult).filter(
            ScanResult.scan_id == s.scan_id
        ).first()

        results = scan_result.results if scan_result else {}
        status = results.get("status", "Pending")
        
        summary = db.query(ScanSummary).filter(
            ScanSummary.scan_id == s.scan_id
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
=======
    db: Session = Depends(get_db),
):
    """Return all scans"""
    scans = (
        db.query(ScanRequest)
        .order_by(desc(ScanRequest.time))
        .all()
    )
    return [
        {
>>>>>>> f4a690b (Refactor scanner API routes and schemas; remove user_id dependency from scan tasks)
            "scan_id": s.scan_id,
            "domain": s.domain,
            "time": s.time.isoformat() if s.time else None,
            "status": display_status,
            "score": domain_score,
        })

    return history
=======
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
