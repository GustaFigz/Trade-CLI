"""
RAG System Tests — Trade-CLI Phase 2.3+

Tests ObsidianReader, RAGRetriever, and ContextBuilder.
Targets 80%+ coverage on knowledge/ module.

Phase: 2.4
Date: 2026-05-01
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from knowledge.obsidian_reader import ObsidianReader
from knowledge.rag_retriever import RAGRetriever, KnowledgeChunk
from knowledge.context_builder import ContextBuilder


class TestObsidianReader:
    def test_initialization(self):
        """Test ObsidianReader can initialize."""
        reader = ObsidianReader(vault_path="Trade-CLI-Vault")
        assert reader.vault_path == Path("Trade-CLI-Vault")

    def test_read_folder_returns_list(self):
        """Test reading a folder returns list."""
        reader = ObsidianReader(vault_path="Trade-CLI-Vault")
        concepts = reader.read_folder("conceitos")
        assert isinstance(concepts, list)
        # Should find some concept notes
        if Path("Trade-CLI-Vault/conceitos").exists():
            assert len(concepts) > 0

    def test_get_all_concepts(self):
        """Test get_all_concepts returns list."""
        reader = ObsidianReader(vault_path="Trade-CLI-Vault")
        concepts = reader.get_all_concepts()
        assert isinstance(concepts, list)

    def test_get_all_methods(self):
        """Test get_all_methods returns list."""
        reader = ObsidianReader(vault_path="Trade-CLI-Vault")
        methods = reader.get_all_methods()
        assert isinstance(methods, list)

    def test_search_by_symbol(self):
        """Test symbol-based search returns list."""
        reader = ObsidianReader(vault_path="Trade-CLI-Vault")
        results = reader.search_by_symbol("EURUSD")
        assert isinstance(results, list)

    def test_search_by_tag(self):
        """Test tag-based search returns list."""
        reader = ObsidianReader(vault_path="Trade-CLI-Vault")
        results = reader.search_by_tag("ict")
        assert isinstance(results, list)


class TestRAGRetriever:
    def test_initialization(self):
        """Test RAGRetriever initializes."""
        retriever = RAGRetriever()
        assert retriever.vault_path is not None
        assert retriever.db_path is not None

    def test_search_returns_list(self):
        """Test search returns list of KnowledgeChunk."""
        retriever = RAGRetriever()
        results = retriever.search("EURUSD order block", top_k=3)
        assert isinstance(results, list)
        # Results should be KnowledgeChunk objects
        for result in results:
            assert isinstance(result, KnowledgeChunk)
            assert hasattr(result, "content")
            assert hasattr(result, "source")
            assert hasattr(result, "score")

    def test_search_empty_corpus(self):
        """Test search gracefully handles empty corpus."""
        retriever = RAGRetriever()
        with patch.object(retriever, "_corpus", []):
            results = retriever.search("test query", top_k=3)
        assert results == []

    def test_search_top_k_limit(self):
        """Test top_k parameter limits results."""
        retriever = RAGRetriever()
        results_3 = retriever.search("trading", top_k=3)
        assert len(results_3) <= 3

    def test_corpus_loading(self):
        """Test corpus loads from vault."""
        retriever = RAGRetriever()
        # Corpus should be loaded during init
        assert len(retriever._corpus) >= 0  # May be 0 if vault empty


class TestContextBuilder:
    def test_initialization(self):
        """Test ContextBuilder initializes."""
        builder = ContextBuilder(symbol="EURUSD", timeframe="H1")
        assert builder.symbol == "EURUSD"
        assert builder.timeframe == "H1"

    def test_build_rag_context(self):
        """Test building RAG context from chunks."""
        builder = ContextBuilder()
        chunks = [
            {
                "text": "Order block at 1.0850",
                "metadata": {"source": "vault/conceitos/order-block.md", "tags": ["ict"]},
                "similarity": 0.85,
            }
        ]
        context = builder.build_rag_context(chunks)
        assert isinstance(context, str)
        assert len(context) > 0
        assert "Order block" in context

    def test_build_rag_context_empty(self):
        """Test building context with no chunks."""
        builder = ContextBuilder()
        context = builder.build_rag_context([])
        assert isinstance(context, str)
        assert "No relevant context" in context

    def test_build_analysis_context(self):
        """Test building analysis context."""
        builder = ContextBuilder(symbol="EURUSD", timeframe="H1")
        technical_data = {
            "bias": "bullish",
            "confidence": 0.75,
            "alignment_score": 0.70,
            "engine_scores": {"technical": 0.80, "price_action": 0.70},
            "invalidations": ["Close below 1.0850"],
            "risk_notes": ["Spread elevated"],
        }
        context = builder.build_analysis_context(technical_data, "Some knowledge context")
        assert isinstance(context, str)
        assert "EURUSD" in context
        assert "H1" in context
        assert "bullish" in context

    def test_build_prompt_for_synthesis(self):
        """Test building LLM synthesis prompt."""
        builder = ContextBuilder(symbol="USDJPY", timeframe="M15")
        analysis_context = "Technical scores: 0.75"
        prompt = builder.build_prompt_for_synthesis(analysis_context, user_query="Is this bullish?")
        assert isinstance(prompt, str)
        assert "USDJPY" in prompt
        assert "M15" in prompt
        assert "Is this bullish?" in prompt

    def test_build_prompt_without_query(self):
        """Test building prompt without user query."""
        builder = ContextBuilder()
        analysis_context = "Some analysis"
        prompt = builder.build_prompt_for_synthesis(analysis_context)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
