from ..ai.gemini import Gemini
from ..models.quiz import QuizRequest, QuizResponse
from ..models.question import Question
import json
import re

class QuizGenerator:
    def __init__(self, gemini: Gemini):
        self.gemini = gemini
    
    def generate(self, request: QuizRequest) -> QuizResponse:
        """
        Generate a complete quiz with multiple questions
        """
        prompt = self._build_prompt(request)
        response = self.gemini.generate_response(prompt)
        
        cleaned_response = ""
        
        try:
            cleaned_response = self._clean_json_response(response)
            quiz_data = json.loads(cleaned_response)
            return QuizResponse(**quiz_data)
        except json.JSONDecodeError as e:
            # Fallback: extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                try:
                    cleaned_json = self._clean_json_response(json_match.group(1))
                    quiz_data = json.loads(cleaned_json)
                    return QuizResponse(**quiz_data)
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
    
    def _build_prompt(self, request: QuizRequest) -> str:
        """
        Build detailed prompt for quiz generation
        """
        # Default difficulty distribution if not provided
        if request.difficulty_distribution:
            easy_percent = request.difficulty_distribution.easy / 100
            medium_percent = request.difficulty_distribution.medium / 100
            hard_percent = request.difficulty_distribution.hard / 100
        else:
            easy_percent = 0.3
            medium_percent = 0.5
            hard_percent = 0.2
        
        # Calculate number of questions per difficulty
        easy_count = int(request.question_count * easy_percent)
        medium_count = int(request.question_count * medium_percent)
        hard_count = request.question_count - easy_count - medium_count
        
        prompt = f"""Tạo bài kiểm tra/quiz môn Toán với thông tin sau:

**Thông tin chung:**
- Tiêu đề: {request.title}
- Chủ đề: {request.topic}
- Cấp học: {request.grade_level}
- Thời gian: {request.duration} phút
- Tổng số câu: {request.question_count}

**Phân bố độ khó:**
- Dễ: {easy_count} câu ({easy_percent*100:.0f}%)
- Trung bình: {medium_count} câu ({medium_percent*100:.0f}%)
- Khó: {hard_count} câu ({hard_percent*100:.0f}%)

**Yêu cầu:**
1. Tạo câu hỏi đa dạng (trắc nghiệm, tự luận ngắn)
2. Mỗi câu có điểm phù hợp với độ khó (dễ: 1-2đ, TB: 3-4đ, khó: 5-6đ)
3. Bao gồm lời giải chi tiết cho từng câu
4. Sử dụng LaTeX cho công thức toán học
5. Câu hỏi theo thứ tự từ dễ đến khó
6. Phù hợp với trình độ học sinh cấp {request.grade_level}

**Format JSON trả về:**
{{
    "title": "{request.title}",
    "topic": "{request.topic}",
    "grade_level": "{request.grade_level}",
    "duration": {request.duration},
    "total_points": tổng_điểm,
    "instructions": "Hướng dẫn làm bài cho học sinh",
    "questions": [
        {{
            "question_text": "Câu hỏi (dùng LaTeX: $...$)",
            "question_type": "multiple_choice" hoặc "short_answer" hoặc "essay",
            "choices": [
                {{"id": "A", "text": "Đáp án A", "is_correct": false}},
                {{"id": "B", "text": "Đáp án B", "is_correct": true}},
                {{"id": "C", "text": "Đáp án C", "is_correct": false}},
                {{"id": "D", "text": "Đáp án D", "is_correct": false}}
            ],
            "correct_answer": "B" hoặc "đáp án đúng",
            "solution": "Lời giải chi tiết từng bước",
            "difficulty": "easy" hoặc "medium" hoặc "hard",
            "points": điểm_số,
            "tags": ["tag1", "tag2"]
        }}
    ]
}}

**Lưu ý quan trọng:**
- Công thức toán: $x^2$, $\\frac{{a}}{{b}}$, $\\sqrt{{x}}$
- Lời giải phải có các bước rõ ràng
- Câu trắc nghiệm: 4 đáp án, 1 đúng
- Câu tự luận: có rubric chấm điểm
- Tổng điểm = tổng điểm các câu
"""
        
        return prompt
    
    def _calculate_points_distribution(self, request: QuizRequest) -> dict:
        """
        Calculate points for each difficulty level
        """
        if request.difficulty_distribution:
            easy_percent = request.difficulty_distribution.easy / 100
            medium_percent = request.difficulty_distribution.medium / 100
            hard_percent = request.difficulty_distribution.hard / 100
        else:
            easy_percent = 0.3
            medium_percent = 0.5
            hard_percent = 0.2
        
        easy_count = int(request.question_count * easy_percent)
        medium_count = int(request.question_count * medium_percent)
        hard_count = request.question_count - easy_count - medium_count
        
        return {
            "easy": {"count": easy_count, "points_per_question": 1},
            "medium": {"count": medium_count, "points_per_question": 3},
            "hard": {"count": hard_count, "points_per_question": 5}
        }