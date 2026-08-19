import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import pdfplumber
import uuid
from dotenv import load_dotenv
from backend.rag.question_generator import generate_questions

load_dotenv()

# ─────────────────────────────────────────────
# Auto ingest books on startup
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(os.getenv("CHROMA_DB_PATH", "./chroma_db")):
        print("ChromaDB not found — running ingestion...")
        from backend.rag.ingest import load_documents, chunk_documents, store_in_vectordb
        docs = load_documents("./data")
        if docs:
            chunks = chunk_documents(docs)
            store_in_vectordb(chunks)
            print("Ingestion complete!")
        else:
            print("No books found in /data folder!")
    else:
        print("ChromaDB already exists — skipping ingestion.")
    yield

app = FastAPI(title="AI Interview System", lifespan=lifespan)

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────
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
# ROUTE 2 — Start interview
# ─────────────────────────────────────────────
@app.post("/start-interview")
async def start_interview(
    file: UploadFile = File(...),
    role: str = Form(...)
):
    contents = await file.read()
    with open("temp_resume.pdf", "wb") as f:
        f.write(contents)

    resume_text = ""
    with pdfplumber.open("temp_resume.pdf") as pdf:
        for page in pdf.pages:
            resume_text += page.extract_text() or ""

    if not resume_text.strip():
        return {"error": "Could not extract text from resume."}

    questions = generate_questions(
        resume_text=resume_text,
        role=role,
        num_questions=5
    )

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
# ROUTE 3 — Submit answer
# ─────────────────────────────────────────────
@app.post("/submit-answer")
def submit_answer(request: AnswerRequest):
    session = sessions.get(request.session_id)
    if not session:
        return {"error": "Session not found."}

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
# ROUTE 4 — Get summary
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