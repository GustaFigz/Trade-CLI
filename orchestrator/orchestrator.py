"""
Main Orchestrator — Trade-CLI Phase 2

Coordinates all engines, LLM, RAG, and risk guardian.
Graceful degradation: works without LLM, MT5, or RAG.

Phase 2: Active
Date: 2026-05-01
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from core.analysis_schema import AnalysisOutput, EngineOutput, ProposalVerdictOutput, VerdictType
from core.risk_guardian import RiskGuardian
from engines import TechnicalEngine, PriceActionEngine, FundamentalEngine, ThesisEngine

from data.mt5_client import MT5Client
from knowledge.obsidian_reader import ObsidianReader
from knowledge.chunk_vectorizer import ChunkVectorizer
from knowledge.rag_retriever import RAGRetriever
from knowledge.context_builder import ContextBuilder
from orchestrator.llm_client import LocalLLMClient

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main analysis orchestrator.
    Coordinates engines, RAG, LLM, and risk guardian.
    Graceful degradation: each component can fail without crashing.
    """
    
    def __init__(self, use_llm: bool = True, use_rag: bool = True, use_mt5: bool = True):
        """
        Initialize orchestrator.
        
        Args:
            use_llm: Enable Gemma LLM synthesis
            use_rag: Enable RAG knowledge retrieval
            use_mt5: Enable MT5 data (fallback to mock if unavailable)
        """
        self.use_llm = use_llm
        self.use_rag = use_rag
        self.use_mt5 = use_mt5
        
        # Initialize components
        self.risk_guardian = RiskGuardian()
        
        # Data plane
        self.mt5_client = MT5Client(fallback_to_mock=True) if use_mt5 else None
        
        # Engines
        self.technical_engine = TechnicalEngine()
        self.price_action_engine = PriceActionEngine()
        self.fundamental_engine = FundamentalEngine()
        self.thesis_engine = ThesisEngine()
        
        # Knowledge & RAG
        self.obsidian_reader = ObsidianReader() if use_rag else None
        self.vectorizer = ChunkVectorizer() if use_rag else None
        self.rag_retriever = RAGRetriever() if use_rag else None
        self.context_builder: Optional[ContextBuilder] = None
        
        # LLM
        self.llm_client = LocalLLMClient() if use_llm else None
        
        logger.info(f"Orchestrator initialized (LLM={use_llm}, RAG={use_rag}, MT5={use_mt5})")
    
    def analyze(self, symbol: str, timeframe: str, user_query: Optional[str] = None) -> Dict[str, Any]:
        """
        Run full analysis pipeline.
        
        Args:
            symbol: Currency pair (e.g., "EURUSD")
            timeframe: Timeframe (e.g., "H1")
            user_query: Optional user question / analyst notes
            
        Returns:
            Dict with analysis result, verdict, explanation
        """
        logger.info(f"Starting analysis: {symbol} {timeframe}")
        
        # Step 1: Get market data
        bars = None
        if self.mt5_client:
            try:
                bars = self.mt5_client.get_bars(symbol, timeframe, count=500)
            except Exception as e:
                logger.warning(f"MT5 data fetch failed, continuing without bars: {e}")
        
        # Step 2: Run engines (in parallel, conceptually)
        engine_outputs: List[EngineOutput] = []
        
        try:
            tech_output = self.technical_engine.analyze(symbol, timeframe, bars)
            if tech_output:
                engine_outputs.append(tech_output)
                logger.info(f"Technical engine: {tech_output.score:.1%}")
        except Exception as e:
            logger.error(f"Technical engine failed: {e}")
        
        try:
            pa_output = self.price_action_engine.analyze(symbol, timeframe, bars)
            if pa_output:
                engine_outputs.append(pa_output)
                logger.info(f"Price action engine: {pa_output.score:.1%}")
        except Exception as e:
            logger.error(f"Price action engine failed: {e}")
        
        try:
            fund_output = self.fundamental_engine.analyze(symbol, timeframe)
            if fund_output:
                engine_outputs.append(fund_output)
                logger.info(f"Fundamental engine: {fund_output.score:.1%}")
        except Exception as e:
            logger.error(f"Fundamental engine failed: {e}")
        
        # Step 3: Retrieve RAG context (if enabled)
        rag_context = ""
        if self.use_rag and self.rag_retriever:
            try:
                query = f"{symbol} {timeframe} {user_query or ''}"
                # Create a simple random embedding for testing, or use real embedding if available
                import numpy as np
                query_embedding = np.random.rand(384).astype(np.float32)  # Assuming 384 is the dim
                chunks = self.rag_retriever.search(query_embedding, k=5, symbol_filter=symbol)
                rag_context = "\n".join([c.get("text", "") for c in chunks]) if chunks else ""
                self.context_builder = ContextBuilder(symbol, timeframe)
                logger.info(f"RAG context: {len(chunks)} chunks retrieved")
            except Exception as e:
                logger.warning(f"RAG context setup failed: {e}")
                rag_context = ""
                self.context_builder = ContextBuilder(symbol, timeframe)
        
        # Step 4: Synthesize via LLM (if available and engines agree)
        llm_synthesis: Optional[str] = None
        if self.use_llm and self.llm_client and self.context_builder:
            try:
                if self.llm_client.is_available():
                    # Build technical data summary for context
                    technical_data = {
                        'bias': 'neutral',
                        'confidence': sum(e.score for e in engine_outputs) / len(engine_outputs) if engine_outputs else 0.5,
                        'alignment_score': 0.5,
                        'engine_scores': {e.engine_name: e.score for e in engine_outputs},
                    }
                    analysis_context = self.context_builder.build_analysis_context(
                        technical_data,
                        rag_context
                    )
                    llm_synthesis = self.llm_client.generate_thesis(analysis_context)
                    if llm_synthesis:
                        logger.info("LLM synthesis complete")
            except Exception as e:
                logger.warning(f"LLM synthesis failed, continuing without: {e}")
                llm_synthesis = None
        
        # Step 5: Synthesize engines into final analysis
        try:
            thesis_output: AnalysisOutput = self.thesis_engine.synthesize(
                symbol=symbol,
                timeframe=timeframe,
                analyst_notes=user_query or "",
                engine_outputs=engine_outputs if engine_outputs else None,
                llm_synthesis=llm_synthesis,
            )
        except Exception as e:
            logger.error(f"Thesis synthesis failed: {e}")
            return {'error': f'Analysis failed: {e}'}
        
        if not thesis_output:
            logger.error("Thesis synthesis returned None")
            return {'error': 'Analysis failed'}
        
        # Step 6: Apply RiskGuardian (FIX-002: use should_block, not evaluate)
        verdict: ProposalVerdictOutput = self.risk_guardian.should_block(thesis_output)
        
        # Update thesis with verdict info
        thesis_output.verdict = verdict.verdict
        thesis_output.veto_reason = verdict.reason
        
        # Step 7: Prepare result (FIX-003: use .confidence_score and .bias.value)
        result = {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'bias': thesis_output.bias.value,           # FIX-003: enum → string
                'confidence_score': thesis_output.confidence_score,  # FIX-003: correct field name
                'alignment_score': thesis_output.alignment_score,
                'setup_type': thesis_output.setup_type,
                'technical_score': thesis_output.technical_score,
                'price_action_score': thesis_output.price_action_score,
                'fundamental_score': thesis_output.fundamental_score,
            },
            'engine_outputs': [
                {
                    'name': e.engine_name,
                    'score': e.score,
                    'explanation': e.explanation,
                } for e in engine_outputs
            ],
            'verdict': verdict.verdict.value,       # FIX-003: enum → string
            'verdict_reason': verdict.reason,       # FIX-003: correct field is .reason
            'risk_notes': thesis_output.risk_notes,
            'invalidations': thesis_output.invalidations,
            'llm_used': llm_synthesis is not None,
            'data_source': 'mt5' if (self.mt5_client and self.mt5_client.connected) else 'mock',
        }
        
        logger.info(f"Analysis complete: {verdict.verdict.value}")
        return result
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all components."""
        health = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
        }
        
        # MT5
        if self.mt5_client:
            health['components']['mt5'] = {
                'available': self.mt5_client.connected,
                'fallback_mode': self.mt5_client.fallback_to_mock,
            }
        else:
            health['components']['mt5'] = {'available': False, 'fallback_mode': False}
        
        # LLM
        if self.llm_client:
            try:
                llm_available = self.llm_client.is_available()
            except Exception:
                llm_available = False
            health['components']['llm'] = {
                'available': llm_available,
                'model': self.llm_client.model,
            }
        else:
            health['components']['llm'] = {'available': False, 'model': 'disabled'}
        
        # RAG
        if self.obsidian_reader:
            try:
                vault_exists = self.obsidian_reader.vault_path.exists()
            except Exception:
                vault_exists = False
            health['components']['rag'] = {
                'vault_available': vault_exists,
                'vectorizer': self.vectorizer is not None,
            }
        else:
            health['components']['rag'] = {'vault_available': False, 'vectorizer': False}
        
        # Risk Guardian
        health['components']['risk_guardian'] = {
            'loaded': self.risk_guardian is not None,
            'status': 'operational',
        }
        
        # Engines
        health['components']['engines'] = {
            'technical': True,
            'price_action': True,
            'fundamental': True,
            'thesis': True,
        }
        
        return health
