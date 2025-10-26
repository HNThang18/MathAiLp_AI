from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message/question", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_role: Optional[str] = Field("user", description="User role: teacher, student, or admin")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Math Learning Platform là gì?",
                "conversation_id": None,
                "user_role": "user"
            }
        }

class ChatResponse(BaseModel):
    message: str = Field(..., description="AI's response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: str = Field(..., description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Math Learning Platform là nền tảng học toán...",
                "conversation_id": "conv_123456",
                "timestamp": "2025-10-24T10:30:00"
            }
        }