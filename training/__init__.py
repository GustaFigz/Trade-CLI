"""
Training System — Trade-CLI Phase 2

Knowledge ingestion and processing:
- Ingest PDFs, Markdown, TXT
- Chunk into semantic pieces
- Auto-tag with metadata
- Write to SQLite + Obsidian
- Process post-mortems
"""

from training.ingest import ingest_document
from training.chunker import chunk_text
from training.tagger import auto_tag
from training.kb_writer import write_to_knowledge_base

__all__ = [
    "ingest_document",
    "chunk_text",
    "auto_tag",
    "write_to_knowledge_base"
]
