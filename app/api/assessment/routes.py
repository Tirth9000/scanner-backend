from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models import User, AssessmentResult
from app.core.middleware import protect
from app.db.base import get_db
from app.api.assessment.schemas import SubmitAssessmentBody
from app.api.assessment.controller import (
    submit_assessment_logic,
    get_latest_assessment
)

router = APIRouter(prefix="/api/assess", tags=["assessment"])


@router.post("/")
async def submit_assessment(
    body: SubmitAssessmentBody,
    db: Session = Depends(get_db),
    user: User = Depends(protect)
):
    user_id = user.user_id
    result = submit_assessment_logic(body, user_id, db)

    return {
        "success": True,
        "resultId": str(result._id),
        "userId": str(result.user_id),
        "data": {
            "_id": str(result._id),
            "summary": result.summary,
            "answers": result.answers,
            "created_at": result.created_at.isoformat(),
        },
    }


@router.get("/latest")
async def get_latest_assessment_result(
    db: Session = Depends(get_db),
    user: User = Depends(protect)
):
    result = get_latest_assessment(user.user_id, db)

    return {
        "_id": str(result._id),
        "summary": result.summary,
        "answers": result.answers,
        "created_at": result.created_at.isoformat(),
    }