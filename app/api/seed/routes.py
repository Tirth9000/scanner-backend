from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
import os
import json

from app.db.base import get_db
from app.db.models import Question

router = APIRouter(prefix="/api/seed", tags=["insert_questions"])


def seed_questions_data(db: Session):
    try:
        count = db.query(Question).count()

        if count > 0:
            return (False, "Questions already exist — seeding skipped", count)

        app_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )
        data_path = os.path.join(app_dir, "data", "questionsData.json")

        with open(data_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        question_objects = []

        for q in questions:
            question = Question(
                _id=q["id"],
                category_id=q["category_id"],
                category_name=q["category_name"],
                question_text=q["question_text"],
                options=q["options"]
            )
            question_objects.append(question)

        db.bulk_save_objects(question_objects)
        db.commit()

        return (True, "Questions seeded successfully", len(questions))

    except Exception as e:
        db.rollback()
        print(f"Error seeding questions: {e}")
        raise


@router.post("/")
def seed_questions(db: Session = Depends(get_db)):
    try:
        success, message, count = seed_questions_data(db)
        status_code = 201 if success else 200
        return JSONResponse(
            status_code=status_code,
            content={
                "message": message,
                "count": count,
            },
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Server Error")