"""
Context Builder — Trade-CLI Phase 2

Assembles retrieved chunks into structured LLM prompt context.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds structured context for LLM prompts."""
    
    def __init__(self, symbol: str = "EURUSD", timeframe: str = "H1"):
        """
        Initialize context builder.
        
        Args:
            symbol: Currency pair
            timeframe: Trading timeframe
        """
        self.symbol = symbol
        self.timeframe = timeframe
    
    def build_rag_context(self, retrieved_chunks: List[Dict[str, Any]], 
                         max_tokens: int = 2000) -> str:
        """
        Build RAG context from retrieved chunks.
        
        Args:
            retrieved_chunks: List of chunk results from RAGRetriever
            max_tokens: Maximum tokens in context
            
        Returns:
            Formatted context string for LLM
        """
        if not retrieved_chunks:
            return "No relevant context found in knowledge base."
        
        context = "# Relevant Knowledge Base Context\n\n"
        token_count = 0
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            similarity = chunk.get('similarity', 0.0)
            
            # Format chunk
            chunk_text = f"## Chunk {i} (Relevance: {similarity:.1%})\n"
            chunk_text += f"Source: {metadata.get('source', 'unknown')}\n"
            
            if metadata.get('symbol'):
                chunk_text += f"Symbol: {metadata['symbol']}\n"
            
            if metadata.get('tags'):
                chunk_text += f"Tags: {', '.join(metadata['tags'])}\n"
            
            chunk_text += f"\n{text}\n\n"
            
            # Check token limit (rough estimate: 1 token ~= 4 chars)
            estimated_tokens = len(chunk_text) // 4
            if token_count + estimated_tokens > max_tokens:
                logger.info(f"Context limit reached after {i-1} chunks")
                break
            
            context += chunk_text
            token_count += estimated_tokens
        
        return context
    
    def build_analysis_context(self, technical_data: Dict[str, Any],
                               retrieved_context: str) -> str:
        """
        Build full analysis context with technical data + RAG.
        
        Args:
            technical_data: Dict with technical analysis scores
            retrieved_context: RAG context from build_rag_context
            
        Returns:
            Full context for LLM
        """
        context = f"# Analysis Context for {self.symbol} {self.timeframe}\n\n"
        
        # Add technical summary
        context += "## Current Technical State\n"
        context += f"Symbol: {self.symbol}\n"
        context += f"Timeframe: {self.timeframe}\n"
        context += f"Bias: {technical_data.get('bias', 'unknown')}\n"
        context += f"Confidence: {technical_data.get('confidence', 0.0):.1%}\n"
        context += f"Alignment Score: {technical_data.get('alignment_score', 0.0):.1%}\n"
        context += "\n"
        
        # Add engine scores
        context += "## Engine Scores\n"
        for engine_name, score in technical_data.get('engine_scores', {}).items():
            context += f"- {engine_name}: {score:.1%}\n"
        context += "\n"
        
        # Add invalidations
        if technical_data.get('invalidations'):
            context += "## Invalidation Levels\n"
            for inv in technical_data['invalidations']:
                context += f"- {inv}\n"
            context += "\n"
        
        # Add risk notes
        if technical_data.get('risk_notes'):
            context += "## Risk Factors\n"
            for risk in technical_data['risk_notes']:
                context += f"- {risk}\n"
            context += "\n"
        
        # Add RAG context
        context += "## Knowledge Base Context\n"
        context += retrieved_context
        
        return context
    
    def build_prompt_for_synthesis(self, analysis_context: str, 
                                    user_query: Optional[str] = None) -> str:
        """
        Build final prompt for LLM synthesis.
        
        Args:
            analysis_context: Context from build_analysis_context
            user_query: Optional user question
            
        Returns:
            Complete prompt for LLM
        """
        prompt = analysis_context
        
        if user_query:
            prompt += f"\n## User Question\n{user_query}\n"
        
        prompt += f"""
## Task

Synthesize the above technical analysis and knowledge base context into a concise trading thesis for {self.symbol} on the {self.timeframe} timeframe.

Include:
1. **Bias**: bullish, bearish, or neutral (with confidence)
2. **Setup**: What price action pattern or setup is present?
3. **Edge**: Why is this setup potentially profitable?
4. **Invalidation**: At what price/condition should we abandon this thesis?
5. **Risk Assessment**: What can go wrong?
6. **Confidence Level**: High (80%+), Medium (50-79%), or Low (<50%)

Be concise and specific. Reference the knowledge base if relevant.
"""
        
        return prompt
