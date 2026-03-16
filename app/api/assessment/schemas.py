from pydantic import BaseModel, Field
from typing import List, Optional


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
    quotation: Optional[str] = None


class AssessmentResult(BaseModel):
    summary: Summary
    answers: List[Answer]


class SubmitAnswer(BaseModel):
    questionId: str
    selectedOption: int = Field(
        ge=0,
        le=3,
        description="Option index: 0, 1, 2, or 3"
    )
    quotation: Optional[str] = None


class SubmitAssessmentBody(BaseModel):
    answers: List[SubmitAnswer]