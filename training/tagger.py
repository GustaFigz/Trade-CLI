"""
Auto-Tagging System — Trade-CLI Phase 2

Automatically tag chunks with metadata (symbol, method, confidence, etc).
"""

from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


def auto_tag(text: str, filename: str = "") -> Dict[str, Any]:
    """
    Automatically tag a chunk with metadata.
    
    Args:
        text: Chunk text
        filename: Source filename (optional)
        
    Returns:
        Dict with tags, symbol, method, confidence, category
    """
    tags = []
    symbols = []
    methods = []
    category = "general"
    confidence = 0.7  # Default confidence
    
    # Check for currency pairs
    pairs = ['EURUSD', 'USDJPY', 'USDCAD', 'GBPUSD', 'AUDUSD', 'NZDUSD',
             'EUROGBP', 'EURJPY', 'US30', 'NAS100', 'SP500', 'DAX', 'OIL', 'GOLD']
    
    for pair in pairs:
        if re.search(rf'\b{pair}\b', text, re.IGNORECASE):
            symbols.append(pair)
            tags.append(f"pair:{pair}")
    
    # Check for methods/concepts
    method_keywords = {
        'ICT': ['ICT', 'internal', 'market structure', 'liquidity void', 'equal highs/lows'],
        'SMC': ['smart money', 'liquidity sweep', 'order block', 'fair value gap', 'FVG'],
        'Wyckoff': ['wyckoff', 'accumulation', 'distribution', 'spring', 'shakeout'],
        'Price Action': ['price action', 'candlestick', 'support', 'resistance', 'breakout'],
        'Volume Profile': ['volume profile', 'POC', 'VPM', 'volume weighted'],
        'Elliott Wave': ['elliott', 'impulse', 'corrective', 'wave', 'zigzag'],
        'Macro': ['macro', 'inflation', 'interest rate', 'GDP', 'central bank', 'Fed'],
        'Technical': ['technical', 'MACD', 'RSI', 'stochastic', 'moving average', 'fibonacci'],
    }
    
    for method, keywords in method_keywords.items():
        for keyword in keywords:
            if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                methods.append(method)
                tags.append(f"method:{method}")
                break
    
    # Check for concepts
    concept_keywords = {
        'liquidity_sweep': ['sweep', 'liquidity grab', 'take liquidity'],
        'order_block': ['order block', 'OB', 'institutional'],
        'fair_value_gap': ['fair value gap', 'FVG', 'imbalance'],
        'market_structure': ['structure', 'swing high', 'swing low', 'HTF'],
        'confluence': ['confluence', 'confluence level', 'cluster'],
        'invalidation': ['invalidation', 'invalidate', 'break'],
    }
    
    for concept, keywords in concept_keywords.items():
        for keyword in keywords:
            if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                tags.append(f"concept:{concept}")
                break
    
    # Check for timeframe
    timeframe_keywords = {
        'M1': ['1 minute', 'M1', '1m'],
        'M5': ['5 minute', 'M5', '5m'],
        'M15': ['15 minute', 'M15', '15m'],
        'H1': ['hourly', 'H1', '1h', '1hour'],
        'H4': ['4 hour', 'H4', '4h'],
        'D1': ['daily', 'D1', '1d', 'daily chart'],
        'W1': ['weekly', 'W1', '1w'],
    }
    
    timeframes = []
    for tf, keywords in timeframe_keywords.items():
        for keyword in keywords:
            if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                timeframes.append(tf)
                tags.append(f"tf:{tf}")
                break
    
    # Determine category based on content
    if any(keyword in text.lower() for keyword in ['error', 'loss', 'failed', 'mistake', 'wrong']):
        category = "lesson_learned"
        confidence = 0.8
        tags.append("lesson")
    elif any(keyword in text.lower() for keyword in ['backtest', 'historical', 'past', 'result']):
        category = "backtesting"
        tags.append("historical")
    elif any(keyword in text.lower() for keyword in ['setup', 'pattern', 'playbook', 'checklist']):
        category = "playbook"
        tags.append("playbook")
    elif any(keyword in text.lower() for keyword in ['concept', 'theory', 'explanation', 'definition']):
        category = "educational"
        tags.append("educational")
    
    # Check filename for hints
    if 'post-mortem' in filename.lower() or 'pm' in filename.lower():
        category = "post_mortem"
        confidence = 0.9
        tags.append("post-mortem")
    elif 'playbook' in filename.lower():
        category = "playbook"
        confidence = 0.9
        tags.append("playbook")
    elif 'thesis' in filename.lower():
        category = "thesis"
        tags.append("thesis")
    
    # Remove duplicates
    symbols = list(set(symbols))
    methods = list(set(methods))
    tags = list(set(tags))
    
    return {
        'category': category,
        'symbols': symbols,
        'methods': methods,
        'timeframes': timeframes,
        'tags': tags,
        'confidence': min(confidence + 0.1 * len(methods), 0.95),  # Boost confidence with methods found
        'has_metadata': len(symbols) > 0 or len(methods) > 0,
    }


def tag_batch(chunks: List[str], filenames: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Tag multiple chunks.
    
    Args:
        chunks: List of text chunks
        filenames: Optional list of source filenames
        
    Returns:
        List of chunk dicts with metadata
    """
    if filenames is None:
        filenames = [""] * len(chunks)
    
    results = []
    for chunk, filename in zip(chunks, filenames):
        tags = auto_tag(chunk, filename)
        results.append({
            'text': chunk,
            'filename': filename,
            'metadata': tags,
        })
    
    logger.info(f"Tagged {len(chunks)} chunks")
    return results
