# backend/reranker_utils.py

from sentence_transformers import CrossEncoder
from langchain_core.documents import Document
from operator import itemgetter
from typing import List, Tuple, Dict, Any, Sequence

# Load the CrossEncoder model globally when the module is imported
RERANKER_MODEL_NAME = "BAAI/bge-reranker-base"
try:
    RERANKER = CrossEncoder(RERANKER_MODEL_NAME)
    print(f"Reranker model {RERANKER_MODEL_NAME} loaded successfully for custom utility.")
except Exception as e:
    print(f"Warning: Could not load CrossEncoder model {RERANKER_MODEL_NAME}. Error: {e}")
    RERANKER = None

def rerank_documents(retriever_output: Dict[str, Any], top_n: int = 5) -> str:
    """
    Custom function to perform reranking using sentence-transformers CrossEncoder.
    This replaces the LangChain CrossEncoderReranker component.
    """
    if RERANKER is None:
        return "Reranking model failed to load. Proceeding with original retrieval."
        
    query = retriever_output["question"]
    # We assume the documents are retrieved under the 'context' key by the retriever chain
    documents: Sequence[Document] = retriever_output["context"]
    
    if not documents:
        return "No relevant documents found."

    # 1. Prepare pairs for Cross-Encoder scoring: (query, document_content)
    pairs = [(query, doc.page_content) for doc in documents]

    # 2. Score documents
    # The CrossEncoder returns a score for each pair
    scores = RERANKER.predict(pairs)

    # 3. Combine scores with documents and sort
    scored_documents = list(zip(documents, scores))
    # Sort in descending order (highest score first)
    scored_documents.sort(key=itemgetter(1), reverse=True)

    # 4. Select the top N and format the context for the LLM
    top_docs = [doc for doc, score in scored_documents[:top_n]]
    
    # Format context string (the final output for the LLM)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in top_docs])
    
    return context_text