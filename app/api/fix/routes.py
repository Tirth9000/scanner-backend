import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.redis_queue import RedisClient
from app.api.fix.schemas import FixRequest, FixResponse, FixResultRequest
from app.db.base import get_db
from app.db.models import Temp

router = APIRouter(prefix="/api/fix", tags=["Fix"])

redis_client = RedisClient()

QUEUE_NAME = "fix_queue"


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
        scan_id=request.scan_id
    )


@router.post("/result", response_model=FixResponse)
def submit_fix_result(request: FixResultRequest, db: Session = Depends(get_db)):
    try:
        fix_result = Temp(
            scan_id=request.scan_id,
            domain=request.domain,
            fix_type=request.fix_type,
            result=request.result
        )
        db.add(fix_result)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to store fix result"
        )

    return FixResponse(
        message="Fix result stored successfully",
        scan_id=request.scan_id
    )
