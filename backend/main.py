import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pdfplumber
import uuid
from dotenv import load_dotenv
from backend.rag.question_generator import generate_questions

load_dotenv()

app = FastAPI(title="AI Interview System")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions = {}


class AnswerRequest(BaseModel):
    session_id: str
    question: str
    answer: str


# ─────────────────────────────────────────────
# ROUTE 1 — Health check
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "AI Interview System is running!"}


# ─────────────────────────────────────────────
# ROUTE 2 — Upload resume and start interview
# ─────────────────────────────────────────────
@app.post("/start-interview")
async def start_interview(
    file: UploadFile = File(...),
    role: str = Form(...)
):
    # Extract text from uploaded resume PDF
    contents = await file.read()
    with open("temp_resume.pdf", "wb") as f:
        f.write(contents)

    resume_text = ""
    with pdfplumber.open("temp_resume.pdf") as pdf:
        for page in pdf.pages:
            resume_text += page.extract_text() or ""

    if not resume_text.strip():
        return {"error": "Could not extract text from resume."}

    # Generate questions using RAG pipeline
    questions = generate_questions(
        resume_text=resume_text,
        role=role,
        num_questions=5
    )

    # Create a session
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "role": role,
        "resume_text": resume_text[:500],
        "questions": questions,
        "answers": [],
        "current_question": 0
    }

    return {
        "session_id": session_id,
        "role": role,
        "first_question": questions[0] if questions else "No questions generated.",
        "total_questions": len(questions)
    }


# ─────────────────────────────────────────────
# ROUTE 3 — Submit answer, get next question
# ─────────────────────────────────────────────
@app.post("/submit-answer")
def submit_answer(request: AnswerRequest):
    session = sessions.get(request.session_id)
    if not session:
        return {"error": "Session not found."}

    # Save the answer
    session["answers"].append({
        "question": request.question,
        "answer": request.answer
    })
    session["current_question"] += 1

    current = session["current_question"]
    questions = session["questions"]

    if current >= len(questions):
        return {
            "status": "completed",
            "message": "Interview complete!",
            "next_question": None
        }

    return {
        "status": "ongoing",
        "next_question": questions[current],
        "question_number": current + 1,
        "total_questions": len(questions)
    }


# ─────────────────────────────────────────────
# ROUTE 4 — Get final summary
# ─────────────────────────────────────────────
@app.get("/summary/{session_id}")
def get_summary(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found."}

    return {
        "role": session["role"],
        "total_questions": len(session["questions"]),
        "total_answered": len(session["answers"]),
        "qa_pairs": session["answers"]
    }