"""
Obsidian Vault Reader — Trade-CLI Phase 2

Reads markdown files from Obsidian vault and extracts structured knowledge.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter
import logging

logger = logging.getLogger(__name__)


class ObsidianReader:
    """Reads and parses Obsidian vault files."""
    
    def __init__(self, vault_path: str = "Trade-CLI-Vault"):
        """
        Initialize Obsidian reader.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            logger.error(f"Vault not found: {vault_path}")
        else:
            logger.info(f"Obsidian vault loaded: {vault_path}")
    
    def read_folder(self, folder_name: str) -> List[Dict[str, Any]]:
        """
        Read all markdown files from a folder.
        
        Args:
            folder_name: Folder name (e.g., "teses", "playbooks", "conceitos")
            
        Returns:
            List of dicts with file metadata and content
        """
        folder = self.vault_path / folder_name
        if not folder.exists():
            logger.warning(f"Folder not found: {folder}")
            return []
        
        notes = []
        for md_file in folder.glob("*.md"):
            try:
                note = self._parse_file(md_file)
                if note:
                    notes.append(note)
            except Exception as e:
                logger.error(f"Error parsing {md_file}: {e}")
        
        logger.info(f"Loaded {len(notes)} notes from {folder_name}/")
        return notes
    
    def read_file(self, relative_path: str) -> Optional[Dict[str, Any]]:
        """
        Read a specific markdown file.
        
        Args:
            relative_path: Path relative to vault (e.g., "teses/2026-04-30-EURUSD.md")
            
        Returns:
            Dict with file metadata and content, or None if failed
        """
        file_path = self.vault_path / relative_path
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        return self._parse_file(file_path)
    
    def _parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a markdown file with frontmatter.
        
        Returns:
            Dict with metadata and content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            return {
                "filename": file_path.name,
                "relative_path": str(file_path.relative_to(self.vault_path)),
                "metadata": post.metadata,
                "content": post.content,
                "full_text": str(post),  # Frontmatter + content combined
            }
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        Find all notes with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of matching notes
        """
        all_notes = []
        
        # Search in main folders
        for folder in ["teses", "playbooks", "post-mortems", "conceitos", "metodos", "treino"]:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                all_notes.extend(self.read_folder(folder))
        
        # Filter by tag
        matching = []
        for note in all_notes:
            tags = note.get('metadata', {}).get('tags', [])
            if isinstance(tags, str):
                tags = [tags]
            if tag in tags or tag in str(tags):
                matching.append(note)
        
        logger.info(f"Found {len(matching)} notes with tag '{tag}'")
        return matching
    
    def search_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Find all notes mentioning a symbol (EURUSD, USDJPY, etc).
        
        Args:
            symbol: Currency pair or asset
            
        Returns:
            List of matching notes
        """
        all_notes = []
        
        for folder in ["teses", "playbooks", "post-mortems", "ativos"]:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                all_notes.extend(self.read_folder(folder))
        
        matching = []
        for note in all_notes:
            if symbol in note['content'] or symbol in str(note.get('metadata', {})):
                matching.append(note)
        
        logger.info(f"Found {len(matching)} notes for symbol '{symbol}'")
        return matching
    
    def get_all_concepts(self) -> List[Dict[str, Any]]:
        """Get all concept notes."""
        return self.read_folder("conceitos")
    
    def get_all_methods(self) -> List[Dict[str, Any]]:
        """Get all method notes."""
        return self.read_folder("metodos")
    
    def get_all_playbooks(self) -> List[Dict[str, Any]]:
        """Get all playbook notes."""
        return self.read_folder("playbooks")
    
    def get_all_theses(self) -> List[Dict[str, Any]]:
        """Get all thesis notes."""
        return self.read_folder("teses")
