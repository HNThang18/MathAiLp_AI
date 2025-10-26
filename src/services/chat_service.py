from ..ai.gemini import Gemini
from ..models.chat import ChatRequest, ChatResponse
from datetime import datetime
import uuid

class ChatService:
    def __init__(self, gemini: Gemini):
        self.gemini = gemini
        
    def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Handle chat conversation with AI
        """
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:12]}"
        
        # Build context-aware prompt
        prompt = self._build_prompt(request)
        
        # Get AI response
        ai_message = self.gemini.generate_response(prompt)
        
        # Create response
        response = ChatResponse(
            message=ai_message,
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat()
        )
        
        return response
    
    def _build_prompt(self, request: ChatRequest) -> str:
        """
        Build prompt with context about the platform
        """
        user_context = ""
        if request.user_role == "teacher":
            user_context = "\n(Người dùng là giáo viên)"
        elif request.user_role == "student":
            user_context = "\n(Người dùng là học sinh)"
        elif request.user_role == "admin":
            user_context = "\n(Người dùng là quản trị viên)"
        
        return f"{request.message}{user_context}"