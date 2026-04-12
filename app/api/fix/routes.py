import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.redis_queue import RedisClient
from app.core.middleware import protect
from app.db.base import get_db
from app.api.fix.schemas import FixRequest, FixSubmitResponse, FixResultRequest, FixResultResponse
from app.api.fix.service import apply_fix_result

router = APIRouter(prefix="/fix", tags=["Fix"])

redis_client = RedisClient()
QUEUE_NAME = "fix_queue"


@router.post("/submit", response_model=FixSubmitResponse)
def submit_fix(request: FixRequest, db: Session = Depends(get_db)):
    try:
        job_data = request.model_dump()
        job_data["scan_id"] = job_data["org_id"]
        redis_client.redis.rpush(QUEUE_NAME, json.dumps(job_data))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Redis connection failed. Please try again later."
        )

    return FixSubmitResponse(
        message="Fix request queued successfully",
        org_id=request.org_id,
    )


@router.post("/result", response_model=FixResultResponse)
def submit_fix_result(request: FixResultRequest, db: Session = Depends(get_db)):
    try:
        fix_result = apply_fix_result(
            org_id=request.scan_id,
            domain=request.domain,
            fix_type=request.fix_type,
            result=request.result,
            db=db,
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update scan summary after fix result"
        )

    return FixResultResponse(
        message="Fix result stored successfully",
        org_id=request.scan_id,
        domain_score=fix_result["domain_score"],
        severity=fix_result["severity"],
    )
