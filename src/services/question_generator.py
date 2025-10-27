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
            # Convert solution dict to string if needed
            questions_data = self._normalize_solutions(questions_data)
            return QuestionResponse(**questions_data)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group(1))
                # Convert solution dict to string if needed
                questions_data = self._normalize_solutions(questions_data)
                return QuestionResponse(**questions_data)
            raise ValueError("Unable to parse AI response")
    
    def _normalize_solutions(self, questions_data: dict) -> dict:
        """
        Convert solution dictionaries to formatted strings
        """
        if "questions" in questions_data:
            for question in questions_data["questions"]:
                if "solution" in question and isinstance(question["solution"], dict):
                    # Convert dict with steps to formatted string
                    steps = question["solution"]
                    solution_parts = []
                    
                    # Sort keys to maintain step order
                    sorted_keys = sorted(steps.keys())
                    for key in sorted_keys:
                        if key.startswith('step_') or key.startswith('Step'):
                            solution_parts.append(f"{steps[key]}")
                        elif key == 'answer' or key == 'final_answer':
                            solution_parts.append(f"Đáp án: {steps[key]}")
                        else:
                            solution_parts.append(f"{steps[key]}")
                    
                    # Join all parts with newlines
                    question["solution"] = "\n".join(solution_parts)
        
        return questions_data
    
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
            "solution": "lời giải chi tiết dưới dạng TEXT thuần túy. VD: Bước 1: ...\nBước 2: ...\nĐáp án: ...",
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
- Lời giải (solution) PHẢI là chuỗi text, KHÔNG ĐƯỢC là object/dictionary
- Lời giải từng bước rõ ràng, ngăn cách bởi xuống dòng"""