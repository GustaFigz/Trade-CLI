# 🗺️ Trade-CLI — Plano de Acção Completo (Fase 3)
> Análise cirúrgica do código real + guia de implementação passo-a-passo  
> Data: Maio 2026 | Repositório: [GustaFigz/Trade-CLI](https://github.com/GustaFigz/Trade-CLI)

---

## 📊 Estado Real do Projecto

### ✅ O que já existe e funciona
- `main.py` — entry point correcto, delega para `cli/launcher.py`
- `pyproject.toml` — scripts `tradecli` e `trade-cli` **já definidos** mas com entry point errado
- `cli/launcher.py` — REPL Rich completo, splash, boot sequence, status panel, help table
- `cli/main.py` — Typer com comandos: `init`, `analyze`, `health`, `version`, `db-setup`, `show`, `train`, `knowledge`, `outcome`, `review`, `assets`, `tui`
- `orchestrator/llm_client.py` — Ollama httpx directo + fallback OpenAI-compatible
- `orchestrator/chat_engine.py` — RAG + LLM + histórico de sessão (em memória)
- `orchestrator/orchestrator.py` — pipeline completo: MT5 → engines → RAG → LLM → RiskGuardian
- `core/risk_guardian.py` + `core/analysis_schema.py` — regras FTMO e schema de análise
- `engines/__init__.py` — TechnicalEngine, PriceActionEngine, FundamentalEngine, ThesisEngine
- `cli/tui/app.py` — TradeCLIApp Textual existe mas tem bugs críticos
- `cli/tui/screens/dashboard.py` — DashboardScreen com 3 colunas
- `cli/tui/widgets/` — 4 widgets: `candle_chart.py`, `engine_scores.py`, `verdict_panel.py`, `asset_sidebar.py`
- `cli/tui/theme/trade_cli.tcss` — tema CSS Textual completo (dark trading palette)

### ❌ Bugs Críticos Identificados (por ficheiro)

#### Bug 1 — `cli/tui/app.py` — `os.chdir()` perigoso no `__init__`
```python
# LINHA ACTUAL (quebrado):
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
# Muda o CWD global da aplicação. Parte qualquer path relativo depois disto.
```

#### Bug 2 — `cli/tui/app.py` — CSS_PATH inconsistente com os.chdir()
```python
# ACTUAL (ambíguo após os.chdir):
CSS_PATH = "theme/trade_cli.tcss"
# Textual resolve CSS_PATH relativo ao ficheiro .py,
# mas o os.chdir() causa conflito de CWD.
```

#### Bug 3 — `pyproject.toml` — entry point aponta para módulo raiz
```toml
# ACTUAL (quebrado após install com pipx):
tradecli = "main:main"
# O módulo "main" da raiz não fica no sys.path após install global.
```

#### Bug 4 — `orchestrator/llm_client.py` — modelo default errado
```python
# ACTUAL:
self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma3:latest")
```

#### Bug 5 — `cli/launcher.py` — modelo default errado em `_check_ollama()`
```python
# ACTUAL:
model = os.getenv("OLLAMA_MODEL", "gemma3:latest")
```

#### Bug 6 — `.env.example` — modelo default errado
```env
# ACTUAL:
OLLAMA_MODEL=gemma3:latest
```

#### Bug 7 — `cli/launcher.py` — LLM sem streaming (bloqueia terminal)
```python
# No llm_client.py _chat_ollama:
"stream": False   # bloqueia até a resposta estar 100% completa
```

#### Bug 8 — `cli/launcher.py` — `console.input()` sem histórico nem autocomplete
```python
raw = console.input(Text.assemble(...).plain).strip()
# Rich input básico: sem setas ↑↓, sem histórico entre sessões
```

#### Bug 9 — `cli/launcher.py` — `_run_cli_command` usa ClickRunner (frágil)
```python
from click.testing import CliRunner
runner = CliRunner(mix_stderr=False)
result = runner.invoke(click_app, parts, catch_exceptions=False)
# CliRunner é para testes unitários, não para produção.
```

#### Bug 10 — `orchestrator/chat_engine.py` — histórico não persiste entre sessões
```python
self.session = ChatSession()  # apenas memória RAM — perde-se ao fechar
```

#### Bug 11 — `pyproject.toml` — falta `[tool.setuptools.packages.find]`
Sem isto, `pip install -e .` pode não incluir todos os sub-packages
(`cli`, `core`, `engines`, `orchestrator`, etc.).

#### Bug 12 — `requirements.txt` — falta `textual`
A TUI usa `textual` mas não está declarado em `requirements.txt`.

---

## 🔧 Implementação — Passo a Passo

---

### PASSO 1 — Instalar o modelo `gemma4:e4b`

```bash
# Garantir que Ollama está a correr
ollama serve &

# Instalar modelo
ollama pull gemma4:e4b

# Verificar
ollama list
# Deve mostrar: gemma4:e4b   ID   SIZE   MODIFIED
```

---

### PASSO 2 — Substituir `pyproject.toml`

Abre `pyproject.toml` na raiz do projecto e substitui o conteúdo **completo**:

```toml
[project]
name = "trade-cli"
version = "0.3.0"
description = "Local AI Trading Specialist — Forex Copilot for the Terminal"
requires-python = ">=3.11"
readme = "README.md"

[project.scripts]
tradecli = "cli.launcher:main"
trade-cli = "cli.launcher:main"

[tool.setuptools.packages.find]
where = ["."]
include = [
  "cli*", "core*", "engines*", "orchestrator*",
  "knowledge*", "db*", "data*", "training*",
  "config*"
]

[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "B"]
ignore = ["E501", "B008"]
exclude = [".venv", "dist", "build", "__pycache__"]

[tool.ruff.isort]
known-first-party = [
  "core", "engines", "data", "orchestrator",
  "training", "knowledge", "cli", "db"
]

[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short -m 'not slow'"
asyncio_mode = "auto"
markers = [
  "slow: testes pesados (sentence-transformers, RAG completo)",
  "integration: testes que requerem Ollama ou MT5",
  "unit: testes rápidos sem dependências externas",
]

[tool.coverage.run]
source = ["core", "engines", "data", "orchestrator", "training", "knowledge"]
omit = ["tests/*", "*/__init__.py", "*/migrations.py"]

[tool.coverage.report]
fail_under = 75
show_missing = true
```

---

### PASSO 3 — Substituir `requirements.txt`

Substitui o ficheiro `requirements.txt` completo:

```txt
# ─── CLI & Terminal ──────────────────────────────────────────
typer[all]==0.12.3
rich==13.7.0
click==8.1.7
prompt-toolkit>=3.0.47
textual>=0.59.0

# ─── Configuration ───────────────────────────────────────────
python-dotenv==1.0.1
pyyaml==6.0.1

# ─── Data & Analysis ─────────────────────────────────────────
pandas>=2.2.0
numpy>=1.26.4
ta>=0.11.0

# ─── HTTP (Ollama + calendário económico) ────────────────────
httpx>=0.27.0
requests>=2.31.0

# ─── Knowledge & RAG ─────────────────────────────────────────
scikit-learn>=1.4.0

# ─── Text Processing (training) ──────────────────────────────
pypdf>=4.2.0
markdown>=3.6
python-dateutil>=2.9.0

# ─── Logging estruturado ─────────────────────────────────────
structlog>=24.1.0

# ─── Scheduling ──────────────────────────────────────────────
schedule>=1.2.1

# ─── Testing ─────────────────────────────────────────────────
pytest>=8.2.0
pytest-cov>=5.0.0
pytest-asyncio>=0.23.6

# ─── Code Quality ────────────────────────────────────────────
ruff>=0.4.4
mypy>=1.10.0

# ─── MT5 (Windows only — descomentar quando necessário) ───────
# MetaTrader5>=5.0.45
```

---

### PASSO 4 — Actualizar `.env.example` e criar `.env`

Substitui `.env.example` completo:

```env
# ════════════════════════════════════════════════
# Trade-CLI — Environment Configuration
# Copiar para .env e preencher com valores reais
# NUNCA commitar o .env
# ════════════════════════════════════════════════

# ─── LLM Backend (Ollama — padrão local) ────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e4b
LLM_TIMEOUT_SECONDS=120

# ─── LLM Fallback OpenAI-compatible (OPCIONAL — deixar vazio)
LLM_API_BASE=
LLM_API_KEY=
LLM_MODEL=

# ─── MT5 (MetaTrader 5 — Phase 2.3+) ────────────────────────
MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=

# ─── Base de Dados ───────────────────────────────────────────
DB_PATH=database.db

# ─── Obsidian Vault ──────────────────────────────────────────
OBSIDIAN_VAULT_PATH=./Trade-CLI-Vault

# ─── Modo de Dados ───────────────────────────────────────────
MOCK_DATA=true

# ─── Sistema ─────────────────────────────────────────────────
LOG_LEVEL=INFO
LOG_FILE=trade-cli.log
TRADECLI_VERSION=0.3.0
```

Depois:

```bash
cp .env.example .env
```

---

### PASSO 5 — Editar `orchestrator/llm_client.py`

#### 5a — Mudar o modelo default

Localiza no `__init__` da classe `LLMClient`:

```python
# ANTES:
self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma3:latest")

# DEPOIS:
self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
```

#### 5b — Adicionar método `stream_chat()`

Adiciona este método à classe `LLMClient`, antes do método `generate_thesis`:

```python
def stream_chat(
    self,
    system: str,
    user: str,
    history=None,
    temperature: float = 0.3,
):
    """
    Streama a resposta token a token do Ollama.
    Yields: strings (chunks de texto) à medida que chegam.
    Se Ollama offline, faz yield de mensagem de erro e termina.
    """
    import json as _json

    if not self._is_ollama_up():
        yield (
            "⚠️  Ollama offline.\n"
            f"Inicia com: `ollama serve`\n"
            f"Instala o modelo: `ollama pull {self.ollama_model}`"
        )
        return

    messages = [{"role": "system", "content": system}]
    if history:
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user})

    payload = {
        "model": self.ollama_model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature},
    }

    try:
        with httpx.stream(
            "POST",
            f"{self.ollama_base}/api/chat",
            json=payload,
            timeout=self.timeout,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    try:
                        data = _json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk
                        if data.get("done"):
                            break
                    except _json.JSONDecodeError:
                        continue
    except Exception as e:
        log.error("stream_chat_failed", error=str(e))
        yield f"\n⚠️  Erro de streaming: {e}"
```

---

### PASSO 6 — Editar `orchestrator/chat_engine.py`

#### 6a — Adicionar imports no topo (após os imports existentes)

```python
import json
from pathlib import Path
```

#### 6b — Adicionar constantes antes da classe `ChatSession`

```python
_HISTORY_FILE = Path.home() / ".tradecli" / "chat_history.json"
_MAX_PERSIST = 40
```

#### 6c — Substituir o `__init__` da classe `ChatEngine`

```python
def __init__(self) -> None:
    self.llm = LLMClient()
    self.session = ChatSession()
    self._rag_available = self._init_rag()
    self._load_history()
```

#### 6d — Adicionar novos métodos à classe `ChatEngine`

Adiciona estes métodos após `_init_rag()`:

```python
def _load_history(self) -> None:
    """Carrega histórico persistido da sessão anterior."""
    try:
        _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if _HISTORY_FILE.exists():
            data = json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
            for msg in data[-_MAX_PERSIST:]:
                self.session.add(msg["role"], msg["content"])
            log.info("history_loaded", messages=len(self.session.history))
    except Exception as e:
        log.warning("history_load_failed", error=str(e))

def _save_history(self) -> None:
    """Persiste histórico em disco após cada troca."""
    try:
        data = [
            {"role": m.role, "content": m.content}
            for m in self.session.history[-_MAX_PERSIST:]
        ]
        _HISTORY_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log.warning("history_save_failed", error=str(e))

@property
def model_name(self) -> str:
    """Nome do modelo LLM activo."""
    return self.llm.ollama_model

def stream(self, user_message: str):
    """
    Stream da resposta token a token.
    Yields: chunks de texto.
    Actualiza e persiste o histórico após completar.
    """
    rag_context = self._get_rag_context(user_message)
    system = SPECIALIST_SYSTEM_PROMPT.format(rag_context=rag_context)
    full_response = ""
    for chunk in self.llm.stream_chat(
        system=system,
        user=user_message,
        history=self.session.history,
        temperature=0.3,
    ):
        full_response += chunk
        yield chunk
    self.session.add("user", user_message)
    self.session.add("assistant", full_response)
    self._save_history()
```

#### 6e — Actualizar o método `chat()` existente

Localiza o método `chat()` e adiciona `self._save_history()` após a linha de `session.add`:

```python
def chat(self, user_message: str) -> LLMResponse:
    rag_context = self._get_rag_context(user_message)
    system = SPECIALIST_SYSTEM_PROMPT.format(rag_context=rag_context)
    response = self.llm.chat(
        system=system,
        user=user_message,
        history=self.session.history,
        temperature=0.3,
    )
    self.session.add("user", user_message)
    self.session.add("assistant", response.content)
    self._save_history()   # ← linha nova
    return response
```

---

### PASSO 7 — Editar `cli/launcher.py`

#### 7a — Corrigir modelo default em `_check_ollama()`

```python
# ANTES:
model = os.getenv("OLLAMA_MODEL", "gemma3:latest")

# DEPOIS:
model = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
```

#### 7b — Adicionar função `_print_streaming_response()`

Adiciona esta função após `print_analyzing()`, antes de `boot_sequence()`:

```python
def _print_streaming_response(token_iter, model: str = "") -> None:
    """Imprime resposta em streaming com efeito typewriter usando Rich Live."""
    full = ""
    console.print()
    with Live(
        Spinner("dots2", text=Text("  a processar...", style=C_ACCENT)),
        console=console,
        refresh_per_second=20,
        transient=False,
    ) as live:
        for chunk in token_iter:
            full += chunk
            live.update(
                Panel(
                    Markdown(full),
                    title=Text("  Especialista", style=f"bold {C_ACCENT}"),
                    subtitle=Text(f"  {model}", style=C_DIM) if model else None,
                    border_style=C_ACCENT,
                    padding=(0, 2),
                )
            )
    if not full:
        print_error("Sem resposta do modelo.")
```

#### 7c — Substituir `start_repl()` completo

Localiza `def start_repl() -> None:` e substitui a função **inteira**:

```python
def start_repl() -> None:
    """
    REPL interactivo com prompt_toolkit.
    Histórico persistente, autocomplete, streaming de respostas LLM.
    """
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.formatted_text import ANSI
    from orchestrator.chat_engine import ChatEngine

    repl_history_file = Path.home() / ".tradecli" / "repl_history"
    repl_history_file.parent.mkdir(parents=True, exist_ok=True)

    session = PromptSession(
        history=FileHistory(str(repl_history_file)),
        auto_suggest=AutoSuggestFromHistory(),
    )

    chat_engine = ChatEngine()
    render_main_screen()

    CLI_COMMANDS = {
        "analyze", "train", "knowledge", "outcome",
        "review", "history", "health", "init", "db-setup",
        "show", "version", "models", "assets", "tui", "config",
    }

    while True:
        try:
            raw = session.prompt(
                ANSI("\033[36m  tradecli\033[0m\033[2m › \033[0m"),
            ).strip()

            if not raw:
                continue

            cmd = raw.lower().split() if raw.split() else ""

            if cmd in ("exit", "quit", "q", "sair", "bye"):
                console.print(
                    Text.assemble(("\n  Até já. ", C_MUTED), ("Bons trades.\n", C_BRAND))
                )
                break

            if cmd == "clear":
                render_main_screen()
                continue

            if cmd == "help":
                console.print(render_help())
                continue

            if cmd in CLI_COMMANDS:
                _run_cli_command(raw.split())
                continue

            # Chat com streaming
            _print_streaming_response(
                chat_engine.stream(raw),
                model=chat_engine.model_name,
            )

        except KeyboardInterrupt:
            console.print(
                Text.assemble(
                    ("\n\n  Ctrl+C detectado. ", C_MUTED),
                    ("Escreve exit para sair correctamente.\n", C_DIM),
                )
            )
        except EOFError:
            break
        except Exception as e:
            print_error(f"Erro inesperado: {e}")
            log.error("repl_error", error=str(e))
```

#### 7d — Substituir `_run_cli_command()` completo

```python
def _run_cli_command(parts: list[str]) -> None:
    """Executa sub-comando Typer directamente sem CliRunner."""
    import sys as _sys
    from cli.main import app
    from typer.main import get_command

    old_argv = _sys.argv
    _sys.argv = ["tradecli"] + parts
    try:
        click_app = get_command(app)
        click_app.main(parts, standalone_mode=False)
    except SystemExit:
        pass
    except Exception as e:
        print_error(f"Erro no comando '{parts}': {e}")
        log.error("cli_command_error", cmd=parts, error=str(e))
    finally:
        _sys.argv = old_argv
```

---

### PASSO 8 — Substituir `cli/tui/app.py` completo

Substitui o conteúdo **completo** do ficheiro:

```python
"""
Trade-CLI TUI — Main Application
Textual app com DashboardScreen.
Fase 3 — 2026-05-01
"""

from pathlib import Path
from textual.app import App
from textual.widgets import Input
from cli.tui.screens.dashboard import DashboardScreen
from orchestrator.orchestrator import Orchestrator

# CSS_PATH absoluto — evita ambiguidade com CWD
_CSS_PATH = str(Path(__file__).parent / "theme" / "trade_cli.tcss")


class TradeCLIApp(App):
    """
    Textual application principal do Trade-CLI.
    Carrega DashboardScreen e lida com input de análise.
    Sem os.chdir() — paths resolvidos explicitamente.
    """

    CSS_PATH = _CSS_PATH

    BINDINGS = [
        ("q", "quit", "Sair"),
        ("ctrl+c", "quit", "Sair"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        super().__init__()
        # Mock por defeito — não depende de MT5
        self.orchestrator = Orchestrator(use_llm=True, use_rag=False, use_mt5=False)

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle análise via barra de input."""
        cmd = event.value.strip().upper().split()
        if len(cmd) >= 2:
            symbol, timeframe = cmd, cmd[1]
            event.input.value = f"Analisando {symbol} {timeframe}..."
            try:
                result = self.orchestrator.analyze(symbol, timeframe)
                screen = self.screen
                if isinstance(screen, DashboardScreen):
                    screen.update_analysis(result, symbol, timeframe, [])
            except Exception as e:
                event.input.value = f"Erro: {e}"
            else:
                event.input.value = ""
        else:
            event.input.value = "Formato: SYMBOL TIMEFRAME  (ex: EURUSD H1)"

    def action_refresh(self) -> None:
        self.refresh()
```

---

### PASSO 9 — Instalar Globalmente com pipx

```bash
# 1. Instalar pipx
pip install pipx
pipx ensurepath

# 2. FECHAR e REABRIR o terminal

# 3. Ir ao root do projecto
cd /caminho/completo/para/Trade-CLI

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Instalar globalmente
pipx install -e .

# 6. Confirmar
which tradecli        # Linux/Mac
where tradecli        # Windows
```

**Alternativa sem pipx:**
```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows
pip install -e .

# Adicionar ao ~/.bashrc ou ~/.zshrc:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### PASSO 10 — Inicializar e Testar

```bash
# Inicializar vault + base de dados
tradecli init

# Estado de todos os componentes
tradecli health

# Teste de análise (modo mock)
tradecli analyze EURUSD H1 --test

# REPL interactivo (de qualquer directório)
cd /tmp
tradecli

# TUI Textual
tradecli tui

# Histórico — fechar e reabrir, usar seta ↑
tradecli
```

---

## 📋 Checklist Completa
MODELO
[] ollama pull gemma4:e4b
[] ollama list → gemma4:e4b aparece

FICHEIROS
[] pyproject.toml → substituição completa (entry point + packages.find + v0.3.0)
[] requirements.txt → adicionar textual>=0.59.0
[] .env.example → OLLAMA_MODEL=gemma4:e4b
[] .env → cp .env.example .env
[] orchestrator/llm_client.py → default gemma4:e4b + método stream_chat()
[] orchestrator/chat_engine.py → imports + constante + _init_ + 4 métodos novos
[] cli/launcher.py → default + _print_streaming_response + start_repl + _run_cli_command
[] cli/tui/app.py → substituição completa (sem os.chdir, CSS_PATH absoluto)

INSTALAÇÃO
[] pip install -r requirements.txt
[] pipx install -e .
[] Reabrir terminal
[] which tradecli → mostra caminho

TESTES
[] tradecli version
[] tradecli health
[] tradecli analyze EURUSD H1 --test
[] tradecli (REPL — testar streaming gemma4:e4b)
[] tradecli tui
[] cd /tmp && tradecli health (testar de outro directório)
[] Testar histórico persistente (seta ↑ após reiniciar)

text

---

## 🗂️ Ficheiros Afectados

| Ficheiro | Alteração | Prioridade |
|---|---|---|
| `pyproject.toml` | Substituição completa | 🔴 Crítico |
| `requirements.txt` | Adicionar `textual>=0.59.0` | 🔴 Crítico |
| `.env.example` | Substituição completa | 🔴 Crítico |
| `orchestrator/llm_client.py` | Default gemma4:e4b + `stream_chat()` | 🔴 Crítico |
| `cli/launcher.py` | Default + streaming + PromptSession | 🔴 Crítico |
| `cli/tui/app.py` | Substituição completa | 🔴 Crítico |
| `orchestrator/chat_engine.py` | Histórico persistente + `stream()` | 🟠 Alta |
| `.env` (criar) | `cp .env.example .env` | 🟠 Alta |

---

## 🧩 Ficheiros que NÃO precisam de alteração

- `main.py` — wrapper entry point (funciona)
- `cli/main.py` — todos os comandos Typer (funciona)
- `orchestrator/orchestrator.py` — pipeline completo (funciona)
- `core/risk_guardian.py` — regras FTMO (funciona)
- `core/analysis_schema.py` — schema de análise (funciona)
- `engines/__init__.py` — todos os engines (funciona)
- `cli/tui/screens/dashboard.py` — layout 3 colunas (funciona)
- `cli/tui/widgets/` — todos os 4 widgets (funciona)
- `cli/tui/theme/trade_cli.tcss` — tema CSS (funciona)

---

*Gerado com análise directa do código em [github.com/GustaFigz/Trade-CLI](https://github.com/GustaFigz/Trade-CLI) — Maio 2026*

---

---

# 🧠 CONTEXTO COMPLETO DO PROJECTO — Para Agentes de Codificação

> Esta secção é leitura obrigatória para qualquer agente (Antigravity, Copilot, Cursor, etc.)  
> que abra este projecto. Contém o mapa mental completo, contratos de código,  
> e o plano de integração Graphify sem Claude e sem custos.

---

## 🗺️ Mapa da Arquitectura Real (Maio 2026)
Trade-CLI/
│
├── main.py ← Entry point (wrapper, não tocar)
│
├── cli/
│ ├── launcher.py ← REPL interactivo + boot sequence + chat
│ ├── main.py ← Typer: 12 sub-comandos (analyze, health, tui…)
│ └── tui/
│ ├── app.py ← TradeCLIApp (Textual) — CSS_PATH corrigido
│ ├── screens/
│ │ └── dashboard.py ← Layout 3 colunas (sidebar + chart + scores)
│ ├── widgets/
│ │ ├── candle_chart.py ← Gráfico de candlestick em ASCII
│ │ ├── engine_scores.py ← Barras de score por engine
│ │ ├── verdict_panel.py ← Painel ALLOWED/BLOCKED/WATCH_ONLY
│ │ └── asset_sidebar.py ← Lista de ativos activos
│ └── theme/
│ └── trade_cli.tcss ← Tema dark trading (CSS Textual)
│
├── orchestrator/
│ ├── orchestrator.py ← Pipeline: MT5→engines→RAG→LLM→RiskGuardian
│ ├── llm_client.py ← Ollama httpx (gemma4:e4b) + stream_chat()
│ ├── chat_engine.py ← RAG+LLM+histórico persistente em disco
│ └── prompt_templates.py ← Prompts estruturados para análise
│
├── core/
│ ├── analysis_schema.py ← FROZEN — Dataclasses + Enums (não modificar)
│ └── risk_guardian.py ← FROZEN — Veto final FTMO (não contornar)
│
├── engines/
│ └── _init_.py ← TechnicalEngine, PriceActionEngine,
│ FundamentalEngine, ThesisEngine
│
├── knowledge/
│ ├── obsidian_reader.py ← Lê vault Obsidian (frontmatter + conteúdo)
│ ├── chunk_vectorizer.py ← Texto → embeddings TF-IDF
│ ├── rag_retriever.py ← SQLite + vault → TF-IDF search
│ └── context_builder.py ← Monta contexto LLM a partir de RAG
│
├── data/
│ ├── mt5_client.py ← MT5 read-only (fallback mock automático)
│ ├── mock_data.py ← OHLCV mock para testes sem MT5
│ └── calendar_client.py ← Calendário económico (HTTP, sem API key)
│
├── db/
│ ├── migrations.py ← create_database("database.db")
│ └── db_schema.sql ← 5 tabelas: analyses, knowledge_base, outcomes…
│
├── training/
│ ├── ingest.py ← PDF/Markdown/TXT → chunks
│ ├── chunker.py ← Chunking semântico
│ ├── tagger.py ← Auto-tagging por símbolo/método
│ └── kb_writer.py ← Escreve em SQLite knowledge_base
│
├── config/
│ ├── ftmo-rules.yaml ← Regras FTMO (daily loss, total loss, etc.)
│ └── assets.yaml ← EURUSD, USDJPY, USDCAD, US30, NAS100
│
├── Trade-CLI-Vault/ ← Obsidian vault (RAG source)
│ ├── 00-meta/ ← Templates + sessões Antigravity
│ ├── ativos/ ← Notas por ativo (EURUSD, USDJPY…)
│ ├── conceitos/ ← Order blocks, liquidity, FVG, ICT…
│ ├── metodos/ ← Smart Money, ICT, Wyckoff…
│ ├── treino/ ← Exercícios e simulações
│ └── revisoes/ ← Post-mortems e revisões semanais
│
├── pyproject.toml ← entry: cli.launcher:main | v0.3.0
├── requirements.txt ← inclui textual>=0.59.0
├── .env / .env.example ← OLLAMA_MODEL=gemma4:e4b
└── CLAUDE.md ← Instruções para agentes (LEITURA OBRIGATÓRIA)

text

---

## 🔒 Contratos de Código (Invioláveis)

### Contrato 1 — RiskGuardian é sempre a última palavra
```python
# SEMPRE assim — sem excepções:
verdict = risk_guardian.should_block(thesis_output)
# NUNCA:
verdict = VerdictType.ALLOWED  # hardcoded
```

### Contrato 2 — Todo o engine retorna EngineOutput
```python
# OBRIGATÓRIO em qualquer engine novo:
EngineOutput(
    engine_name="meu_engine",   # snake_case
    score=0.0,                  # 0.0 a 1.0
    explanation="...",          # porquê
    evidence={...}              # dados usados
)
```

### Contrato 3 — LLM sintetiza, nunca decide
```python
# LLM explica e organiza — RiskGuardian decide
# Se LLM está offline → análise continua sem ele
# Se RiskGuardian bloqueia → nenhum LLM pode desbloquear
```

### Contrato 4 — Memória dupla
Obsidian Vault → Conhecimento humano-legível (teses, conceitos, métodos)
SQLite → Log estruturado + embeddings RAG + outcomes
NUNCA → Dumps de chat para o vault

text

### Contrato 5 — Zero cloud, zero custo
```python
# ✅ Permitido:
from orchestrator.llm_client import LLMClient  # Ollama local
# ❌ Proibido:
import anthropic   # Claude API
import openai      # OpenAI API (excepto endpoint local via LLM_API_BASE)
```

### Contrato 6 — Símbolos suportados
```python
SYMBOLS = ["EURUSD", "USDJPY", "USDCAD", "US30", "NAS100"]
# NUNCA usar NZDUSD — era apenas placeholder de Phase 1
```

---

## 📊 Schema de Análise — Contrato de Output

Qualquer chamada a `orchestrator.analyze(symbol, timeframe)` deve retornar
um dict com esta estrutura exacta:

```python
{
    "symbol": "EURUSD",
    "timeframe": "H1",
    "timestamp": "2026-05-01T15:00:00",
    "analysis": {
        "bias": "bullish",              # enum: bullish|bearish|neutral|fragile
        "confidence_score": 0.72,       # 0.0–1.0
        "alignment_score": 0.65,        # concordância entre engines
        "setup_type": "ICT BOS + OB",
        "technical_score": 0.70,
        "price_action_score": 0.75,
        "fundamental_score": 0.60,
    },
    "engine_outputs": [
        {"name": "Technical", "score": 0.70, "explanation": "..."},
        {"name": "Price Action", "score": 0.75, "explanation": "..."},
        {"name": "Fundamental", "score": 0.60, "explanation": "..."},
    ],
    "verdict": "ALLOWED",              # enum: ALLOWED|WATCH_ONLY|BLOCKED
    "verdict_reason": "All engines aligned, FTMO rules met",
    "risk_notes": ["Session overlap risk", "NFP tomorrow"],
    "invalidations": ["Break below 1.0800", "Close above 1.0950"],
    "llm_used": True,
    "data_source": "mock",             # mock|mt5
}
```

---

## 🧩 Vault Obsidian — Estrutura de Notas

Cada nota do vault **deve** ter este frontmatter:

```yaml
***
type: tese|conceito|metodo|ativo|treino|revisao
symbol: EURUSD          # ou "todos" para conceitos gerais
created: 2026-05-01
tags: [ict, order-block, london-session, bullish]
confidence: high|medium|low
***
```

Cada tese deve ter **mínimo 2 wikilinks** para criar o grafo:
```markdown
Vejo setup ICT no [[ativos/EURUSD]] com [[conceitos/order-block]]
confirmado por [[metodos/smart-money-concepts]].
```

---

## 🌐 Integração Graphify — 100% Gratuita, Sem Claude

**O que é o Graphify:** ferramenta open-source que gera um knowledge graph
navegável do teu projecto inteiro — código, docs, vault Obsidian — e
integra-se directamente com Antigravity como skill permanente.
Repositório: https://github.com/safishamsi/graphify

### Porquê usar Graphify com este projecto

O Trade-CLI tem uma estrutura complexa: código Python + vault Obsidian +
configs YAML + schema SQL. O Graphify extrai as relações entre tudo e
cria um `index.md` navegável que qualquer agente (Antigravity, Copilot,
Cursor, etc.) pode ler para entender o projecto sem precisar de explorar
ficheiro a ficheiro. Funciona 100% local — zero Claude, zero OpenAI.

### Instalação do Graphify

```bash
# 1. Instalar pipx se não tiveres
pip install pipx
pipx ensurepath

# 2. Instalar Graphify globalmente
pipx install graphify

# Ou alternativa com pip normal:
pip install graphify
```

### Configurar Graphify para o Trade-CLI

```bash
# No root do projecto Trade-CLI:
cd /caminho/para/Trade-CLI

# Instalar integração com Antigravity (gera .agents/rules + .agents/workflows)
graphify antigravity install

# Gerar o knowledge graph do projecto completo
# Inclui código Python + vault Obsidian + docs + configs
graphify . --obsidian --obsidian-dir ./Trade-CLI-Vault

# O que isto gera:
# graphify-out/
# ├── graph.json          ← grafo completo (nodes + edges)
# ├── graph.html          ← visualização interactiva (abrir no browser)
# ├── report.md           ← resumo de clusters e conexões
# └── index.md            ← wiki navegável (entrada para agentes)
```

### Usar Graphify com o vault Obsidian como destino principal

```bash
# Gerar grafo e escrever directamente no vault:
graphify . --obsidian --obsidian-dir ./Trade-CLI-Vault

# Isto cria em Trade-CLI-Vault/:
# graphify-out/
# ├── index.md              ← mapa do projecto (agente começa aqui)
# ├── communities/          ← clusters de ficheiros relacionados
# └── graph.json            ← dados brutos do grafo

# Abrir visualização no browser:
open graphify-out/graph.html    # Mac
xdg-open graphify-out/graph.html  # Linux
start graphify-out/graph.html   # Windows
```

### Manter o grafo actualizado automaticamente (git hook)

```bash
# Instalar hook — rebuild automático em cada commit:
graphify hook install

# Verificar que o hook está activo:
graphify hook status

# A partir de agora, cada git commit actualiza o grafo automaticamente.
```

### Watch mode — actualização em tempo real durante desenvolvimento

```bash
# Mantém o grafo sincronizado enquanto programas:
graphify . --watch

# Em terminal separado, trabalhar normalmente:
# O grafo actualiza-se automaticamente quando guardas ficheiros Python/Markdown.
```

### Comandos Graphify mais úteis para este projecto

```bash
# Pesquisar conexões no grafo via terminal (sem abrir nada):
graphify query "como o RAGRetriever se liga ao ObsidianReader"
graphify query "qual o caminho do MT5 até ao RiskGuardian"
graphify query "onde são usados os EngineOutput"

# Ver caminho mais curto entre dois conceitos:
graphify path "LLMClient" "RiskGuardian"
graphify path "ObsidianReader" "ContextBuilder"

# Explicação plain-language de um node:
graphify explain "ThesisEngine"
graphify explain "ChatEngine"

# Adicionar documentação externa ao grafo:
graphify add https://docs.textual.textualize.io
graphify add https://ollama.com/library/gemma4

# Update incremental (só re-extrai ficheiros alterados):
graphify . --update
```

### Alternativa — Cognee (mais avançado, também gratuito)

Se quiseres um grafo com relações semânticas mais ricas (extrai entidades
e relações automáticamente usando LLM local):

```bash
pip install cognee

# Usar com Ollama local (gemma4:e4b):
# Ver: https://forum.obsidian.md/t/automated-knowledge-graphs-with-cognee/108834
```

Cognee processa os .md do vault, extrai entidades (conceitos de trading,
símbolos, métodos) e cria links automáticos — sem Claude, usando Ollama.

### Como o agente usa o grafo gerado

Quando Antigravity (ou qualquer agente) abre o projecto:
Lê CLAUDE.md → regras e arquitectura

Lê graphify-out/index.md → mapa de todos os ficheiros e conexões

Navega communities/ → percebe quais ficheiros pertencem ao mesmo cluster

Usa graphify query → responde perguntas sobre conexões sem ler código

text

Exemplo prático para Antigravity:
Antes de qualquer tarefa, o agente corre:
graphify query "quais ficheiros dependem de AnalysisOutput"

Resposta: core/analysis_schema.py → engines/_init_.py → orchestrator.py → cli/main.py
O agente sabe exactamente o que pode partir se mudar o schema.
text

---

## 📋 Ficheiros Pendentes de Criar (Phase 2 não completada)

Estes ficheiros estão referenciados no código mas ainda não existem no repo:

| Ficheiro | Prioridade | Descrição |
|---|---|---|
| `engines/sentiment.py` | 🟠 Alta | Análise de sentimento (RSS feeds, sem API) |
| `engines/intermarket.py` | 🟡 Média | Correlações entre pares e índices |
| `engines/volume.py` | 🟡 Média | Volume profile e delta |
| `tests/test_rag.py` | 🟠 Alta | Testes do RAGRetriever + ObsidianReader |
| `tests/test_orchestrator.py` | 🟠 Alta | Testes do pipeline completo |
| `tests/test_engines.py` | 🟡 Média | Testes unit dos 3 engines existentes |
| `docs/decisions-phase2.md` | 🟡 Média | Log de decisões arquitecturais Phase 2 |

### Template para `engines/sentiment.py` (sem API, sem custo)

```python
"""
Sentiment Engine — Trade-CLI Phase 2.4
Analisa sentimento de mercado via RSS feeds públicos (sem API key).
Fontes: ForexFactory RSS, Investing.com RSS, Reuters RSS.

Fase: 2.4
Data: 2026-05-01
"""
from __future__ import annotations
import feedparser
import structlog
from core.analysis_schema import EngineOutput

log = structlog.get_logger(__name__)

RSS_FEEDS = {
    "forexfactory": "https://www.forexfactory.com/feed",
    "fxstreet": "https://www.fxstreet.com/rss",
}

class SentimentEngine:
    """Análise de sentimento via RSS público — zero custo."""

    def analyze(self, symbol: str, timeframe: str) -> EngineOutput | None:
        try:
            score = self._compute_sentiment(symbol)
            return EngineOutput(
                engine_name="sentiment",
                score=score,
                explanation=f"RSS sentiment score for {symbol}: {score:.1%}",
                evidence={"symbol": symbol, "source": "rss_public"},
            )
        except Exception as e:
            log.error("sentiment_engine_failed", error=str(e))
            return None

    def _compute_sentiment(self, symbol: str) -> float:
        """Busca RSS e calcula score por frequência de menções positivas/negativas."""
        positive_words = ["bullish", "rally", "gains", "strength", "buying"]
        negative_words = ["bearish", "drop", "losses", "weakness", "selling"]
        pos, neg = 0, 0
        for url in RSS_FEEDS.values():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:20]:
                    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
                    if symbol.lower() in text or symbol[:3].lower() in text:
                        pos += sum(1 for w in positive_words if w in text)
                        neg += sum(1 for w in negative_words if w in text)
            except Exception:
                continue
        total = pos + neg
        if total == 0:
            return 0.5  # neutro por defeito
        return pos / total
```

Adicionar ao `requirements.txt`:
```txt
feedparser>=6.0.10
```

---

## 🔄 Workflow de Sessão para Antigravity

Antes de qualquer tarefa de codificação, o agente deve executar em sequência:

```bash
# 1. Ler estado actual
cat CLAUDE.md
cat graphify-out/index.md      # se graphify já instalado

# 2. Correr testes (confirmar que nada está partido)
pytest tests/ -v -m "not slow and not integration"

# 3. Verificar saúde do sistema
python main.py health

# 4. Verificar que o modelo está disponível
ollama list | grep gemma4

# 5. Só então começar a tarefa
```

Após terminar qualquer tarefa:

```bash
# 1. Correr testes novamente
pytest tests/ -v --cov

# 2. Actualizar grafo (se graphify instalado)
graphify . --update

# 3. Guardar sessão (template abaixo)
# Criar: Trade-CLI-Vault/00-meta/ANTIGRAVITY-SESSION-YYYY-MM-DD.md
```

Template de sessão a guardar no vault:

```markdown
***
type: sessao-antigravity
created: 2026-05-01
tags: [antigravity, phase-2, sessao]
***

# Sessão Antigravity — 2026-05-01

## Tarefa
[Descrição do que foi pedido]

## O que foi feito
- [ficheiro1.py] — [o que mudou]
- [ficheiro2.py] — [o que mudou]

## Testes
- pytest: X passed, Y warnings

## Próximos passos
- [ ] [tarefa pendente 1]
- [ ] [tarefa pendente 2]

## Decisões tomadas
[Porquê foi feito desta forma e não de outra]
```

---

## 🚦 Estado de Phase 2 — O que falta para estar 100% completo
PHASE 2 — STATUS ACTUAL (Maio 2026)

✅ 2.1 — Infraestrutura
✓ pyproject.toml corrigido
✓ requirements.txt completo
✓ .env configurado (gemma4:e4b)
✓ config/assets.yaml
✓ config/ftmo-rules.yaml

✅ 2.2 — Data Layer
✓ data/mt5_client.py (mock automático)
✓ data/mock_data.py
✓ knowledge/obsidian_reader.py
✓ knowledge/chunk_vectorizer.py
✓ knowledge/rag_retriever.py (TF-IDF)
✓ knowledge/context_builder.py

✅ 2.3 — Orchestrator + LLM
✓ orchestrator/orchestrator.py
✓ orchestrator/llm_client.py (stream_chat pendente)
✓ orchestrator/chat_engine.py (histórico persistente pendente)
✓ cli/launcher.py (PromptSession pendente)

🚧 2.4 — Engines Adicionais
✗ engines/sentiment.py ← template acima
✗ engines/intermarket.py
✗ engines/volume.py

🚧 2.5 — Persistência + Testes
✗ tests/test_rag.py
✗ tests/test_orchestrator.py
✗ tests/test_engines.py
✗ docs/decisions-phase2.md

🚧 TUI — Fase 3
✓ cli/tui/app.py (corrigido)
✓ cli/tui/screens/dashboard.py
✓ cli/tui/widgets/ (4 widgets)
✓ cli/tui/theme/trade_cli.tcss
✗ Persistência análise → SQLite (Phase 3 completo)
✗ Obsidian export automático (Phase 3)

text

---

## 📞 Decisões Rápidas para o Agente

| Situação | Acção Correcta |
|---|---|
| Preciso de mudar `AnalysisOutput` | PARAR — pedir ao utilizador primeiro |
| Preciso de mudar `RiskGuardian` | PARAR — pedir ao utilizador primeiro |
| Quero adicionar engine novo | Criar `engines/nome.py` + registar em `engines/__init__.py` |
| Quero adicionar comando CLI | Adicionar `@app.command()` em `cli/main.py` |
| Quero usar LLM | Usar `LLMClient()` — nunca importar anthropic/openai |
| Tests estão a falhar | `pytest tests/ -v --tb=long` e corrigir antes de avançar |
| Vault não encontrado | `tradecli init` ou verificar `OBSIDIAN_VAULT_PATH` no `.env` |
| Ollama não responde | `ollama serve` num terminal separado |
| MT5 não disponível | Normal — `fallback_to_mock=True` está activo por defeito |

---

*Secção gerada em Maio 2026 — análise directa de todos os ficheiros do repositório  
[github.com/GustaFigz/Trade-CLI](https://github.com/GustaFigz/Trade-CLI)*