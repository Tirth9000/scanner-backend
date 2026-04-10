from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.analyzer.controller import calculate_score
from app.db.models import ScanSummary, ScanResult, User
from app.core.middleware import protect

router = APIRouter(prefix="/api/score",tags=["Scoring"])


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
        user_id = user.user_id
        return calculate_score(db, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating score: {str(e)}"
        )


@router.get("/get_score")
def get_score(
    db: Session = Depends(get_db),
    user: User = Depends(protect)
):
    user_id = user.user_id
    score = db.query(ScanSummary).filter(
        ScanSummary.user_id == user_id
    ).last()
    if not score:
        raise HTTPException(
            status_code=404,
            detail="Score not found. Generate it first."
        )
    return {
        "user_id": score.user_id,
        "domain_score": score.domain_score,
        "host": {
            "domain": score.domain,
            "mail_security": score.mail_security or {}
        },
        "severity": score.severity,
        "categorized_vulnerabilities": build_categorized_vulnerabilities(score),
        "ips": score.ips or []
    }

@router.get("/get_raw_data/{user_id}")
def get_raw_data(
    user_id: str,
    db: Session = Depends(get_db)
):
    score = db.query(ScanResult).filter(
        ScanResult.user_id == user_id
    ).all()
    if not score:
        raise HTTPException(
            status_code=404,
            detail="Raw data not found. Generate it first."
        )
    return [s for s in score]

@router.delete("/delete_score/{user_id}")
def delete_score(
    user_id: str,
    db: Session = Depends(get_db)
):
    score = db.query(ScanSummary).filter(
        ScanSummary.user_id == user_id
    ).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    db.delete(score)
    db.commit()
    return {"detail": "Score deleted successfully"}