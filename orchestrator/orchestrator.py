"""
Main Orchestrator — Trade-CLI Phase 2

Coordinates all engines, LLM, RAG, and risk guardian.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from core.analysis_schema import AnalysisOutput, EngineOutput, ProposalVerdictOutput
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
        self.context_builder = None
        
        # LLM
        self.llm_client = LocalLLMClient() if use_llm else None
        
        logger.info(f"Orchestrator initialized (LLM={use_llm}, RAG={use_rag}, MT5={use_mt5})")
    
    def analyze(self, symbol: str, timeframe: str, user_query: Optional[str] = None) -> Dict[str, Any]:
        """
        Run full analysis pipeline.
        
        Args:
            symbol: Currency pair (e.g., "EURUSD")
            timeframe: Timeframe (e.g., "H1")
            user_query: Optional user question
            
        Returns:
            Dict with analysis result, verdict, explanation
        """
        logger.info(f"Starting analysis: {symbol} {timeframe}")
        
        # Step 1: Get market data
        bars = None
        if self.mt5_client:
            bars = self.mt5_client.get_bars(symbol, timeframe, count=500)
        
        # Step 2: Run engines (in parallel, conceptually)
        engine_outputs = []
        
        tech_output = self.technical_engine.analyze(symbol, timeframe, bars)
        if tech_output:
            engine_outputs.append(tech_output)
            logger.info(f"Technical engine: {tech_output.score:.1%}")
        
        pa_output = self.price_action_engine.analyze(symbol, timeframe, bars)
        if pa_output:
            engine_outputs.append(pa_output)
            logger.info(f"Price action engine: {pa_output.score:.1%}")
        
        fund_output = self.fundamental_engine.analyze(symbol, timeframe)
        if fund_output:
            engine_outputs.append(fund_output)
            logger.info(f"Fundamental engine: {fund_output.score:.1%}")
        
        # Step 3: Retrieve RAG context (if enabled)
        rag_context = ""
        if self.use_rag and self.obsidian_reader:
            self.context_builder = ContextBuilder(symbol, timeframe)
            # Search for relevant knowledge
            # (In full implementation, would vectorize query and search)
            logger.info("RAG context retrieval enabled")
        
        # Step 4: Synthesize via LLM (if available and engines agree)
        llm_synthesis = None
        if self.use_llm and self.llm_client and self.llm_client.is_available():
            if self.context_builder:
                analysis_context = self.context_builder.build_analysis_context(
                    {'bias': 'neutral', 'confidence': 0.5, 'engine_scores': {}},
                    rag_context
                )
                llm_synthesis = self.llm_client.generate_thesis(analysis_context)
                if llm_synthesis:
                    logger.info("LLM synthesis complete")
        
        # Step 5: Synthesize engines
        thesis_output = self.thesis_engine.synthesize(
            symbol=symbol,
            timeframe=timeframe,
            engine_outputs=engine_outputs,
            llm_synthesis=llm_synthesis
        )
        
        if not thesis_output:
            logger.error("Thesis synthesis failed")
            return {'error': 'Analysis failed'}
        
        # Step 6: Apply RiskGuardian
        verdict = self.risk_guardian.evaluate(thesis_output)
        
        # Step 7: Prepare result
        result = {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'bias': thesis_output.bias,
                'confidence': thesis_output.confidence,
                'alignment_score': thesis_output.alignment_score,
                'setup_type': thesis_output.setup_type,
            },
            'engine_outputs': [
                {
                    'name': e.engine_name,
                    'score': e.score,
                    'explanation': e.explanation,
                } for e in engine_outputs
            ],
            'verdict': verdict.verdict,
            'verdict_reason': verdict.reasoning,
            'risk_notes': thesis_output.risk_notes,
            'invalidations': thesis_output.invalidations,
        }
        
        logger.info(f"Analysis complete: {verdict.verdict}")
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
        
        # LLM
        if self.llm_client:
            health['components']['llm'] = {
                'available': self.llm_client.is_available(),
                'model': self.llm_client.model,
            }
        
        # RAG
        if self.obsidian_reader:
            vault_exists = self.obsidian_reader.vault_path.exists()
            health['components']['rag'] = {
                'vault_available': vault_exists,
                'vectorizer': self.vectorizer is not None,
            }
        
        # Risk Guardian
        health['components']['risk_guardian'] = {
            'loaded': self.risk_guardian is not None,
        }
        
        return health
