# 🤖 AI-Powered Role-Based Candidate Screening System

> An intelligent interview system that dynamically generates technical interview questions based on the candidate's resume and selected job role using RAG (Retrieval-Augmented Generation).

**Built by:** Nethula Shirisha  
**Assignment:** PGAGI AI/ML & Backend Engineering Internship  

---

## 📌 What This Project Does

- 📄 Reads the candidate's resume and extracts their skills and experience
- 🧠 Searches a knowledge base of ML textbooks using RAG
- ❓ Generates 5 smart, role-specific interview questions using Groq LLaMA
- 💬 Conducts the interview question by question
- 📊 Produces a final summary of all questions and answers

---

## 🏗️ System Architecture

```
Candidate → Upload Resume + Select Role
                    ↓
           Resume Parsing (pdfplumber)
                    ↓
         Build Query (Resume + Role)
                    ↓
     ChromaDB Similarity Search (RAG)
                    ↓
    Groq LLaMA Generates 5 Questions
                    ↓
       Angular Interview UI (Q&A)
                    ↓
          Final Summary Report
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Angular 16 |
| Backend | FastAPI (Python) |
| RAG Pipeline | LangChain + ChromaDB |
| LLM | Groq API — LLaMA 3.3 70B Versatile |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Vector DB | ChromaDB |
| PDF Parsing | pdfplumber |
| Version Control | Git + GitHub |

---

## 📁 Folder Structure

```
ai-interview-system/
├── backend/
│   ├── rag/
│   │   ├── ingest.py             ← loads ML books into ChromaDB
│   │   ├── retriever.py          ← searches vector database
│   │   └── question_generator.py ← generates questions via Groq
│   ├── api/
│   ├── models/
│   ├── utils/
│   └── main.py                   ← FastAPI server (4 endpoints)
├── frontend/                     ← Angular application
│   └── src/app/
│       ├── app.component.ts      ← main logic
│       ├── app.component.html    ← UI screens
│       ├── app.component.css     ← styling
│       └── services/
│           └── interview.service.ts ← API calls
├── data/                         ← ML textbook PDFs
├── .env                          ← API keys (not committed)
└── requirements.txt              ← Python dependencies
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js v18+
- Angular CLI 16
- Free Groq API key → [console.groq.com](https://console.groq.com)

---

### Backend Setup

**1. Clone the repository**
```bash
git clone https://github.com/shirisha0/ai-interview-systems.git
cd ai-interview-systems
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**3. Create `.env` file**
```env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_DB_PATH=./chroma_db
```

**4. Add ML books to `/data` folder**

Download any of these free ML books as PDFs and place them in the `/data` folder:
- Machine Learning for Absolute Beginners
- Machine Learning — Tom Mitchell
- The Hundred-Page Machine Learning Book

**5. Run ingestion (one time only)**
```bash
python backend/rag/ingest.py
```

**6. Start the backend server**
```bash
python -m uvicorn backend.main:app --reload
```

- Backend runs at → **http://localhost:8000**
- API docs at → **http://localhost:8000/docs**

---

### Frontend Setup

```bash
cd frontend
npm install
ng serve
```

Frontend runs at → **http://localhost:4200**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/start-interview` | Upload resume + role → get first question |
| POST | `/submit-answer` | Submit answer → get next question |
| GET | `/summary/{session_id}` | Get full interview summary |

---

## 🖥️ Frontend Screens

**Screen 1 — Upload**
- Select job role from dropdown
- Upload resume PDF
- Click Start Interview

**Screen 2 — Interview**
- Progress bar showing question number
- Question displayed in highlighted box
- Text area to type answers
- Next Question button

**Screen 3 — Summary**
- Stats cards (questions asked / answered)
- Full Q&A list
- Start New Interview button

---

## 🧠 RAG Pipeline Details

### Ingestion Phase (run once)
1. Load PDF books using PyPDFLoader
2. Split into 500-character chunks with 50-character overlap
3. Generate embeddings using HuggingFace all-MiniLM-L6-v2
4. Store in ChromaDB vector database

### Query Phase (per candidate)
1. Extract text from uploaded resume using pdfplumber
2. Build search query from resume + selected role
3. Retrieve top 5 relevant chunks from ChromaDB
4. Send resume + chunks to Groq LLaMA as context
5. LLM generates 5 smart, role-specific questions

---

## ✅ Assignment Requirements Met

| Requirement | Status |
|-------------|--------|
| Resume parsing | ✅ pdfplumber extracts text |
| RAG pipeline | ✅ ChromaDB + HuggingFace embeddings |
| Dynamic question generation | ✅ Groq LLaMA from resume context |
| Interactive interview UI | ✅ Angular with session management |
| Session continuity | ✅ In-memory session storage |
| Response storage | ✅ Q&A stored per session |
| Final summary | ✅ Full report with all Q&A pairs |
| FastAPI backend | ✅ 4 REST endpoints |
| Frontend | ✅ Angular 16 |

---

## ⚠️ Known Limitations

- Sessions stored in memory — reset when server restarts
- No user authentication
- No AI-based answer scoring

## 🔮 Future Improvements

- PostgreSQL for persistent session storage
- AI-powered answer evaluation and scoring
- JWT authentication
- Cloud deployment (AWS / GCP)
- Support for DOCX resume format

---

## 📄 License

This project was built as part of the PGAGI Internship Assignment.

---

*Built with ❤️ by Nethula Shirisha*
