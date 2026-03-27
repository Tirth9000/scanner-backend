from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.analyzer.controller import calculate_score
from app.db.models import ScanSummary, ScanResult

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


@router.post("/{scan_id}")
def generate_score(scan_id: str, db: Session = Depends(get_db)):
    try:
        scans = db.query(ScanSummary).filter(ScanSummary.scan_id == scan_id).first()

        if scans:
            print("Score already exists for scan_id:", scan_id)
            return {
                "scan_id": scans.scan_id,
                "domain_score": scans.domain_score,
                "host": {
                    "domain": scans.domain,
                    "mail_security": scans.mail_security or {}
                },
                "severity": scans.severity,
                "categorized_vulnerabilities": build_categorized_vulnerabilities(scans),
                "ips": scans.ips or []
            }
        
        return calculate_score(scan_id, db)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating score: {str(e)}"
        )

@router.post("/rescore/{scan_id}")
def force_rescore(scan_id: str, db: Session = Depends(get_db)):
    """Force re-generation of score with latest analysis logic (including IP reputation)."""
    try:

        return calculate_score(scan_id, db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error rescoring: {str(e)}"
        )


@router.get("/get_score/{scan_id}")
def get_score(scan_id: str, db: Session = Depends(get_db)):
    score = db.query(ScanSummary).filter(
        ScanSummary.scan_id == scan_id
    ).first()
    if not score:
        raise HTTPException(
            status_code=404,
            detail="Score not found. Generate it first."
        )
    return {
        "scan_id": score.scan_id,
        "domain_score": score.domain_score,
        "host": {
            "domain": score.domain,
            "mail_security": score.mail_security or {}
        },
        "severity": score.severity,
        "categorized_vulnerabilities": build_categorized_vulnerabilities(score),
        "ips": score.ips or []
    }

@router.get("/get_raw_data/{scan_id}")
def get_raw_data(scan_id: str, db: Session = Depends(get_db)):
    score = db.query(ScanResult).filter(
        ScanResult.scan_id == scan_id
    ).first()
    if not score:
        raise HTTPException(
            status_code=404,
            detail="Raw data not found. Generate it first."
        )
    return score.results

@router.get("/get_all")
def get_all_scores(db: Session = Depends(get_db)):
    scores = db.query(ScanResult).all()
    return [score.scan_id for score in scores]