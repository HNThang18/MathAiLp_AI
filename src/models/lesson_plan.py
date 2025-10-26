from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class GradeLevel(str, Enum):
    ELEMENTARY = "elementary"  # Cấp 1
    MIDDLE = "middle"          # Cấp 2
    HIGH = "high"              # Cấp 3

class LessonPlanRequest(BaseModel):
    topic: str = Field(..., description="Chủ đề bài học (VD: Phép cộng, Phân số)")
    grade_level: GradeLevel = Field(..., description="Cấp học")
    duration: int = Field(..., description="Thời lượng (phút)", ge=30, le=90)
    objectives: Optional[List[str]] = Field(None, description="Mục tiêu bài học")
    additional_requirements: Optional[str] = Field(None, description="Yêu cầu bổ sung")

class LessonSection(BaseModel):
    title: str
    duration: int
    content: str
    activities: List[str]

class LessonPlanResponse(BaseModel):
    topic: str
    grade_level: str
    duration: int
    objectives: List[str]
    materials: List[str]
    sections: List[LessonSection]
    assessment: str
    homework: Optional[str]
    notes: Optional[str]