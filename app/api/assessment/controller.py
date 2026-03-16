from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Question, AssessmentResult


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


async def submit_assessment_logic(body, db: Session):
    answers = body.answers
    questions = db.query(Question).all()
    if not questions:
        raise HTTPException(status_code=500, detail="No questions found")

    questionMap = {
        str(q._id): {
            "_id": q._id,
            "question_text": q.question_text,
            "options": q.options or [],
        }
        for q in questions
    }

    totalScore = 0
    maxPossibleScore = 0
    processedAnswers = []

    for ans in answers:

        qid = ans.questionId
        question = questionMap.get(qid)

        if not question:
            continue

        options = question["options"]
        idx = ans.selectedOption

        if idx < 0 or idx >= len(options):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid option {idx} for question {qid}"
            )

        selectedOption = options[idx]

        points = int(selectedOption.get("score", 0))

        totalScore += points
        maxPossibleScore += 3

        processedAnswers.append(
            {
                "questionId": str(question["_id"]),
                "questionText": question["question_text"],
                "selectedOption": selectedOption,
                "pointsAwarded": points,
                "quotation": ans.quotation,
            }
        )

    percentage = round(
        (totalScore / maxPossibleScore) * 100
    ) if maxPossibleScore > 0 else 0

    grade = calculateGrade(percentage)
    risk = mapGradeToRisk(grade)
    color = mapRiskToColor(risk)

    summary = {
        "score": totalScore,
        "total_questions": len(processedAnswers),
        "max_possible_score": maxPossibleScore,
        "percentage": percentage,
        "grade": grade,
        "risk_level": risk,
        "risk_color": color,
    }

    new_result = AssessmentResult(
        summary=summary,
        answers=processedAnswers,
    )

    db.add(new_result)
    db.commit()
    db.refresh(new_result)

    return new_result


async def get_latest_assessment(db: Session):
    result = (
        db.query(AssessmentResult)
        .order_by(AssessmentResult.created_at.desc())
        .first()
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No assessment results found"
        )
    return result