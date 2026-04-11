from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.analyzer.controller import calculate_score
from app.db.models import ScanSummary, ScanResult, User
from app.core.middleware import protect

router = APIRouter(prefix="/score",tags=["Scoring"])


def build_categorized_vulnerabilities(scans: ScanSummary) -> dict:
    categorized = {}

    if scans.app_security:
        categorized["Application Security"] = scans.app_security
    if scans.network_security:
        categorized["Network Security"] = scans.network_security
    if scans.tls_security:
        categorized["TLS Security"] = scans.tls_security
    if scans.dns_security:
        categorized["DNS Security"] = scans.dns_security

    return categorized


@router.get("/generate")
def generate_score(
    db: Session = Depends(get_db),
    user: User = Depends(protect)
):
    try:
        org_id = user.org_id
        return calculate_score(db, org_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating score: {str(e)}"
        )


@router.get("/get_score/{org_id}")
def get_score(
    org_id: str,
    db: Session = Depends(get_db)
):
    score = db.query(ScanSummary).filter(
        ScanSummary.org_id == org_id
    ).first()
    if not score:
        raise HTTPException(
            status_code=404,
            detail="Score not found. Generate it first."
        )
    return {
        "org_id": score.org_id,
        "domain_score": score.domain_score,
        "host": {
            "domain": score.domain,
            "mail_security": score.mail_security or {}
        },
        "severity": score.severity,
        "categorized_vulnerabilities": build_categorized_vulnerabilities(score),
        "ips": score.ips or []
    }

@router.get("/get_raw_data/{org_id}")
def get_raw_data(
    org_id: str,
    db: Session = Depends(get_db)
):
    scan = db.query(ScanResult).filter(
        ScanResult.org_id == org_id
    ).first()
    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Raw data not found. Generate it first."
        )
    return scan

@router.delete("/delete_score/{org_id}")
def delete_score(
    org_id: str,
    db: Session = Depends(get_db)
):
    score = db.query(ScanSummary).filter(
        ScanSummary.org_id == org_id
    ).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    db.delete(score)
    db.commit()
    return {"detail": "Score deleted successfully"}
