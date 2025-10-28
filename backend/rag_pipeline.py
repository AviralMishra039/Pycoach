# backend/rag_pipeline.py 

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# --- Import LOCAL Embedding Library ---
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from langchain_community.vectorstores import Chroma

# --- Configuration  ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

ROOT = Path(__file__).resolve().parents[1]
COURSE_DIR = ROOT / "course_materials"
CHROMA_DB_PATH = ROOT / "chroma_db"
# Use a high-quality local model for embedding:
LOCAL_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
# ----------------------------------------------------------------------


def load_and_index_documents():
    """Loads, splits, and embeds documents into the ChromaDB vector store using a local model."""
    
    if not os.path.exists(COURSE_DIR) or not os.listdir(COURSE_DIR):
        print(f"Error: Directory '{COURSE_DIR}' is empty. Please add course materials.")
        return

    # 1. Load Documents
    print("Loading documents...")
   
    loader = DirectoryLoader(
        str(COURSE_DIR),
        glob="**/*",
        loader_kwargs={'silent_errors': True} 
    )
    docs = loader.load()

    # 2. Split Documents (Chunking)
    print(f"Loaded {len(docs)} documents. Splitting into chunks...")
    # ... (Splitting remains the same)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)

    # 3. Create Embeddings with LOCAL Model and Vector Store
    print(f"Creating embeddings with {LOCAL_EMBEDDING_MODEL} and storing in ChromaDB ({len(splits)} chunks)...")

    # Instantiate the local embedding function
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=LOCAL_EMBEDDING_MODEL,
        encode_kwargs={'normalize_embeddings': True}
    )
    
   
    import shutil
    if os.path.exists(CHROMA_DB_PATH):
        print(f"Clearing incompatible old ChromaDB at {CHROMA_DB_PATH}...")
        shutil.rmtree(CHROMA_DB_PATH)

    # Use Chroma.from_documents to generate vectors and store
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(CHROMA_DB_PATH) 
    )
    vectorstore.persist()
    print("Indexing complete. Vector store persisted.")
    return vectorstore


def get_retriever(embedding_function): 
    
    if embedding_function is None:
        raise ValueError("Embedding function must be provided to retrieve the vectorstore.")

    vectorstore = Chroma(
        persist_directory=str(CHROMA_DB_PATH),
        embedding_function=embedding_function
    )
    return vectorstore.as_retriever(search_kwargs={"k": 5})

if __name__ == "__main__":
    print("--- Running Local Indexing (Zero API Cost) ---")
    
    try:
        load_and_index_documents()
        print("SUCCESS: RAG Foundation is ready.")
    except Exception as e:
        print(f"Indexing Failed! Critical Error: {e}")