from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionRequest(BaseModel):
    topic: str = Field(..., description="Chủ đề câu hỏi")
    grade_level: str = Field(..., description="Cấp học (1-12)")
    question_type: QuestionType
    difficulty: DifficultyLevel
    count: int = Field(1, ge=1, le=20, description="Số lượng câu hỏi")
    include_solution: bool = Field(True, description="Bao gồm lời giải")

class Choice(BaseModel):
    id: str
    text: str
    is_correct: bool

class Question(BaseModel):
    question_text: str
    question_type: str
    choices: Optional[List[Choice]] = None
    correct_answer: str
    solution: Optional[str] = None
    difficulty: str
    tags: List[str]

class QuestionResponse(BaseModel):
    questions: List[Question]
    topic: str
    grade_level: str