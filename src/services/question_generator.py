from ..ai.gemini import Gemini
from ..models.question import QuestionRequest, QuestionResponse, Question
import json

class QuestionGenerator:
    def __init__(self, gemini: Gemini):
        self.gemini = gemini
    
    def generate(self, request: QuestionRequest) -> QuestionResponse:
        prompt = self._build_prompt(request)
        response = self.gemini.generate_response(prompt)
        
        try:
            questions_data = json.loads(response)
            return QuestionResponse(**questions_data)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group(1))
                return QuestionResponse(**questions_data)
            raise ValueError("Unable to parse AI response")
    
    def _build_prompt(self, request: QuestionRequest) -> str:
        return f"""Tạo {request.count} câu hỏi môn Toán với thông tin:
- Chủ đề: {request.topic}
- Cấp học: {request.grade_level}
- Loại câu hỏi: {request.question_type.value}
- Độ khó: {request.difficulty.value}
- Có lời giải: {"Có" if request.include_solution else "Không"}

Trả về JSON:
{{
    "questions": [
        {{
            "question_text": "Câu hỏi (dùng LaTeX cho công thức)",
            "question_type": "{request.question_type.value}",
            "choices": [{{"id": "A", "text": "...", "is_correct": false}}],
            "correct_answer": "đáp án đúng",
            "solution": "lời giải chi tiết (nếu có)",
            "difficulty": "{request.difficulty.value}",
            "tags": ["tag1", "tag2"]
        }}
    ],
    "topic": "{request.topic}",
    "grade_level": "{request.grade_level}"
}}

Lưu ý:
- Câu hỏi phải phù hợp trình độ
- Sử dụng LaTeX: $...$
- Lời giải từng bước rõ ràng"""