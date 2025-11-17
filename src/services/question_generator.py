from ..ai.gemini import Gemini
from ..models.question import QuestionRequest, QuestionResponse, Question
import json
import re

class QuestionGenerator:
    def __init__(self, gemini: Gemini):
        self.gemini = gemini
    
    def generate(self, request: QuestionRequest) -> QuestionResponse:
        prompt = self._build_prompt(request)
        response = self.gemini.generate_response(prompt)
        
        cleaned_response = ""
        
        try:
            cleaned_response = self._clean_json_response(response)
            questions_data = json.loads(cleaned_response)
            return QuestionResponse(**questions_data)
        except json.JSONDecodeError as e:
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                try:
                    cleaned_json = self._clean_json_response(json_match.group(1))
                    questions_data = json.loads(cleaned_json)
                    return QuestionResponse(**questions_data)
                except json.JSONDecodeError:
                    pass
            
            print(f"JSON Decode Error: {e}")
            print(f"Response (first 1000 chars): {response[:1000]}...")
            if cleaned_response:
                print(f"Cleaned response (first 500 chars): {cleaned_response[:500]}...")
            raise ValueError(f"Unable to parse AI response. JSON error: {str(e)}")
    
    def _clean_json_response(self, text: str) -> str:
        """Clean and fix common JSON issues from AI responses"""
        cleaned = text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
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