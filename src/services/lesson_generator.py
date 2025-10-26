from ..ai.gemini import Gemini
from ..models.lesson_plan import LessonPlanRequest, LessonPlanResponse
import json

class LessonPlanGenerator:
    def __init__(self, gemini: Gemini):
        self.gemini = gemini
    
    def generate(self, request: LessonPlanRequest) -> LessonPlanResponse:
        prompt = self._build_prompt(request)
        response = self.gemini.generate_response(prompt)
        
        # Parse JSON response from AI
        try:
            lesson_data = json.loads(response)
            return LessonPlanResponse(**lesson_data)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                lesson_data = json.loads(json_match.group(1))
                return LessonPlanResponse(**lesson_data)
            raise ValueError("Unable to parse AI response")
    
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