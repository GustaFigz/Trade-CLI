-- Trade-CLI Database Schema (Phase 1)
-- SQLite
-- Date: 2025-04-30
-- Validates: docs/decisions-phase1.md

-- ============================================================================
-- TABELA 1: Análises (Central)
-- ============================================================================
-- Guarda cada análise de setup com todos os scores e metadados
CREATE TABLE analyses (
    id TEXT PRIMARY KEY,                           -- UUID ou timestamp+pair+tf
    symbol TEXT NOT NULL,                          -- NZDUSD, EURUSD, etc.
    timeframe TEXT NOT NULL,                       -- M5, M15, H1, H4
    analysis_type TEXT,                            -- "thesis", "educational", "test"
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- quando foi criada
    analyst_notes TEXT,
    
    -- Valores de análise
    confidence_score REAL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    alignment_score REAL CHECK (alignment_score >= 0.0 AND alignment_score <= 1.0),
    
    -- Classificação
    bias TEXT,                                     -- bullish, bearish, neutral, fragile
    setup_type TEXT,                               -- liquidity_sweep, pullback_continuation, etc.
    
    -- Scores por motor
    technical_score REAL CHECK (technical_score >= 0.0 AND technical_score <= 1.0),
    price_action_score REAL CHECK (price_action_score >= 0.0 AND price_action_score <= 1.0),
    fundamental_score REAL CHECK (fundamental_score >= 0.0 AND fundamental_score <= 1.0),
    
    -- Saídas estruturadas
    invalidations TEXT,                            -- JSON array ["condition1", "condition2"]
    risk_notes TEXT,                               -- JSON array ["risk1", "risk2"]
    
    -- Decisão final
    verdict TEXT CHECK (verdict IN ('allowed', 'watch_only', 'blocked')),
    
    -- Links para outras memórias
    obsidian_link TEXT,                            -- [[2025-04-30-NZDUSD-M15-thesis]]
    
    -- Índices para busca rápida
    UNIQUE(symbol, timeframe, timestamp)
);

CREATE INDEX idx_analyses_symbol ON analyses(symbol);
CREATE INDEX idx_analyses_timestamp ON analyses(timestamp);
CREATE INDEX idx_analyses_verdict ON analyses(verdict);
CREATE INDEX idx_analyses_setup_type ON analyses(setup_type);
CREATE INDEX idx_analyses_confidence ON analyses(confidence_score);

-- ============================================================================
-- TABELA 2: Resultados Posteriores
-- ============================================================================
-- Compara análise original com o que realmente aconteceu
CREATE TABLE analysis_outcomes (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,                     -- foreign key
    
    -- Quando foi avaliado
    outcome_timestamp DATETIME,
    outcome_source TEXT,                           -- 'manual', 'automated', 'backtest'
    
    -- O que realmente aconteceu
    price_action TEXT,                             -- descrição do que o preço fez
    price_moved_pips INT,                          -- pips de movimento
    
    -- Validação
    invalidated BOOLEAN,                           -- se a invalidação ocorreu
    invalidation_type TEXT,                        -- qual invalidação aconteceu
    
    -- Resultado operacional
    profit_loss_pips INT,                          -- ganho ou perda em pips
    execution_quality TEXT CHECK (execution_quality IN ('ideal', 'acceptable', 'poor', 'not_traded')),
    
    -- Análise
    post_mortem_notes TEXT,                        -- reflexão
    
    -- Link para doc de aprendizado
    obsidian_link TEXT,                            -- [[2025-04-30-NZDUSD-M15-postmortem]]
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);

CREATE INDEX idx_outcomes_analysis_id ON analysis_outcomes(analysis_id);
CREATE INDEX idx_outcomes_timestamp ON analysis_outcomes(outcome_timestamp);
CREATE INDEX idx_outcomes_invalidated ON analysis_outcomes(invalidated);

-- ============================================================================
-- TABELA 3: Outputs de Motores (Auditoria)
-- ============================================================================
-- Rastreia o que cada motor disse (para debug e aprendizado)
CREATE TABLE engine_outputs (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,                     -- qual análise produziu isto
    
    engine_name TEXT NOT NULL,                     -- 'technical', 'price_action', 'fundamental'
    engine_version TEXT,                           -- v1.0, v1.1, etc.
    
    -- Resultado do motor
    score REAL CHECK (score >= 0.0 AND score <= 1.0),
    explanation TEXT,                              -- por que este score
    
    -- Dados estruturados usados
    evidence TEXT,                                 -- JSON de features usadas
    
    -- Conflito inter-motores
    conflict_with_other_engines BOOLEAN DEFAULT FALSE,
    conflict_description TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);

CREATE INDEX idx_engine_outputs_analysis ON engine_outputs(analysis_id);
CREATE INDEX idx_engine_outputs_engine ON engine_outputs(engine_name);

-- ============================================================================
-- TABELA 4: Ideias Vetadas (Governança)
-- ============================================================================
-- Histórico de propostas que foram bloqueadas (para análise de filtros)
CREATE TABLE vetoed_ideas (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    setup_type TEXT,
    
    -- Por que foi vetada
    veto_reason TEXT CHECK (veto_reason IN (
        'drawdown_limit',
        'daily_loss_limit', 
        'correlation_block',
        'news_blackout',
        'quality_below_threshold',
        'confidence_too_low',
        'alignment_too_low',
        'spread_too_wide',
        'other'
    )),
    veto_detail TEXT,                              -- descrição específica
    
    -- Scores da proposta
    confidence_was REAL,
    alignment_was REAL,
    
    -- Resultado posterior (foi corretamente bloqueada?)
    outcome_was_correct BOOLEAN,                   -- se realmente teria sido ruim
    
    UNIQUE(symbol, timeframe, timestamp)
);

CREATE INDEX idx_vetoed_symbol ON vetoed_ideas(symbol);
CREATE INDEX idx_vetoed_reason ON vetoed_ideas(veto_reason);
CREATE INDEX idx_vetoed_timestamp ON vetoed_ideas(timestamp);

-- ============================================================================
-- TABELA 5: Base de Conhecimento Persistente
-- ============================================================================
-- Playbooks, padrões, regras, insights que valem a pena guardar
CREATE TABLE knowledge_base (
    id TEXT PRIMARY KEY,
    
    category TEXT CHECK (category IN (
        'playbook',           -- padrão de setup reutilizável
        'error_pattern',      -- erro que se repete
        'setup_rule',         -- regra para um tipo de setup
        'market_insight',     -- insight sobre mercado/par
        'procedure',          -- procedimento operacional
        'guardrail'           -- regra de proteção
    )),
    
    -- Contexto
    symbol TEXT,                                   -- null = aplica a tudo
    setup_type TEXT,                               -- null = não específico a setup
    
    -- Conteúdo
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    conditions TEXT,                               -- JSON de pré-condições
    
    -- Qualidade
    confidence_level TEXT CHECK (confidence_level IN ('high', 'medium', 'low')),
    source TEXT,                                   -- 'research', 'live_trading', 'external', 'ai_generated'
    review_status TEXT CHECK (review_status IN ('unreviewed', 'reviewed', 'validated')),
    
    -- Timestamps
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_reviewed DATETIME,
    
    -- Links
    obsidian_link TEXT,                            -- [[playbook-name]]
    references TEXT,                               -- JSON array de referências externas
    
    -- Uso
    usage_count INTEGER DEFAULT 0,                 -- quantas análises citaram isto
    success_rate REAL,                             -- % de sucessos quando aplicado
    
    UNIQUE(category, symbol, title)
);

CREATE INDEX idx_kb_category ON knowledge_base(category);
CREATE INDEX idx_kb_symbol ON knowledge_base(symbol);
CREATE INDEX idx_kb_review_status ON knowledge_base(review_status);
CREATE INDEX idx_kb_confidence ON knowledge_base(confidence_level);

-- ============================================================================
-- VIEWS (para queries úteis)
-- ============================================================================

-- View: Últimas análises de um par
CREATE VIEW recent_analyses_by_symbol AS
    SELECT symbol, timeframe, timestamp, confidence_score, alignment_score, bias, verdict
    FROM analyses
    ORDER BY symbol, timestamp DESC;

-- View: Taxa de acerto de verdicts (para calibração)
CREATE VIEW verdict_accuracy AS
    SELECT 
        analyses.verdict,
        COUNT(*) as total_analyses,
        SUM(CASE WHEN analysis_outcomes.profit_loss_pips > 0 THEN 1 ELSE 0 END) as won,
        CAST(SUM(CASE WHEN analysis_outcomes.profit_loss_pips > 0 THEN 1 ELSE 0 END) AS FLOAT) 
            / NULLIF(COUNT(*), 0) as win_rate
    FROM analyses
    LEFT JOIN analysis_outcomes ON analyses.id = analysis_outcomes.analysis_id
    WHERE analysis_outcomes.id IS NOT NULL
    GROUP BY analyses.verdict;

-- View: Motores com discordância (conflitos)
CREATE VIEW engine_conflicts AS
    SELECT 
        eo.analysis_id,
        eo.engine_name,
        eo.conflict_with_other_engines,
        eo.conflict_description
    FROM engine_outputs eo
    WHERE eo.conflict_with_other_engines = TRUE;

-- View: Taxa de veto correta (quantos setups bloqueados realmente teriam sido ruins?)
CREATE VIEW veto_accuracy AS
    SELECT 
        veto_reason,
        COUNT(*) as vetoed_count,
        SUM(CASE WHEN outcome_was_correct THEN 1 ELSE 0 END) as correctly_blocked,
        CAST(SUM(CASE WHEN outcome_was_correct THEN 1 ELSE 0 END) AS FLOAT) 
            / NULLIF(COUNT(*), 0) as accuracy_rate
    FROM vetoed_ideas
    WHERE outcome_was_correct IS NOT NULL
    GROUP BY veto_reason;

-- ============================================================================
-- SAMPLE QUERIES (para referência)
-- ============================================================================

/*
-- Buscar todas as análises NZDUSD com confidence >= 70%
SELECT * FROM analyses
WHERE symbol = 'NZDUSD' AND confidence_score >= 0.7
ORDER BY timestamp DESC;

-- Contar setups por tipo
SELECT setup_type, COUNT(*) as count
FROM analyses
GROUP BY setup_type
ORDER BY count DESC;

-- Análises que foram bloqueadas (verdict = 'blocked')
SELECT symbol, timeframe, setup_type, confidence_score, alignment_score
FROM analyses
WHERE verdict = 'blocked'
ORDER BY timestamp DESC;

-- Taxa de sucesso de teses "allowed" vs "watch_only"
SELECT 
    a.verdict,
    COUNT(*) as total,
    AVG(ao.profit_loss_pips) as avg_pips,
    AVG(a.confidence_score) as avg_confidence
FROM analyses a
LEFT JOIN analysis_outcomes ao ON a.id = ao.analysis_id
WHERE ao.id IS NOT NULL
GROUP BY a.verdict;

-- Quais motores mais discordam (conflitos)
SELECT engine_name, COUNT(*) as conflict_count
FROM engine_outputs
WHERE conflict_with_other_engines = TRUE
GROUP BY engine_name
ORDER BY conflict_count DESC;

-- Playbooks mais usados
SELECT title, usage_count, success_rate
FROM knowledge_base
WHERE category = 'playbook'
ORDER BY usage_count DESC;

-- Erros que se repetem
SELECT title, COUNT(*) as occurrences, success_rate
FROM knowledge_base
WHERE category = 'error_pattern'
GROUP BY title
ORDER BY occurrences DESC;
*/

-- ============================================================================
-- COMMENTS (documentação)
-- ============================================================================
/*
Schema Notes:

1. PRIMARY KEYS usam TEXT (UUID ou natural keys), não auto-increment
   - Razão: Permitir replicação, importação, sem conflitos

2. FOREIGN KEYS referem analysis.id (PK da tabela central)
   - Manutenção fácil se precisar reorganizar

3. REAL para scores (não INTEGER)
   - Razão: Suporta decimais (0.0–1.0, não apenas 0–100%)

4. JSON stored as TEXT
   - Razão: SQLite nativo, sem plugin JSON extra necessário
   - Parsed em Python quando necessário

5. UNIQUE constraints evitam duplicatas
   - Razão: Garantir uma entrada por (symbol, timeframe, timestamp)

6. Índices em colunas frequentemente filtradas
   - symbol, timestamp, verdict, confidence_score, engine_name

7. VIEWs para queries usuais
   - Facilita análise sem JOIN complexo

8. Congelado para Fase 1
   - Não adicionar colunas sem migration
   - Schema muda em migration durante Fase 2+
*/
