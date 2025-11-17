from ..ai.gemini import Gemini
from ..models.lesson_plan import LessonPlanRequest, LessonPlanResponse
import json
import re

class LessonPlanGenerator:
    def __init__(self, gemini: Gemini):
        self.gemini = gemini
    
    def generate(self, request: LessonPlanRequest) -> LessonPlanResponse:
        prompt = self._build_prompt(request)
        response = self.gemini.generate_response(prompt)
        
        cleaned_response = ""
        
        # Parse JSON response from AI
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = self._clean_json_response(response)
            
            # Try to parse the cleaned response
            lesson_data = json.loads(cleaned_response)
            return LessonPlanResponse(**lesson_data)
        except json.JSONDecodeError as e:
            # Fallback: extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                try:
                    cleaned_json = self._clean_json_response(json_match.group(1))
                    lesson_data = json.loads(cleaned_json)
                    return LessonPlanResponse(**lesson_data)
                except json.JSONDecodeError:
                    pass
            
            # Log the error for debugging
            print(f"JSON Decode Error: {e}")
            print(f"Response (first 1000 chars): {response[:1000]}...")
            if cleaned_response:
                print(f"Cleaned response (first 500 chars): {cleaned_response[:500]}...")
            raise ValueError(f"Unable to parse AI response. JSON error: {str(e)}")
    
    def _clean_json_response(self, text: str) -> str:
        """Clean and fix common JSON issues from AI responses"""
        # Remove markdown code blocks
        cleaned = text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]  # Remove ```json
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]   # Remove ```
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]  # Remove trailing ```
        
        cleaned = cleaned.strip()
        
        # Fix common LaTeX escape issues in JSON strings
        # Replace single backslashes with double backslashes for LaTeX
        # But be careful not to break already escaped characters
        # This is a simplified approach - the prompt should handle this better
        
        return cleaned
    
    def _build_prompt(self, request: LessonPlanRequest) -> str:
        objectives_text = ""
        if request.objectives:
            objectives_text = "\nMục tiêu cụ thể:\n" + "\n".join(f"- {obj}" for obj in request.objectives)
        
        additional = ""
        if request.additional_requirements:
            additional = f"\n\nYêu cầu bổ sung: {request.additional_requirements}"
        
        return f"""Tạo giáo án môn Toán chi tiết với thông tin sau:
- Chủ đề: {request.topic}
- Cấp học: {request.grade_level.value}
- Thời lượng: {request.duration} phút{objectives_text}{additional}

Trả về kết quả dưới dạng JSON với cấu trúc sau:
{{
    "topic": "tên chủ đề",
    "grade_level": "cấp học",
    "duration": thời_lượng,
    "objectives": ["mục tiêu 1", "mục tiêu 2"],
    "materials": ["dụng cụ 1", "dụng cụ 2"],
    "sections": [
        {{
            "title": "Khởi động",
            "duration": 10,
            "content": "nội dung chi tiết",
            "activities": ["hoạt động 1", "hoạt động 2"]
        }}
    ],
    "assessment": "phương pháp đánh giá",
    "homework": "bài tập về nhà",
    "notes": "ghi chú cho giáo viên"
}}

Lưu ý: 
- Sử dụng LaTeX cho công thức toán (VD: $x^2 + y^2 = z^2$)
- Phù hợp với trình độ học sinh
- Bao gồm ví dụ minh họa cụ thể"""