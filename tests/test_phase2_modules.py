"""
Phase 2.2 Tests — Data Plane, RAG, Training, Orchestrator

Tests marked with @pytest.mark.slow import heavy ML libraries
(sentence-transformers) and are excluded by default.
Run with: pytest -m slow
"""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np

# Data Plane (light — always run)
from data.mt5_client import MT5Client
from data.mock_data import get_mock_bars, get_mock_ticks, get_mock_account_state

# LLM & Orchestrator — import at module level (uses httpx, not heavy)
from orchestrator.llm_client import LLMClient


# ============================================================================
# DATA PLANE TESTS
# ============================================================================

class TestMT5Client:
    def test_mt5_fallback_mode(self):
        """Test MT5 client with mock fallback"""
        client = MT5Client(fallback_to_mock=True)
        assert client.connect()
        
    def test_get_mock_bars(self):
        """Test mock bar generation"""
        bars = get_mock_bars("EURUSD", "H1", count=100)
        assert len(bars) == 100
        assert 'open' in bars.columns
        assert 'high' in bars.columns
        assert 'low' in bars.columns
        assert 'close' in bars.columns
        assert 'tick_volume' in bars.columns
        
    def test_get_mock_ticks(self):
        """Test mock tick generation"""
        ticks = get_mock_ticks("USDJPY", count=500)
        assert len(ticks) == 500
        assert 'bid' in ticks.columns
        assert 'ask' in ticks.columns
        
    def test_get_mock_account_state(self):
        """Test mock account state"""
        state = get_mock_account_state()
        assert 'balance' in state
        assert 'equity' in state
        assert 'profit' in state
        assert state['balance'] > 0


# ============================================================================
# KNOWLEDGE & RAG TESTS
# ============================================================================

@pytest.mark.slow
class TestObsidianReader:
    def test_vault_exists(self):
        """Test Obsidian vault is loaded"""
        from knowledge.obsidian_reader import ObsidianReader
        reader = ObsidianReader("Trade-CLI-Vault")
        assert reader.vault_path.exists()
        
    def test_get_concepts(self):
        """Test reading concepts folder"""
        from knowledge.obsidian_reader import ObsidianReader
        reader = ObsidianReader("Trade-CLI-Vault")
        concepts = reader.get_all_concepts()
        assert isinstance(concepts, list)


@pytest.mark.slow
class TestChunkVectorizer:
    def test_split_chunks(self):
        """Test text chunking"""
        from knowledge.chunk_vectorizer import split_into_chunks
        text = "This is a test. " * 50
        chunks = split_into_chunks(text, chunk_size=100, overlap=10)
        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)
        
    def test_vectorizer_initialization(self):
        """Test vectorizer initialization"""
        from knowledge.chunk_vectorizer import ChunkVectorizer
        vectorizer = ChunkVectorizer()
        assert vectorizer.model_name == 'all-MiniLM-L6-v2'


@pytest.mark.slow
class TestContextBuilder:
    def test_context_builder(self):
        """Test context building"""
        from knowledge.context_builder import ContextBuilder
        builder = ContextBuilder("EURUSD", "H1")
        assert builder.symbol == "EURUSD"
        assert builder.timeframe == "H1"
        
    def test_build_rag_context(self):
        """Test RAG context assembly"""
        from knowledge.context_builder import ContextBuilder
        builder = ContextBuilder("EURUSD", "H1")
        chunks = [
            {
                'text': 'Sample context about order blocks',
                'metadata': {'source': 'playbooks', 'symbol': 'EURUSD'},
                'similarity': 0.85
            }
        ]
        context = builder.build_rag_context(chunks)
        assert 'order blocks' in context
        assert '85%' in context or '0.8' in context


# ============================================================================
# TRAINING TESTS
# ============================================================================

@pytest.mark.slow
class TestTrainingIngest:
    def test_ingest_text(self, tmp_path):
        """Test text file ingestion"""
        from training.ingest import ingest_document
        test_file = tmp_path / "test.txt"
        test_file.write_text("Sample trading content about EURUSD")
        
        content = ingest_document(str(test_file))
        assert content is not None
        assert "EURUSD" in content
        
    def test_ingest_markdown(self, tmp_path):
        """Test markdown file ingestion"""
        from training.ingest import ingest_document
        test_file = tmp_path / "test.md"
        test_file.write_text("# Trading\nContent about M15 timeframe")
        
        content = ingest_document(str(test_file))
        assert content is not None
        assert "M15" in content


@pytest.mark.slow
class TestChunker:
    def test_chunk_text(self):
        """Test text chunking"""
        from training.chunker import chunk_text
        text = "Sentence one. " * 50
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) > 0
        assert all(len(c) > 10 for c in chunks)
        
    def test_chunk_markdown(self):
        """Test markdown chunking"""
        from training.chunker import chunk_markdown
        md = "# Heading One\nContent here.\n## Heading Two\nMore content."
        chunks = chunk_markdown(md)
        assert len(chunks) > 0


@pytest.mark.slow
class TestAutoTag:
    def test_tag_symbol(self):
        """Test symbol auto-tagging"""
        from training.tagger import auto_tag
        text = "Analysis of EURUSD on the H1 timeframe"
        tags = auto_tag(text)
        assert 'EURUSD' in tags['symbols']
        assert 'H1' in tags['timeframes']
        
    def test_tag_method(self):
        """Test method auto-tagging"""
        from training.tagger import auto_tag
        text = "Smart money accumulation and order block pattern"
        tags = auto_tag(text)
        assert 'SMC' in tags['methods']
        
    def test_tag_concept(self):
        """Test concept auto-tagging"""
        from training.tagger import auto_tag
        text = "The fair value gap is an important concept"
        tags = auto_tag(text)
        assert len(tags['tags']) > 0


# ============================================================================
# LLM & ORCHESTRATOR TESTS
# ============================================================================

class TestLLMClient:
    def test_llm_initialization(self):
        """Test LLM client init"""
        client = LLMClient()
        assert client.ollama_model == "gemma4:e4b"
        assert client.timeout == 120
        
    def test_llm_not_available_graceful(self):
        """Test LLM gracefully handles unavailability"""
        client = LLMClient()
        # is_available should return False if Ollama not running
        # (should not crash)
        result = client.is_available()
        assert isinstance(result, bool)


@pytest.mark.slow
class TestOrchestrator:
    def test_orchestrator_initialization(self):
        """Test orchestrator init"""
        from orchestrator.orchestrator import Orchestrator
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        assert orch.mt5_client is not None
        assert orch.risk_guardian is not None
        
    def test_orchestrator_health_check(self):
        """Test orchestrator health check"""
        from orchestrator.orchestrator import Orchestrator
        orch = Orchestrator(use_llm=False, use_rag=False)
        health = orch.health_check()
        assert 'timestamp' in health
        assert 'components' in health


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.slow
class TestPhase2Integration:
    def test_full_data_pipeline(self):
        """Test data retrieval pipeline"""
        client = MT5Client(fallback_to_mock=True)
        client.connect()
        
        # Should use mock data
        bars = client.get_bars("EURUSD", "H1", count=50)
        assert bars is not None
        assert len(bars) == 50
        
    def test_training_pipeline(self, tmp_path):
        """Test training ingestion pipeline"""
        from training.ingest import ingest_document
        from training.chunker import chunk_text
        from training.tagger import auto_tag
        
        # Create test file
        test_file = tmp_path / "trading_guide.txt"
        test_file.write_text("""
        EURUSD Playbook
        Setup: Order block on H1
        Timeframe: H15, H1
        Confidence: High
        """)
        
        # Ingest
        text = ingest_document(str(test_file))
        assert text is not None
        
        # Chunk
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) > 0
        
        # Tag
        for chunk in chunks:
            tags = auto_tag(chunk)
            assert 'symbols' in tags
            assert 'timeframes' in tags


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
