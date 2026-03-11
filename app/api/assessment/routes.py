from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import Response
import json
from app.api.assessment.schemas import SubmitAssessmentBody
from app.core.middleware import protect
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import Question, AssessmentResult
from app.utils.generate_assessment_pdf import generate_assessment_pdf_bytes


router = APIRouter(prefix="/api/assess", tags=["assessment"])


def calculateGrade(percentage: int) -> str:
    if percentage >= 90:
        return "A"
    if percentage >= 80:
        return "B"
    if percentage >= 70:
        return "C"
    if percentage >= 60:
        return "D"
    return "F"


def mapGradeToRisk(grade: str) -> str:
    if grade == "A":
        return "Secure"
    if grade == "B":
        return "Low"
    if grade == "C":
        return "Medium"
    if grade == "D":
        return "High"
    if grade == "F":
        return "Critical"
    return "Unknown"


def mapRiskToColor(risk: str) -> str:
    if risk in ("Secure", "Low"):
        return "green"
    if risk == "Medium":
        return "yellow"
    if risk in ("High", "Critical"):
        return "red"
    return "gray"

@router.post("/")
def submit_assessment(
    body: SubmitAssessmentBody,
    user: dict = Depends(protect),
    db: Session = Depends(get_db),
):
    try:
        answers = body.answers
        if not isinstance(answers, list) or len(answers) == 0:
            raise HTTPException(status_code=400, detail="Invalid answers payload")

        questions = db.query(Question).all()

        if not questions:
            raise HTTPException(status_code=500, detail="No questions found")
        questionMap = {
            str(q._id): {
                "_id": q._id,
                "category_name": q.category_name,
                "question_text": q.question_text,
                "options": q.options or [],
            }
            for q in questions
        }

        totalScore = 0
        maxPossibleScore = 0
        categoryTracker = {}
        processedAnswers = []

        for q in questions:
            if q.category_name not in categoryTracker:
                categoryTracker[q.category_name] = {"score": 0, "max": 0}
            categoryTracker[q.category_name]["max"] += 3
            maxPossibleScore += 3
        for ans in answers:
            qid = ans.questionId

            if not isinstance(qid, str) or not qid.isdigit():
                raise HTTPException(
                    status_code=400,
                    detail="Invalid questionId payload",
                )

            question = questionMap.get(qid)
            if not question:
                continue
            options = question["options"]
            idx = ans.selectedOption
            if idx < 0 or idx >= len(options):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid selectedOption {idx} for question {qid}",
                )

            selectedOption = options[idx]
            points = int(selectedOption.get("score", 0))
            totalScore += points
            categoryTracker[question["category_name"]]["score"] += points

            processedAnswers.append(
                {
                    "questionId": question["_id"],
                    "questionText": question["question_text"],
                    "selectedOption": selectedOption,
                    "pointsAwarded": points,
                    "quotation": ans.quotation or None,
                }
            )

        # CATEGORY SCORES
        categoryScores = []
        for name, data in categoryTracker.items():
            percentage = round((data["score"] / data["max"]) * 100) if data["max"] > 0 else 0
            grade = calculateGrade(percentage)
            risk = mapGradeToRisk(grade)
            color = mapRiskToColor(risk)

            categoryScores.append(
                {
                    "category_name": name,
                    "score": data["score"],
                    "max_score": data["max"],
                    "percentage": percentage,
                    "grade": grade,
                    "risk": risk,
                    "color": color,
                }
            )

        overallPercentage = round((totalScore / maxPossibleScore) * 100) if maxPossibleScore > 0 else 0
        overallGrade = calculateGrade(overallPercentage)
        overallRisk = mapGradeToRisk(overallGrade)
        overallColor = mapRiskToColor(overallRisk)

        summary = {
            "score": totalScore,
            "total_questions": len(questions),
            "max_possible_score": maxPossibleScore,
            "percentage": overallPercentage,
            "grade": overallGrade,
            "risk_level": overallRisk,
            "risk_color": overallColor,
        }
        new_result = AssessmentResult(
            user_id=user["id"],
            summary=summary,
            category_scores=categoryScores,
            answers=processedAnswers,
        )

        db.add(new_result)
        db.commit()
        db.refresh(new_result)

        return {
            "success": True,
            "resultId": str(new_result._id),
            "data": {
                "_id": str(new_result._id),
                "user": user["id"],
                "summary": summary,
                "category_scores": categoryScores,
                "answers": processedAnswers,
                "created_at": new_result.created_at.isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        print("ASSESSMENT SUBMIT ERROR:", err)
        raise HTTPException(status_code=500, detail="Assessment submission failed")

@router.get("/history")
def history(
    user: dict = Depends(protect),
    db: Session = Depends(get_db),
):
    try:
        results = (
            db.query(AssessmentResult)
            .filter(AssessmentResult.user_id == user["id"])
            .order_by(AssessmentResult.created_at.desc())
            .all()
        )

        return [
            {
                "_id": str(r._id),
                "user": r.user_id,
                "summary": r.summary,
                "category_scores": r.category_scores,
                "answers": r.answers,
                "created_at": r.created_at.isoformat(),
            }
            for r in results
        ]

    except Exception as err:
        print("FETCH HISTORY ERROR:", err)
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@router.get("/{id}/download")
def download_pdf(
    id: str,
    user: dict = Depends(protect),
    db: Session = Depends(get_db),
):
    try:
        result = (
            db.query(AssessmentResult)
            .filter(AssessmentResult._id == id)
            .first()
        )

        if not result:
            raise HTTPException(status_code=404, detail="Assessment not found")

        if result.user_id != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

        assessment = {
            "_id": str(result._id),
            "user": result.user_id,
            "summary": result.summary,
            "category_scores": result.category_scores,
            "answers": result.answers,
            "created_at": result.created_at.isoformat(),
        }
        pdf_bytes = generate_assessment_pdf_bytes(assessment)
        filename = f"assessment-{assessment['_id']}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to generate PDF")