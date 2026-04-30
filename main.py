"""
Trade-CLI - Main Entry Point

Phase 1: Terminal CLI with core subcommands
Date: 2025-04-30
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from cli.main import app

if __name__ == "__main__":
    app()
