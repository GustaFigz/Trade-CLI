"""
RAG Retriever — Sistema de recuperação de conhecimento.
Versão leve: TF-IDF (sklearn) para embeddings.
Upgrade path: sentence-transformers quando disponível.

O RAG consulta:
1. SQLite knowledge_base (chunks indexados)
2. Obsidian vault (ficheiros markdown directamente)

Fase: 2.3
Data: 2026-05-01
"""
from __future__ import annotations

import os
import sqlite3
import re
from dataclasses import dataclass
from pathlib import Path
import structlog

log = structlog.get_logger(__name__)


@dataclass
class KnowledgeChunk:
    content: str
    source: str        # nome do ficheiro ou ID
    topic: str
    score: float = 0.0


class RAGRetriever:
    """
    Retriever de conhecimento com TF-IDF simples.
    Consulta SQLite knowledge_base + vault Obsidian.
    """

    def __init__(self) -> None:
        self.db_path = Path(os.getenv("DB_PATH", "database.db"))
        self.vault_path = Path(os.getenv("OBSIDIAN_VAULT_PATH", "./Trade-CLI-Vault"))
        self._vectorizer = None
        self._matrix = None
        self._corpus: list[KnowledgeChunk] = []
        self._load_corpus()

    def _load_corpus(self) -> None:
        """Carrega corpus do SQLite + vault para memória."""
        chunks: list[KnowledgeChunk] = []

        # 1. SQLite knowledge_base
        if self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                # Check if table exists first
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_base'"
                )
                if cursor.fetchone():
                    rows = conn.execute(
                        "SELECT id, content, topic, source FROM knowledge_base "
                        "WHERE review_status = 'active' LIMIT 500"
                    ).fetchall()
                    for row_id, content, topic, source in rows:
                        chunks.append(KnowledgeChunk(
                            content=content or "",
                            source=source or str(row_id),
                            topic=topic or "geral",
                        ))
                conn.close()
            except Exception as e:
                log.warning("kb_load_failed", error=str(e))

        # 2. Obsidian vault (conceitos, metodos, playbooks)
        priority_folders = ["conceitos", "metodos", "playbooks", "teses", "treino"]
        for folder in priority_folders:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                for md_file in folder_path.glob("*.md"):
                    try:
                        content = md_file.read_text(encoding="utf-8")
                        # Remove frontmatter YAML
                        content = re.sub(r"^---.*?---\n", "", content, flags=re.DOTALL)
                        if len(content.strip()) > 50:
                            chunks.append(KnowledgeChunk(
                                content=content[:2000],  # primeiros 2000 chars
                                source=f"vault/{folder}/{md_file.name}",
                                topic=folder,
                            ))
                    except Exception:
                        pass

        self._corpus = chunks
        if chunks:
            self._build_tfidf()
        log.info("rag_corpus_loaded", chunks=len(chunks))

    def _build_tfidf(self) -> None:
        """Constrói índice TF-IDF do corpus."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words=None,  # mantém termos técnicos de trading
                ngram_range=(1, 2),
            )
            texts = [c.content for c in self._corpus]
            self._matrix = self._vectorizer.fit_transform(texts)
            log.info("tfidf_built", vocabulary_size=len(self._vectorizer.vocabulary_))
        except ImportError:
            log.warning("sklearn_not_available", fallback="keyword_search")
            self._vectorizer = None

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeChunk]:
        """Retorna os top_k chunks mais relevantes para a query."""
        if not self._corpus:
            return []

        if self._vectorizer is not None and self._matrix is not None:
            return self._tfidf_search(query, top_k)
        else:
            return self._keyword_search(query, top_k)

    def _tfidf_search(self, query: str, top_k: int) -> list[KnowledgeChunk]:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        q_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self._matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0.01:  # threshold mínimo
                chunk = KnowledgeChunk(
                    content=self._corpus[idx].content,
                    source=self._corpus[idx].source,
                    topic=self._corpus[idx].topic,
                    score=float(scores[idx]),
                )
                results.append(chunk)
        return results

    def _keyword_search(self, query: str, top_k: int) -> list[KnowledgeChunk]:
        """Fallback: busca por keywords simples."""
        keywords = query.lower().split()
        scored = []
        for chunk in self._corpus:
            content_lower = chunk.content.lower()
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                result = KnowledgeChunk(
                    content=chunk.content,
                    source=chunk.source,
                    topic=chunk.topic,
                    score=float(score),
                )
                scored.append(result)
        scored.sort(reverse=True, key=lambda x: x.score)
        return scored[:top_k]
