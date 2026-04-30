"""
Chunking System — Trade-CLI Phase 2

Split ingested documents into semantic chunks.
"""

from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping semantic chunks.
    
    Args:
        text: Input text
        chunk_size: Target chunk size in characters
        overlap: Character overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or chunk_size <= 0:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at sentence boundary (period, question mark, exclamation)
        if end < len(text):
            # Look for sentence-ending punctuation
            last_punct = max(
                text.rfind('.', start, end),
                text.rfind('?', start, end),
                text.rfind('!', start, end),
                text.rfind('\n\n', start, end)  # Paragraph break
            )
            
            if last_punct > start + (chunk_size // 2):  # At least half-way
                end = last_punct + 1
        
        chunk = text[start:end].strip()
        if len(chunk) > 10:  # Skip tiny chunks
            chunks.append(chunk)
        
        start = end - overlap
    
    logger.info(f"Split text into {len(chunks)} chunks (size ~{chunk_size}, overlap {overlap})")
    return chunks


def chunk_markdown(text: str, chunk_at_headings: bool = True) -> List[str]:
    """
    Split markdown text, preferring heading boundaries.
    
    Args:
        text: Markdown text
        chunk_at_headings: Split at # or ## headings
        
    Returns:
        List of chunks
    """
    if not chunk_at_headings:
        return chunk_text(text)
    
    chunks = []
    
    # Split by heading level
    sections = re.split(r'^(#{1,3}\s+.+?)$', text, flags=re.MULTILINE)
    
    current_chunk = ""
    for section in sections:
        if section.strip():
            current_chunk += section + "\n"
            
            # Check if we have enough for a chunk
            if len(current_chunk) > 400:
                chunks.append(current_chunk.strip())
                current_chunk = ""
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    logger.info(f"Split markdown into {len(chunks)} sections")
    return chunks


def chunk_pdf(text: str) -> List[str]:
    """
    Split PDF text (usually one chunk per paragraph/page).
    
    Args:
        text: PDF-extracted text
        
    Returns:
        List of chunks
    """
    # Split by double newlines (paragraphs) or page breaks
    chunks = re.split(r'\n\n+|\f', text)
    chunks = [c.strip() for c in chunks if len(c.strip()) > 20]
    
    logger.info(f"Split PDF into {len(chunks)} paragraphs")
    return chunks


def merge_small_chunks(chunks: List[str], min_size: int = 100) -> List[str]:
    """
    Merge chunks smaller than min_size with neighbors.
    
    Args:
        chunks: List of chunks
        min_size: Minimum chunk size
        
    Returns:
        Merged chunks
    """
    merged = []
    current = ""
    
    for chunk in chunks:
        current += chunk + "\n\n"
        
        if len(current) >= min_size:
            merged.append(current.strip())
            current = ""
    
    if current.strip():
        merged.append(current.strip())
    
    logger.info(f"Merged {len(chunks)} chunks into {len(merged)} chunks (min size: {min_size})")
    return merged
