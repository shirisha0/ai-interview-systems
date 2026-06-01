import os
from groq import Groq
from dotenv import load_dotenv
from backend.rag.retriever import retrieve_context

load_dotenv()

# Groq client — free and fast
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_query(resume_text: str, role: str) -> str:
    return f"{role} {resume_text[:500]}"


def generate_questions(resume_text: str, role: str, num_questions: int = 5) -> list:

    # Step 1 — retrieve relevant chunks
    query = build_query(resume_text, role)
    context_chunks = retrieve_context(query, k=5)
    context_str = "\n\n".join(context_chunks)

    # Step 2 — build prompt
    prompt = f"""
You are a technical interviewer for the role of {role}.

Here is the candidate's resume:
{resume_text[:1000]}

Here is relevant knowledge from the textbook:
{context_str}

Generate {num_questions} interview questions that:
- Are specific to the candidate's background and skills
- Test concepts from the knowledge base above
- Range from basic to advanced
- Are NOT generic (avoid "tell me about yourself")
- Are practical and real-world focused

Return only the questions, numbered 1 to {num_questions}.
"""

    # Step 3 — call Groq (free, fast)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    raw = response.choices[0].message.content

    # Step 4 — clean and return as list
    questions = [
        line.strip() for line in raw.split("\n")
        if line.strip() and line.strip()[0].isdigit()
    ]
    return questions


# ─────────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    sample_resume = """
    Name: Ganesh
    Skills: Python, Machine Learning, scikit-learn, TensorFlow, REST APIs
    Experience: Built a sentiment analysis model using LSTM.
                Deployed ML models using Flask.
    Education: B.Tech Computer Science
    """

    print("Generating interview questions...\n")
    questions = generate_questions(
        resume_text=sample_resume,
        role="AI/ML Engineer",
        num_questions=5
    )

    for q in questions:
        print(q)