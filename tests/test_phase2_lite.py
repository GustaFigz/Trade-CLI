"""
Phase 2.2 Lightweight Tests — Quick validation without heavy model loading

Knowledge/training tests are marked @pytest.mark.slow
since their modules may import heavy ML libraries.
"""

import pytest
from pathlib import Path
import pandas as pd

# Data Plane (light — always imported)
from data.mt5_client import MT5Client
from data.mock_data import get_mock_bars, get_mock_ticks, get_mock_account_state

# LLM (uses httpx — lightweight)
from orchestrator.llm_client import LLMClient


# ============================================================================
# DATA PLANE TESTS
# ============================================================================

def test_mt5_fallback_mode():
    """Test MT5 client with mock fallback"""
    client = MT5Client(fallback_to_mock=True)
    assert client.connect()


def test_get_mock_bars():
    """Test mock bar generation"""
    bars = get_mock_bars("EURUSD", "H1", count=100)
    assert len(bars) == 100
    assert 'open' in bars.columns
    assert 'close' in bars.columns
    assert bars['close'].dtype in ['float64', 'float32']


def test_get_mock_ticks():
    """Test mock tick generation"""
    ticks = get_mock_ticks("USDJPY", count=500)
    assert len(ticks) == 500
    assert 'bid' in ticks.columns
    assert 'ask' in ticks.columns


def test_mock_account_state():
    """Test mock account state"""
    state = get_mock_account_state()
    assert state['balance'] == 100000
    assert state['equity'] == 98500


# ============================================================================
# KNOWLEDGE & RAG TESTS
# ============================================================================

@pytest.mark.slow
def test_vault_exists():
    """Test Obsidian vault is loaded"""
    from knowledge.obsidian_reader import ObsidianReader
    reader = ObsidianReader("Trade-CLI-Vault")
    assert reader.vault_path.exists()


@pytest.mark.slow
def test_split_chunks():
    """Test text chunking"""
    from knowledge.chunk_vectorizer import split_into_chunks
    text = "This is a test sentence. " * 50
    chunks = split_into_chunks(text, chunk_size=100, overlap=10)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


@pytest.mark.slow
def test_context_builder():
    """Test context building"""
    from knowledge.context_builder import ContextBuilder
    builder = ContextBuilder("EURUSD", "H1")
    assert builder.symbol == "EURUSD"
    assert builder.timeframe == "H1"


@pytest.mark.slow
def test_build_rag_context():
    """Test RAG context assembly"""
    from knowledge.context_builder import ContextBuilder
    builder = ContextBuilder("EURUSD", "H1")
    chunks = [
        {
            'text': 'Sample context about order blocks and smart money',
            'metadata': {'source': 'playbooks', 'symbol': 'EURUSD'},
            'similarity': 0.85
        }
    ]
    context = builder.build_rag_context(chunks)
    assert len(context) > 0
    assert 'order blocks' in context


# ============================================================================
# TRAINING TESTS
# ============================================================================

@pytest.mark.slow
def test_ingest_text(tmp_path):
    """Test text file ingestion"""
    from training.ingest import ingest_text
    test_file = tmp_path / "test.txt"
    test_file.write_text("Sample trading content about EURUSD and H1 timeframe")
    
    content = ingest_text(str(test_file))
    assert content is not None
    assert "EURUSD" in content
    assert "H1" in content


@pytest.mark.slow
def test_chunk_text_lite():
    """Test text chunking"""
    from training.chunker import chunk_text
    text = "Sentence one. " * 50
    chunks = chunk_text(text, chunk_size=100)
    assert len(chunks) > 0
    assert all(len(c) > 10 for c in chunks)


@pytest.mark.slow
def test_auto_tag_symbol():
    """Test symbol auto-tagging"""
    from training.tagger import auto_tag
    text = "Analysis of EURUSD on the H1 timeframe with order blocks"
    tags = auto_tag(text)
    assert 'EURUSD' in tags['symbols']
    assert 'H1' in tags['timeframes']


@pytest.mark.slow
def test_auto_tag_method():
    """Test method auto-tagging"""
    from training.tagger import auto_tag
    text = "Smart money accumulation and order block pattern analysis"
    tags = auto_tag(text)
    assert 'SMC' in tags['methods']


@pytest.mark.slow
def test_auto_tag_concept():
    """Test concept auto-tagging"""
    from training.tagger import auto_tag
    text = "The fair value gap is an important ICT concept for price action"
    tags = auto_tag(text)
    assert len(tags['tags']) > 0


# ============================================================================
# LLM & ORCHESTRATOR TESTS
# ============================================================================

def test_llm_initialization():
    """Test LLM client initialization"""
    client = LLMClient()
    assert client.ollama_model == "gemma4:e4b"
    assert client.timeout == 120


def test_llm_is_available():
    """Test LLM availability check (should not crash)"""
    client = LLMClient()
    result = client.is_available()
    assert isinstance(result, bool)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_data_pipeline():
    """Test data retrieval pipeline"""
    client = MT5Client(fallback_to_mock=True)
    client.connect()
    
    bars = client.get_bars("EURUSD", "H1", count=50)
    assert bars is not None
    assert len(bars) == 50
    assert 'close' in bars.columns


@pytest.mark.slow
def test_training_pipeline(tmp_path):
    """Test training ingestion pipeline"""
    from training.ingest import ingest_text
    from training.chunker import chunk_text
    from training.tagger import auto_tag
    
    # Create test file
    test_file = tmp_path / "trading_guide.txt"
    test_file.write_text("""
    EURUSD Playbook on H1
    Setup: Order block on H4
    Timeframe: H15, H1
    Confidence: High
    """)
    
    # Ingest
    text = ingest_text(str(test_file))
    assert text is not None
    assert "EURUSD" in text
    
    # Chunk
    chunks = chunk_text(text, chunk_size=100)
    assert len(chunks) > 0
    
    # Tag
    tags_found = False
    for chunk in chunks:
        tags = auto_tag(chunk)
        if 'EURUSD' in tags.get('symbols', []):
            tags_found = True
    assert tags_found  # At least one chunk should be tagged


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
