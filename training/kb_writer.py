"""
Knowledge Base Writer — Trade-CLI Phase 2

Save trained knowledge to SQLite and Obsidian.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import sqlite3
import logging
from datetime import datetime
import frontmatter

logger = logging.getLogger(__name__)


def write_to_knowledge_base(chunk_data: Dict[str, Any], db_path: str = "database.db") -> bool:
    """
    Write a chunk to SQLite knowledge_base table.
    
    Args:
        chunk_data: Dict with text, metadata, source_file
        db_path: Path to SQLite database
        
    Returns:
        True if successful
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert into knowledge_base table
        cursor.execute("""
            INSERT OR REPLACE INTO knowledge_base
            (id, category, symbol, setup_type, description, conditions, 
             edge_description, created_date, confidence_level, source, review_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"kb_{datetime.now().timestamp()}_{hash(chunk_data['text']) % 1000000}",
            chunk_data.get('metadata', {}).get('category', 'general'),
            chunk_data.get('metadata', {}).get('symbols', [''])[0] or 'ALL',
            chunk_data.get('metadata', {}).get('methods', [''])[0] or 'general',
            chunk_data.get('text', '')[:500],  # First 500 chars
            str(chunk_data.get('metadata', {})),
            chunk_data.get('text', '')[500:1000] if len(chunk_data.get('text', '')) > 500 else '',
            datetime.now().isoformat(),
            'high' if chunk_data.get('metadata', {}).get('confidence', 0) > 0.8 else 'medium',
            chunk_data.get('source_file', 'manual_ingestion'),
            'unreviewed'
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Wrote chunk to knowledge_base")
        return True
    except Exception as e:
        logger.error(f"Failed to write to knowledge_base: {e}")
        return False


def write_to_obsidian(chunk_data: Dict[str, Any], vault_path: str = "Trade-CLI-Vault") -> bool:
    """
    Write a chunk to Obsidian vault.
    Creates a file in treino/conhecimento/ or appropriate folder.
    
    Args:
        chunk_data: Dict with text, metadata
        vault_path: Path to Obsidian vault
        
    Returns:
        True if successful
    """
    try:
        vault = Path(vault_path)
        metadata = chunk_data.get('metadata', {})
        
        # Determine folder based on category
        category = metadata.get('category', 'general')
        folder_map = {
            'playbook': 'playbooks',
            'post_mortem': 'post-mortems',
            'thesis': 'teses',
            'lesson_learned': 'treino/estudos-de-caso',
            'educational': 'treino',
            'backtesting': 'treino',
        }
        
        folder_name = folder_map.get(category, 'treino/conhecimento')
        folder = vault / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        symbol = metadata.get('symbols', ['general'])[0] if metadata.get('symbols') else 'general'
        filename = f"{timestamp}-{symbol}-{category}.md"
        file_path = folder / filename
        
        # Create frontmatter
        frontmatter_data = {
            'title': f"Knowledge: {category} - {symbol}",
            'created': datetime.now().isoformat(),
            'category': category,
            'symbols': metadata.get('symbols', []),
            'methods': metadata.get('methods', []),
            'timeframes': metadata.get('timeframes', []),
            'tags': metadata.get('tags', []),
            'confidence': metadata.get('confidence', 0.5),
            'source': chunk_data.get('source_file', 'unknown'),
            'review_status': 'unreviewed',
        }
        
        # Create post
        post = frontmatter.Post(chunk_data.get('text', ''))
        post.metadata = frontmatter_data
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        logger.info(f"Wrote chunk to Obsidian: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write to Obsidian: {e}")
        return False


def batch_write_knowledge(chunks_data: List[Dict[str, Any]], 
                         db_path: str = "database.db",
                         vault_path: str = "Trade-CLI-Vault") -> Dict[str, int]:
    """
    Batch write multiple chunks to knowledge base.
    
    Args:
        chunks_data: List of chunk dicts
        db_path: Path to SQLite database
        vault_path: Path to Obsidian vault
        
    Returns:
        Dict with counts: {db_written, obsidian_written, failed}
    """
    counts = {'db_written': 0, 'obsidian_written': 0, 'failed': 0}
    
    for chunk in chunks_data:
        try:
            # Write to SQLite
            if write_to_knowledge_base(chunk, db_path):
                counts['db_written'] += 1
            
            # Write to Obsidian
            if write_to_obsidian(chunk, vault_path):
                counts['obsidian_written'] += 1
        except Exception as e:
            logger.error(f"Failed to write chunk: {e}")
            counts['failed'] += 1
    
    logger.info(f"Batch write complete: {counts}")
    return counts
