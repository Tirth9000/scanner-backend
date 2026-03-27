import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.redis_queue import RedisClient
from app.api.fix.schemas import FixRequest, FixResponse, FixResultRequest
from app.db.base import get_db
from app.db.models import ScanSummary

router = APIRouter(prefix="/api/fix", tags=["Fix"])

redis_client = RedisClient()

QUEUE_NAME = "fix_queue"

FIX_TYPE_TO_ISSUE_KEY = {
    # Network Security
    "unexpected_port": "Unexpected open port",
    "risky_port": "Risky port exposed",

    # App Security
    "missing_csp": "Missing CSP header",
    "missing_hsts": "Missing HSTS header",
    "missing_x_frame": "Missing X-Frame-Options",
    "missing_x_content": "Missing X-Content-Type-Options",
    "http_without_https": "HTTP without HTTPS",

    # TLS Security
    "expired_tls": "Expired TLS",
    "weak_tls": "Weak TLS version",
    "tls_missing_443": "443 open without TLS",

    # DNS Security
    "missing_ns": "Missing NS record",
    "missing_mx": "Missing MX record",
    "missing_txt": "Missing TXT record",
    "duplicate_spf": "Duplicate SPF record",
    "weak_spf": "Weak SPF policy",
    "missing_spf": "Missing SPF record",
    "missing_dmarc": "Missing DMARC",
    "weak_dmarc": "Weak DMARC policy",
    "missing_dkim": "Missing DKIM",
}

FIX_TYPE_TO_CATEGORY = {
    # Network Security
    "unexpected_port": "network_security",
    "risky_port": "network_security",
    # App Security
    "missing_csp": "app_security",
    "missing_hsts": "app_security",
    "missing_x_frame": "app_security",
    "missing_x_content": "app_security",
    "http_without_https": "app_security",
    # TLS Security
    "expired_tls": "tls_security",
    "weak_tls": "tls_security",
    "tls_missing_443": "tls_security",
    # DNS Security
    "missing_ns": "dns_security",
    "missing_mx": "dns_security",
    "missing_txt": "dns_security",
    "duplicate_spf": "dns_security",
    "weak_spf": "dns_security",
    "missing_spf": "dns_security",
    "missing_dmarc": "dns_security",
    "weak_dmarc": "dns_security",
    "missing_dkim": "dns_security",
}

def is_fix_successful(result) -> bool:
    if isinstance(result, bool):
        return result
    if isinstance(result, str):
        return result.strip().lower() in {"success", "succeeded", "ok", "true"}
    if isinstance(result, dict):
        for key in ("success", "is_success", "fixed"):
            if key in result:
                return bool(result[key])
        status = str(result.get("status", "")).strip().lower()
        if status:
            return status in {"success", "succeeded", "ok"}
    return False


def remove_fixed_issue(summary_row: ScanSummary, issue_key: str, domain: str, category: str):
    allowed_categories = {"app_security", "network_security", "tls_security", "dns_security"}
    if category not in allowed_categories:
        return

    category_data = getattr(summary_row, category, None) or {}
    findings = list(category_data.get(issue_key, []))
    if not findings:
        return

    updated_findings = [f for f in findings if f.get("subdomain") != domain]
    if updated_findings:
        category_data[issue_key] = updated_findings
    else:
        category_data.pop(issue_key, None)

    setattr(summary_row, category, category_data or None)


@router.post("/submit", response_model=FixResponse)
def submit_fix(request: FixRequest):
    try:
        redis_client.redis.rpush(QUEUE_NAME, json.dumps(request.model_dump()))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Redis connection failed. Please try again later."
        )

    return FixResponse(
        message="Fix request queued successfully",
        scan_id=request.scan_id,
        reload=False,
    )


@router.post("/result", response_model=FixResponse)
async def submit_fix_result(request: FixResultRequest, db: Session = Depends(get_db)):
    should_reload = False
    try:
        if is_fix_successful(request.result):
            issue_key = FIX_TYPE_TO_ISSUE_KEY.get(request.fix_type)
            category = FIX_TYPE_TO_CATEGORY.get(request.fix_type)
            if issue_key and category:
                summary = db.query(ScanSummary).filter(
                    ScanSummary.scan_id == request.scan_id
                ).first()
                if summary:
                    remove_fixed_issue(summary, issue_key, request.domain, category)
                    db.add(summary)
                    db.commit()
                    should_reload = True
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update scan summary after fix result"
        )

    return FixResponse(
        message="Fix result stored successfully",
        scan_id=request.scan_id,
        reload=should_reload,
    )
