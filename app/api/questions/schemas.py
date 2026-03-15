from pydantic import BaseModel
from typing import List

class Option(BaseModel):
    option_key: str
    option_text: str
    score: int

class Question(BaseModel):
    id: int
    category_id: int
    category_name: str
    question_text: str
    options: List[Option]