import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models.lesson_plan import LessonPlanRequest, LessonPlanResponse
from .models.question import QuestionRequest, QuestionResponse
from .models.quiz import QuizRequest, QuizResponse
from .models.chat import ChatRequest, ChatResponse
from .services.lesson_generator import LessonPlanGenerator
from .services.question_generator import QuestionGenerator
from .services.quiz_generator import QuizGenerator
from .services.chat_service import ChatService
from .ai.gemini import Gemini

load_dotenv()

app = FastAPI(
    title="Math AI Learning Platform - AI Service",
    description="AI service for generating lesson plans, questions, and quizzes",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load prompts
def load_prompt(prompt_type: str = "default"):
    prompt_path = f"src/prompts/{prompt_type}_prompt.md"
    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return None

def get_gemini_instance(prompt_type: str = "default"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured"
        )
    system_prompt = load_prompt(prompt_type)
    return Gemini(api_key=api_key, system_prompt=system_prompt) # type: ignore

# === Endpoints ===

@app.get("/")
async def root():
    return {
        "success": True,
        "data": {
            "service": "Math AI Learning Platform - AI Service",
            "version": "1.0.0",
            "endpoints": {
                "chat": "/api/v1/chat",
                "lesson_plan": "/api/v1/generate/lesson-plan",
                "questions": "/api/v1/generate/questions",
                "quiz": "/api/v1/generate/quiz"
            }
        }
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat with AI assistant about the Math Learning Platform
    
    - **message**: User's message/question
    - **conversation_id**: Optional conversation ID for context
    - **user_role**: User role (teacher, student, admin, or user)
    
    The AI can help with:
    - Platform overview and features
    - How to use different functionalities
    - Math education tips and guidance
    - General questions about the system
    - Role-specific assistance
    """
    try:
        print(f"[DEBUG] Chat request from {request.user_role}: {request.message[:50]}...")
        gemini = get_gemini_instance("default")
        chat_service = ChatService(gemini)
        result = chat_service.chat(request)
        print("[DEBUG] Chat response generated successfully")
        return result
    except Exception as e:
        print(f"[ERROR] Chat failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate/lesson-plan")
async def generate_lesson_plan(request: LessonPlanRequest):
    """
    Generate a detailed lesson plan for math topics
    
    - **topic**: Math topic (e.g., "Phép cộng", "Phân số")
    - **grade_level**: elementary, middle, or high
    - **duration**: Lesson duration in minutes (30-90)
    - **objectives**: Optional list of learning objectives
    - **additional_requirements**: Optional additional requirements
    """
    try:
        print(f"[DEBUG] Received request: topic={request.topic}, grade_level={request.grade_level}, duration={request.duration}")
        gemini = get_gemini_instance("lesson_plan")
        generator = LessonPlanGenerator(gemini)
        print("[DEBUG] Starting generation...")
        result = generator.generate(request)
        print("[DEBUG] Generation completed successfully")
        return result.model_dump()
    except Exception as e:
        print(f"[ERROR] Generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate/questions")
async def generate_questions(request: QuestionRequest):
    """
    Generate math questions
    
    - **topic**: Math topic
    - **grade_level**: Grade level (1-12)
    - **question_type**: Type of question (multiple_choice, true_false, short_answer, essay)
    - **difficulty**: easy, medium, or hard
    - **count**: Number of questions (1-20)
    - **include_solution**: Include solution (default: true)
    """
    try:
        print(f"[DEBUG] Generating {request.count} questions for topic: {request.topic}, grade: {request.grade_level}")
        gemini = get_gemini_instance("question_generator")
        generator = QuestionGenerator(gemini)
        result = generator.generate(request)
        print(f"[DEBUG] Generated {len(result.questions)} questions successfully")
        return result.model_dump()
    except Exception as e:
        print(f"[ERROR] Question generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate/quiz")
async def generate_quiz(request: QuizRequest):
    """
    Generate a complete quiz/test
    
    - **title**: Quiz title
    - **topic**: Math topic
    - **grade_level**: Grade level (1-12 or elementary/middle/high)
    - **duration**: Time limit in minutes (10-120)
    - **question_count**: Number of questions (5-50)
    - **difficulty_distribution**: Optional difficulty distribution (default: easy 30%, medium 50%, hard 20%)
    - **include_essay**: Include essay questions (default: false)
    """
    try:
        print(f"[DEBUG] Generating quiz: {request.title}, {request.question_count} questions")
        gemini = get_gemini_instance("quiz_generator")
        generator = QuizGenerator(gemini)
        result = generator.generate(request)
        print(f"[DEBUG] Quiz generated successfully with {len(result.questions)} questions")
        return result.model_dump()
    except Exception as e:
        print(f"[ERROR] Quiz generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}