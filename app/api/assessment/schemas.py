from pydantic import BaseModel, Field
from typing import List, Optional,Literal


class Summary(BaseModel):
    score: Optional[float] = None
    total_questions: Optional[int] = None
    max_possible_score: Optional[float] = None
    percentage: Optional[float] = None
    grade: Optional[str] = None
    risk_level: Optional[str] = None
    risk_color: Optional[str] = None


class SelectedOption(BaseModel):
    option_key: Optional[str] = None
    option_text: Optional[str] = None
    score: Optional[float] = None


class Answer(BaseModel):
    questionId: Optional[str] = None
    questionText: Optional[str] = None
    selectedOption: Optional[SelectedOption] = None
    pointsAwarded: Optional[float] = None


class AssessmentResult(BaseModel):
    summary: Summary
    answers: List[Answer]


class SubmitAnswer(BaseModel):
    questionId: str
    selectedOption: Literal["A", "B", "C", "D"]

class SubmitAssessmentBody(BaseModel):
    answers: List[SubmitAnswer]