"""
Knowledge Retrieval & RAG — Trade-CLI Phase 2

Retrieval-Augmented Generation system:
- Reads Obsidian vault
- Vectorizes chunks with sentence-transformers
- Searches with FAISS
- Returns relevant context for LLM
"""

from knowledge.obsidian_reader import ObsidianReader
from knowledge.chunk_vectorizer import ChunkVectorizer
from knowledge.rag_retriever import RAGRetriever
from knowledge.context_builder import ContextBuilder

__all__ = [
    "ObsidianReader",
    "ChunkVectorizer",
    "RAGRetriever",
    "ContextBuilder"
]
