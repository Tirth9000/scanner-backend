from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from app.api.analyzer.shemas import ScanScoreResponse
from app.db.base import get_db
from app.api.analyzer.controller import calculate_score
from app.db.models import ScanSummary,ScanResult
from sqlalchemy.orm import Session
router = APIRouter(prefix="/score",tags=["Scoring"])

@router.post("/{scan_id}")
def generate_score(scan_id: str, db: Session = Depends(get_db)):
    try:
        scans = db.query(ScanSummary).filter(ScanSummary.scan_id == scan_id).first()

        if scans:
            # Check if this is a stale cache (missing IP reputation data)
            has_ip_reputation = False
            if scans.categorized_vulnerabilities:
                has_ip_reputation = "IP Reputation" in scans.categorized_vulnerabilities
            
            if has_ip_reputation:
                print("Score already exists for scan_id:", scan_id)
                return {
                    "scan_id": scans.scan_id,
                    "domain_score": scans.domain_score,
                    "category_scores": scans.category_scores or {},
                    "host": {},
                    "severity": scans.severity,
                    "categorized_vulnerabilities": scans.categorized_vulnerabilities,
                    "ips": scans.ips or []
                }
            else:
                # Stale cache — re-generate with IP reputation, db.merge will handle updates safely
                print("Stale cache detected for scan_id:", scan_id, "- re-generating with IP reputation")
        

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
    return score

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