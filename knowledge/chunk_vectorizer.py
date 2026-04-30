"""
Chunk Vectorizer — Trade-CLI Phase 2

Converts text chunks into vector embeddings using sentence-transformers.
Lazy-loaded for performance (loads on first use).
"""

from typing import List, Optional, Tuple
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_MODEL = None


def get_embeddings_model():
    """
    Load embedding model (lazy initialization).
    First call is slow (~2-3 seconds), subsequent calls are cached.
    
    Returns:
        sentence_transformers.SentenceTransformer
    """
    global _MODEL
    
    if _MODEL is not None:
        return _MODEL
    
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers embedding model (first time is slow)...")
        _MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded successfully")
        return _MODEL
    except ImportError:
        logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
        return None


class ChunkVectorizer:
    """
    Converts text chunks to embeddings.
    Uses sentence-transformers all-MiniLM-L6-v2 (free, local, ~22MB).
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize vectorizer.
        
        Args:
            model_name: sentence-transformers model name
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = None
    
    def load_model(self) -> bool:
        """
        Load embedding model.
        
        Returns:
            True if successful, False otherwise
        """
        self.model = get_embeddings_model()
        if self.model:
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding dimension: {self.embedding_dim}")
            return True
        return False
    
    def vectorize_chunk(self, text: str) -> Optional[np.ndarray]:
        """
        Convert a single chunk to embedding.
        
        Args:
            text: Text chunk (~500 chars)
            
        Returns:
            Embedding vector (1D array), or None if failed
        """
        if not self.model:
            if not self.load_model():
                return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Vectorization failed: {e}")
            return None
    
    def vectorize_chunks(self, chunks: List[str]) -> Optional[np.ndarray]:
        """
        Convert multiple chunks to embeddings (batch).
        
        Args:
            chunks: List of text chunks
            
        Returns:
            2D array of embeddings (N x embedding_dim), or None if failed
        """
        if not self.model:
            if not self.load_model():
                return None
        
        try:
            embeddings = self.model.encode(chunks, convert_to_numpy=True)
            logger.info(f"Vectorized {len(chunks)} chunks")
            return embeddings
        except Exception as e:
            logger.error(f"Batch vectorization failed: {e}")
            return None
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        # Cosine similarity
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(embedding1, embedding2) / (norm1 * norm2)
    
    def save_embeddings(self, embeddings: np.ndarray, path: str):
        """
        Save embeddings to disk (numpy binary format).
        
        Args:
            embeddings: 2D embedding array
            path: File path to save to
        """
        try:
            np.save(path, embeddings)
            logger.info(f"Embeddings saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")
    
    def load_embeddings(self, path: str) -> Optional[np.ndarray]:
        """
        Load embeddings from disk.
        
        Args:
            path: File path to load from
            
        Returns:
            Embedding array, or None if failed
        """
        try:
            embeddings = np.load(path)
            logger.info(f"Embeddings loaded from {path}")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            return None


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping semantic chunks.
    
    Args:
        text: Full text
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = text.rfind('.', start, end)
            if last_period > start:
                end = last_period + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks
