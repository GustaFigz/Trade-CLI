"""
Training System — Trade-CLI Phase 2

Knowledge ingestion from PDFs, Markdown, TXT.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def ingest_document(file_path: str) -> Optional[str]:
    """
    Read document file (PDF, Markdown, TXT).
    
    Args:
        file_path: Path to document
        
    Returns:
        Document text, or None if failed
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    file_ext = file_path.suffix.lower()
    
    try:
        if file_ext == '.txt':
            return ingest_text(str(file_path))
        elif file_ext == '.md':
            return ingest_markdown(str(file_path))
        elif file_ext == '.pdf':
            return ingest_pdf(str(file_path))
        elif file_ext == '.docx':
            return ingest_docx(str(file_path))
        else:
            logger.error(f"Unsupported file type: {file_ext}")
            return None
    except Exception as e:
        logger.error(f"Ingestion failed for {file_path}: {e}")
        return None


def ingest_text(file_path: str) -> Optional[str]:
    """Read plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Ingested text file: {file_path} ({len(content)} chars)")
        return content
    except Exception as e:
        logger.error(f"Failed to ingest text: {e}")
        return None


def ingest_markdown(file_path: str) -> Optional[str]:
    """Read markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Ingested markdown file: {file_path} ({len(content)} chars)")
        return content
    except Exception as e:
        logger.error(f"Failed to ingest markdown: {e}")
        return None


def ingest_pdf(file_path: str) -> Optional[str]:
    """
    Read PDF file.
    Requires: pip install pypdf
    """
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(file_path)
        text = ""
        
        for page_num, page in enumerate(reader.pages):
            text += page.extract_text()
            logger.debug(f"Extracted page {page_num + 1}/{len(reader.pages)}")
        
        logger.info(f"Ingested PDF: {file_path} ({len(text)} chars from {len(reader.pages)} pages)")
        return text
    except ImportError:
        logger.error("pypdf not installed. Install with: pip install pypdf")
        return None
    except Exception as e:
        logger.error(f"Failed to ingest PDF: {e}")
        return None


def ingest_docx(file_path: str) -> Optional[str]:
    """
    Read DOCX file.
    Requires: pip install python-docx
    """
    try:
        from docx import Document
        
        doc = Document(file_path)
        text = ""
        
        for para in doc.paragraphs:
            text += para.text + "\n"
        
        logger.info(f"Ingested DOCX: {file_path} ({len(text)} chars from {len(doc.paragraphs)} paragraphs)")
        return text
    except ImportError:
        logger.error("python-docx not installed. Install with: pip install python-docx")
        return None
    except Exception as e:
        logger.error(f"Failed to ingest DOCX: {e}")
        return None


def batch_ingest(directory: str, pattern: str = "*.*") -> List[Dict[str, Any]]:
    """
    Ingest all documents from a directory.
    
    Args:
        directory: Directory path
        pattern: File pattern (default: all files)
        
    Returns:
        List of {filename, text, file_type} dicts
    """
    directory = Path(directory)
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return []
    
    results = []
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            text = ingest_document(str(file_path))
            if text:
                results.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'text': text,
                    'file_type': file_path.suffix.lower(),
                    'size': len(text)
                })
    
    logger.info(f"Batch ingested {len(results)} files from {directory}")
    return results
