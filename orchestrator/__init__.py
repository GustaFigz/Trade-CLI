"""
LLM Orchestrator — Trade-CLI Phase 2

Gemma 7B via Ollama (local, free, offline)
- Decides which engines to run
- Synthesizes engine outputs
- Provides reasoning to user
- No cloud dependencies
"""

from orchestrator.llm_client import LocalLLMClient
from orchestrator.orchestrator import Orchestrator

__all__ = [
    "LocalLLMClient",
    "Orchestrator"
]
