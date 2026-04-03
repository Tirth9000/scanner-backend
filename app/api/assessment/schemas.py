from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class SubmitAnswer(BaseModel):
    questionId: str
    selectedOption: Literal["A", "B", "C", "D"]

class SubmitAssessmentBody(BaseModel):
    answers: List[SubmitAnswer]