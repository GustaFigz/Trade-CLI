"""
Local LLM Client — Trade-CLI Phase 2

Gemma 7B via Ollama (local, free, offline).
No cloud dependencies, no API keys.
"""

from typing import Optional, Dict, Any, List
import logging
import json

logger = logging.getLogger(__name__)

# Global Ollama client (lazy loaded)
_OLLAMA_CLIENT = None


def get_ollama_client():
    """
    Get Ollama client (lazy initialization).
    
    Returns:
        ollama module, or None if unavailable
    """
    global _OLLAMA_CLIENT
    
    if _OLLAMA_CLIENT is not None:
        return _OLLAMA_CLIENT
    
    try:
        import ollama
        logger.info("Ollama module loaded")
        _OLLAMA_CLIENT = ollama
        return _OLLAMA_CLIENT
    except ImportError:
        logger.error("Ollama Python client not installed. Install with: pip install ollama")
        return None


class LocalLLMClient:
    """
    Client for local LLM via Ollama.
    Uses Gemma 7B model.
    """
    
    def __init__(self, model: str = "gemma:7b", temperature: float = 0.3):
        """
        Initialize LLM client.
        
        Args:
            model: Ollama model name (default: gemma:7b)
            temperature: Temperature (0.0-1.0, lower = more deterministic)
        """
        self.model = model
        self.temperature = temperature
        self.ollama = get_ollama_client()
        self.available = self.ollama is not None
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        if not self.available:
            return False
        
        try:
            # Try to list models
            models = self.ollama.list()
            model_names = [m['name'] for m in models.get('models', [])]
            available = any(self.model in name for name in model_names)
            
            if available:
                logger.info(f"LLM model '{self.model}' is available")
            else:
                logger.warning(f"LLM model '{self.model}' not found. Run: ollama pull {self.model}")
            
            return available
        except Exception as e:
            logger.warning(f"Cannot reach Ollama: {e}. Make sure 'ollama serve' is running.")
            return False
    
    def chat(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Send chat request to LLM.
        
        Args:
            messages: List of {role, content} dicts
            
        Returns:
            LLM response text, or None if failed
        """
        if not self.available:
            logger.error("LLM not available")
            return None
        
        try:
            response = self.ollama.chat(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            
            return response.get('message', {}).get('content', '').strip()
        except Exception as e:
            logger.error(f"LLM chat failed: {e}")
            return None
    
    def generate_thesis(self, context: str) -> Optional[str]:
        """
        Generate trading thesis from analysis context.
        
        Args:
            context: Full analysis context
            
        Returns:
            LLM-generated thesis, or None if failed
        """
        if not self.available:
            logger.error("LLM not available")
            return None
        
        messages = [
            {
                "role": "user",
                "content": context
            }
        ]
        
        return self.chat(messages)
    
    def explain_verdict(self, analysis: Dict[str, Any], verdict: str) -> Optional[str]:
        """
        Generate explanation for analysis verdict.
        
        Args:
            analysis: Analysis dict with bias, scores, etc.
            verdict: Verdict ("allowed", "watch_only", "blocked")
            
        Returns:
            LLM explanation, or None if failed
        """
        if not self.available:
            return None
        
        prompt = f"""
Given this trading analysis:
- Symbol: {analysis.get('symbol')}
- Timeframe: {analysis.get('timeframe')}
- Bias: {analysis.get('bias')}
- Confidence: {analysis.get('confidence', 0.0):.1%}
- Alignment Score: {analysis.get('alignment_score', 0.0):.1%}
- Verdict: {verdict}

Provide a brief (2-3 sentences) explanation of why this verdict was given.
Be concise and professional.
"""
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return self.chat(messages)
    
    def synthesize_engines(self, engine_outputs: List[Dict[str, Any]]) -> Optional[str]:
        """
        Synthesize multiple engine outputs into consensus.
        
        Args:
            engine_outputs: List of engine output dicts
            
        Returns:
            LLM synthesis, or None if failed
        """
        if not self.available:
            return None
        
        # Format engine outputs
        engines_text = ""
        for output in engine_outputs:
            engines_text += f"""
## {output.get('engine_name')}
Score: {output.get('score', 0.0):.1%}
Explanation: {output.get('explanation')}
"""
        
        prompt = f"""
Below are outputs from multiple trading analysis engines.

{engines_text}

Synthesize these outputs into a single, coherent analysis. 
Note any conflicts between engines.
Provide a consensus bias (bullish/bearish/neutral).
Give an overall confidence level.

Keep response concise (5-7 sentences).
"""
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return self.chat(messages)
    
    def json_parse_response(self, response_text: str, fallback: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Try to parse LLM response as JSON.
        Useful for structured outputs.
        
        Args:
            response_text: LLM response
            fallback: Dict to return if parsing fails
            
        Returns:
            Parsed JSON dict, or fallback
        """
        if not response_text:
            return fallback or {}
        
        try:
            # Try to find JSON block
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON from LLM response: {e}")
        
        return fallback or {}
