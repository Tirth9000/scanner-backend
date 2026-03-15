from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.api.assessment.schemas import SubmitAssessmentBody
from app.api.assessment.controller import submit_assessment_logic, get_latest_assessment


router = APIRouter(prefix="/api/assess", tags=["assessment"])

@router.post("/")
async def submit_assessment(
    body: SubmitAssessmentBody,
    db: Session = Depends(get_db)
):

    result = await submit_assessment_logic(body, db)

    return {
        "success": True,
        "resultId": str(result._id),
        "data": {
            "_id": str(result._id),
            "summary": result.summary,
            "answers": result.answers,
            "created_at": result.created_at.isoformat(),
        },
    }

@router.get("/latest")
async def get_latest_assessment_result(
    db: Session = Depends(get_db)
):
    result = await get_latest_assessment(db)
    return {
        "_id": str(result._id),
        "summary": result.summary,
        "answers": result.answers,
        "created_at": result.created_at.isoformat(),
    }