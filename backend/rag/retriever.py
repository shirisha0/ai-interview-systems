import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# ─────────────────────────────────────────────
# Load the ChromaDB we already created
# ─────────────────────────────────────────────
def get_vectordb():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    vectordb = Chroma(
        persist_directory=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
        embedding_function=embeddings
    )
    return vectordb


# ─────────────────────────────────────────────
# Search knowledge base and return top results
# ─────────────────────────────────────────────
def retrieve_context(query: str, k: int = 5) -> list:
    """
    query = search text built from resume + role
    k     = how many chunks to return
    """
    db = get_vectordb()
    results = db.similarity_search(query, k=k)
    return [doc.page_content for doc in results]


# ─────────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    query = "machine learning algorithms supervised learning"
    print(f"Searching for: {query}\n")
    results = retrieve_context(query, k=3)
    for i, chunk in enumerate(results, 1):
        print(f"--- Result {i} ---")
        print(chunk)
        print()