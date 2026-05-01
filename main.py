#!/usr/bin/env python3
"""
Trade-CLI — Entry point principal.
Usa o launcher interactivo quando chamado sem argumentos.
Usa o CLI Typer directamente quando há argumentos.

Fase: 2.3
Data: 2026-05-01
"""
import sys
from pathlib import Path

# Garantir que o projecto está no path
sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    from cli.launcher import main as launcher_main
    launcher_main()


if __name__ == "__main__":
    main()
