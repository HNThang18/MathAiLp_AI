from pydantic import BaseModel, Field
from typing import List, Optional
from .question import Question

class QuizRequest(BaseModel):
    title: str = Field(..., description="Tên bài kiểm tra")
    topic: str = Field(..., description="Chủ đề")
    grade_level: str = Field(..., description="Cấp học (1-12 hoặc elementary/middle/high)")
    duration: int = Field(..., description="Thời gian làm bài (phút)", ge=10, le=120)
    question_count: int = Field(..., description="Số câu hỏi", ge=5, le=50)
    difficulty_distribution: Optional[dict] = Field(
        default=None,
        description="Phân bố độ khó (VD: {'easy': 0.3, 'medium': 0.5, 'hard': 0.2})"
    )
    include_essay: bool = Field(
        default=False,
        description="Bao gồm câu tự luận"
    )

class QuizQuestion(BaseModel):
    """Extended Question model with points"""
    question_text: str
    question_type: str
    choices: Optional[List[dict]] = None
    correct_answer: str
    solution: str
    difficulty: str
    points: int = Field(..., description="Điểm số câu hỏi")
    tags: List[str]

class QuizResponse(BaseModel):
    title: str
    topic: str
    grade_level: str
    duration: int
    total_points: int
    questions: List[QuizQuestion]
    instructions: str = Field(
        ...,
        description="Hướng dẫn làm bài"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Kiểm tra Toán - Phép cộng và trừ",
                "topic": "Phép cộng và trừ",
                "grade_level": "3",
                "duration": 45,
                "total_points": 10,
                "instructions": "Học sinh làm bài trong 45 phút...",
                "questions": [
                    {
                        "question_text": "Tính: $12 + 8 = ?$",
                        "question_type": "multiple_choice",
                        "choices": [
                            {"id": "A", "text": "18", "is_correct": False},
                            {"id": "B", "text": "20", "is_correct": True},
                            {"id": "C", "text": "22", "is_correct": False},
                            {"id": "D", "text": "24", "is_correct": False}
                        ],
                        "correct_answer": "B",
                        "solution": "12 + 8 = 20",
                        "difficulty": "easy",
                        "points": 1,
                        "tags": ["phép cộng", "số tự nhiên"]
                    }
                ]
            }
        }