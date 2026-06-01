import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load your .env file (GOOGLE_API_KEY and CHROMA_DB_PATH)
load_dotenv()

# ─────────────────────────────────────────────
# STEP 1 — Load all PDF books from /data folder
# ─────────────────────────────────────────────
def load_documents(data_folder: str = "./data"):
    all_docs = []
    pdf_files = [f for f in os.listdir(data_folder) if f.endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in /data folder. Please add your books.")
        return []

    for filename in pdf_files:
        filepath = os.path.join(data_folder, filename)
        print(f"Loading: {filename}")
        try:
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            all_docs.extend(docs)
            print(f"  → {len(docs)} pages loaded")
        except Exception as e:
            print(f"  → Error loading {filename}: {e}")

    print(f"\nTotal pages loaded: {len(all_docs)}")
    return all_docs


# ─────────────────────────────────────────────
# STEP 2 — Split pages into smaller chunks
# ─────────────────────────────────────────────
def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # each chunk = ~500 characters
        chunk_overlap=50,     # overlap so context is not lost between chunks
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"Total chunks created: {len(chunks)}")
    return chunks


# ─────────────────────────────────────────────
# STEP 3 — Convert chunks to vectors and store
# ─────────────────────────────────────────────
def store_in_vectordb(chunks):
    print("\nGenerating embeddings and storing in ChromaDB...")
    print("This may take a few minutes depending on book size...")

    # Use Google Gemini embeddings (free)
    embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
    # Store in ChromaDB
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=os.getenv("CHROMA_DB_PATH", "./chroma_db")
    )

    vectordb.persist()
    print("Successfully stored in ChromaDB!")
    print(f"Database saved at: {os.getenv('CHROMA_DB_PATH', './chroma_db')}")
    return vectordb


# ─────────────────────────────────────────────
# RUN everything
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Starting Knowledge Base Ingestion ===\n")

    # Step 1
    docs = load_documents("./data")
    if not docs:
        exit()

    # Step 2
    chunks = chunk_documents(docs)

    # Step 3
    store_in_vectordb(chunks)

    print("\n=== Ingestion Complete! Knowledge base is ready. ===")