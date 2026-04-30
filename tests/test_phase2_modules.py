"""
Phase 2.2 Tests — Data Plane, RAG, Training, Orchestrator
"""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np

# Data Plane
from data.mt5_client import MT5Client
from data.mock_data import get_mock_bars, get_mock_ticks, get_mock_account_state

# Knowledge & RAG
from knowledge.obsidian_reader import ObsidianReader
from knowledge.chunk_vectorizer import ChunkVectorizer, split_into_chunks
from knowledge.rag_retriever import RAGRetriever
from knowledge.context_builder import ContextBuilder

# Training
from training.ingest import ingest_document, ingest_text
from training.chunker import chunk_text, chunk_markdown
from training.tagger import auto_tag

# LLM & Orchestrator
from orchestrator.llm_client import LocalLLMClient
from orchestrator.orchestrator import Orchestrator


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

class TestObsidianReader:
    def test_vault_exists(self):
        """Test Obsidian vault is loaded"""
        reader = ObsidianReader("Trade-CLI-Vault")
        assert reader.vault_path.exists()
        
    def test_get_concepts(self):
        """Test reading concepts folder"""
        reader = ObsidianReader("Trade-CLI-Vault")
        concepts = reader.get_all_concepts()
        assert isinstance(concepts, list)


class TestChunkVectorizer:
    def test_split_chunks(self):
        """Test text chunking"""
        text = "This is a test. " * 50
        chunks = split_into_chunks(text, chunk_size=100, overlap=10)
        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)
        
    def test_vectorizer_initialization(self):
        """Test vectorizer initialization"""
        vectorizer = ChunkVectorizer()
        assert vectorizer.model_name == 'all-MiniLM-L6-v2'


class TestContextBuilder:
    def test_context_builder(self):
        """Test context building"""
        builder = ContextBuilder("EURUSD", "H1")
        assert builder.symbol == "EURUSD"
        assert builder.timeframe == "H1"
        
    def test_build_rag_context(self):
        """Test RAG context assembly"""
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

class TestTrainingIngest:
    def test_ingest_text(self, tmp_path):
        """Test text file ingestion"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Sample trading content about EURUSD")
        
        content = ingest_document(str(test_file))
        assert content is not None
        assert "EURUSD" in content
        
    def test_ingest_markdown(self, tmp_path):
        """Test markdown file ingestion"""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Trading\nContent about M15 timeframe")
        
        content = ingest_document(str(test_file))
        assert content is not None
        assert "M15" in content


class TestChunker:
    def test_chunk_text(self):
        """Test text chunking"""
        text = "Sentence one. " * 50
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) > 0
        assert all(len(c) > 10 for c in chunks)
        
    def test_chunk_markdown(self):
        """Test markdown chunking"""
        md = "# Heading One\nContent here.\n## Heading Two\nMore content."
        chunks = chunk_markdown(md)
        assert len(chunks) > 0


class TestAutoTag:
    def test_tag_symbol(self):
        """Test symbol auto-tagging"""
        text = "Analysis of EURUSD on the H1 timeframe"
        tags = auto_tag(text)
        assert 'EURUSD' in tags['symbols']
        assert 'H1' in tags['timeframes']
        
    def test_tag_method(self):
        """Test method auto-tagging"""
        text = "Smart money accumulation and order block pattern"
        tags = auto_tag(text)
        assert 'SMC' in tags['methods']
        
    def test_tag_concept(self):
        """Test concept auto-tagging"""
        text = "The fair value gap is an important concept"
        tags = auto_tag(text)
        assert len(tags['tags']) > 0


# ============================================================================
# LLM & ORCHESTRATOR TESTS
# ============================================================================

class TestLocalLLMClient:
    def test_llm_initialization(self):
        """Test LLM client init"""
        client = LocalLLMClient()
        assert client.model == "gemma:7b"
        assert client.temperature == 0.3
        
    def test_llm_not_available_graceful(self):
        """Test LLM gracefully handles unavailability"""
        client = LocalLLMClient()
        # Should not crash if Ollama not running
        result = client.json_parse_response("{}")
        assert isinstance(result, dict)


class TestOrchestrator:
    def test_orchestrator_initialization(self):
        """Test orchestrator init"""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        assert orch.mt5_client is not None
        assert orch.risk_guardian is not None
        
    def test_orchestrator_health_check(self):
        """Test orchestrator health check"""
        orch = Orchestrator(use_llm=False, use_rag=False)
        health = orch.health_check()
        assert 'timestamp' in health
        assert 'components' in health


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

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
