from fastapi import APIRouter, HTTPException,Depends
from fastapi.responses import JSONResponse
import json
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.base import get_db
from app.db.models import Question

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/")
def get_questions(db: Session = Depends(get_db)):
    try:
        questions = (
            db.query(Question)
            .order_by(Question._id.asc())
            .all()
        )
        return [
            {
                "_id": q._id,
                "category_id": q.category_id,
                "category_name": q.category_name,
                "question_text": q.question_text,
                "options": q.options,
            }
            for q in questions
        ]
    except Exception as e:
        print("FETCH QUESTIONS ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch questions")