"""
RAG Retriever — Trade-CLI Phase 2

Vector search with FAISS and metadata filtering.
Retrieves top-K relevant chunks from knowledge base.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import logging
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

# Global FAISS index (lazy loaded)
_FAISS_INDEX = None


def get_faiss_module():
    """Load FAISS module."""
    try:
        import faiss
        return faiss
    except ImportError:
        logger.error("faiss-cpu not installed. Install with: pip install faiss-cpu")
        return None


class RAGRetriever:
    """
    Vector search retriever using FAISS.
    Retrieves relevant chunks from knowledge base based on query.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize retriever.
        
        Args:
            embedding_dim: Dimension of embeddings (default: all-MiniLM-L6-v2)
        """
        self.embedding_dim = embedding_dim
        self.index = None
        self.chunk_metadata = []  # List of {id, symbol, source, confidence, text, ...}
        self.faiss = get_faiss_module()
    
    def build_index(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> bool:
        """
        Build FAISS vector index from embeddings.
        
        Args:
            embeddings: 2D array of embeddings (N x embedding_dim)
            metadata: List of metadata dicts for each embedding
            
        Returns:
            True if successful
        """
        if self.faiss is None:
            return False
        
        try:
            if embeddings.dtype != np.float32:
                embeddings = embeddings.astype(np.float32)
            
            # Create flat index (exact search)
            self.index = self.faiss.IndexFlatL2(self.embedding_dim)
            self.index.add(embeddings)
            
            self.chunk_metadata = metadata
            
            logger.info(f"FAISS index built with {len(embeddings)} vectors")
            return True
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, k: int = 5, 
               symbol_filter: Optional[str] = None,
               min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for top-K similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            symbol_filter: Filter by symbol (e.g., "EURUSD")
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of {id, distance, similarity, metadata, text}
        """
        if self.index is None:
            logger.warning("Index not built yet")
            return []
        
        try:
            if query_embedding.dtype != np.float32:
                query_embedding = query_embedding.astype(np.float32)
            
            # Reshape query to 2D
            query_embedding = query_embedding.reshape(1, -1)
            
            # Search
            distances, indices = self.index.search(query_embedding, k * 2)  # Get more, then filter
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx == -1:  # Invalid result
                    continue
                
                distance = distances[0][i]
                # Convert L2 distance to similarity (0-1)
                similarity = 1.0 / (1.0 + distance)
                
                metadata = self.chunk_metadata[idx]
                
                # Apply filters
                if symbol_filter and metadata.get('symbol') != symbol_filter:
                    continue
                
                if metadata.get('confidence', 1.0) < min_confidence:
                    continue
                
                results.append({
                    'index': idx,
                    'distance': float(distance),
                    'similarity': float(similarity),
                    'metadata': metadata,
                    'text': metadata.get('text', ''),
                })
                
                if len(results) >= k:
                    break
            
            logger.info(f"Retrieved {len(results)} chunks for query (similarity > {min_confidence})")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def save_index(self, path: str):
        """
        Save FAISS index and metadata to disk.
        
        Args:
            path: Directory path to save to
        """
        if self.faiss is None or self.index is None:
            logger.error("Index not available")
            return
        
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_path = Path(path) / "faiss.index"
            self.faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            metadata_path = Path(path) / "metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.chunk_metadata, f)
            
            logger.info(f"Index saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def load_index(self, path: str) -> bool:
        """
        Load FAISS index and metadata from disk.
        
        Args:
            path: Directory path to load from
            
        Returns:
            True if successful
        """
        if self.faiss is None:
            return False
        
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            
            # Load FAISS index
            index_path = Path(path) / "faiss.index"
            if index_path.exists():
                self.index = self.faiss.read_index(str(index_path))
            
            # Load metadata
            metadata_path = Path(path) / "metadata.pkl"
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.chunk_metadata = pickle.load(f)
            
            logger.info(f"Index loaded from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
