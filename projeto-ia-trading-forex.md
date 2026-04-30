# Projeto de IA Local para Apoio a Trading em Forex e Prop Firm

## Visão geral

Este projeto propõe uma IA local multimodal para **análise e apoio à decisão** em trading, com foco em forex, alguns índices e operação em contexto de prop firm, mas **sem abrir trades reais automaticamente**. O objetivo não é construir um bot “mágico” que prevê o mercado, e sim um sistema técnico que agrega múltiplas formas de análise, estrutura conhecimento no Obsidian, debate cenários e ajuda a filtrar oportunidades com disciplina operacional.[cite:24][cite:25][cite:46]

A base técnica faz sentido porque o ecossistema considerado combina três capacidades importantes: Gemma com compreensão de imagens e uso de ferramentas, integração Python do MetaTrader 5 para dados e estado de conta, e webhooks do TradingView para alertas e gatilhos operacionais.[cite:25][cite:37][cite:40][cite:46][cite:36]

O projeto deve ser desenhado como um sistema de apoio analítico avançado, não como substituto do trader humano. A CFTC alertou que IA não prevê o futuro e que promessas de ganhos fáceis com “AI trading bots” são frequentemente parte de narrativas enganosas ou fraudes, o que reforça a necessidade de tratar a IA como copiloto, filtro e motor de processo.[cite:24]

## Objetivos do sistema

### Objetivo principal

Construir um sistema local especializado em trading que consiga:

- reunir e cruzar múltiplas classes de análise;
- interpretar dados estruturados e imagens de gráfico;
- armazenar conhecimento, playbooks e pós-análises no Obsidian;
- produzir hipóteses de trade, cenários e invalidações;
- vetar setups incoerentes com as regras da prop firm e com o plano operacional;
- ajudar no estudo, na revisão e na evolução do processo de trading sem executar ordens reais automaticamente.

### Objetivos secundários

- Evoluir de assistente de estudo para analista operacional.
- Padronizar a análise antes, durante e depois do trade.
- Reduzir impulsividade, overtrading e viés narrativo.
- Criar uma base de conhecimento cumulativa sobre pares, índices, setups, contexto macro e erros recorrentes.
- Permitir expansão futura para mais ativos, mais dados e mais especialização.

## Princípios de projeto

1. **A IA não executa trades reais.** A camada de execução deve existir apenas para simulação, checagem de viabilidade, cálculo de risco e eventualmente integração futura controlada, mas a versão-alvo deste projeto é estritamente de apoio à decisão.[cite:40]
2. **O LLM não é o motor analítico único.** O modelo deve orquestrar ferramentas e interpretar saídas de motores especializados, porque function calling do Gemma é mais adequado para invocar capacidades específicas do que para substituir toda a lógica quantitativa com texto puro.[cite:25]
3. **Análise profunda depende de dados estruturados.** A capacidade multimodal do Gemma é útil para ler gráficos, screenshots e contexto visual, mas scalping e intraday exigem dados de ticks, barras, spread, market book e features calculadas.[cite:46][cite:40]
4. **Order flow em forex spot/CFD tem limitações estruturais.** Leituras de volume/profile e footprint tendem a ser mais sólidas em mercados centralizados como CME, porque ferramentas de Market Profile e FX Market Profile da CME se apoiam em volume negociado por preço em ambiente centralizado.[cite:57][cite:59]
5. **A prop firm vem antes da tese.** Regras de drawdown, consistência, janela de notícia e risco por trade têm de vetar setups antes da narrativa analítica se tornar uma sugestão operacional.[cite:33][cite:38]
6. **Memória deve ser curada, não bruta.** Obsidian deve guardar conhecimento reutilizável, decisões e revisões, e não um despejo indiscriminado de chats e logs.

## Escopo funcional

### Ativos e estilo operacional

O sistema foi concebido para:

- operar em contexto de prop firm;
- focar primeiro em scalping e intraday;
- começar com EURUSD, USDCAD, USDJPY e um conjunto pequeno de índices;
- expandir gradualmente para outros pares e ativos correlacionados.

### Formas de análise a cobrir

A arquitetura deve contemplar explicitamente estas camadas:

- Análise técnica.
- Análise fundamental.
- Análise de sentimento.
- Análise intermarket.
- Análise de volume.
- Price action.
- Market Profile / Volume Profile.
- Wyckoff.
- ICT.
- SMC.
- Microestrutura de mercado.
- Leitura visual de gráficos.

## Arquitetura proposta

### Visão em camadas

A arquitetura recomendada não é de um agente único “que sabe tudo”, mas de um sistema em camadas, com um orquestrador LLM por cima de motores analíticos e fontes de dados. Esta abordagem é mais consistente com o uso de ferramentas do Gemma e com a integração programática do MT5 em Python.[cite:25][cite:40]

| Camada                 | Papel principal                                                  | Observações                                               |
| ---------------------- | ---------------------------------------------------------------- | --------------------------------------------------------- |
| Interface              | Chat local, painel terminal e relatórios                         | Entrada manual, alertas e revisão                         |
| Orquestrador LLM       | Coordena motores, debate e síntese                               | Usa function calling e multimodalidade.[cite:25][cite:46] |
| Data Plane             | Ingestão de dados de mercado, notícias, screenshots e calendário | Alimenta todos os motores.[cite:36][cite:40]              |
| Motores Analíticos     | Cálculo de sinais e hipóteses por disciplina                     | Cada motor produz features e score                        |
| Motor de Tese          | Consolida sinais, monta cenários e conflitos                     | Não executa, apenas propõe                                |
| Guardião de Risco      | Aplica regras da prop firm e veto operacional                    | Deve ser determinístico.[cite:33][cite:38]                |
| Memória e Conhecimento | Obsidian + banco estruturado                                     | Conhecimento curado + histórico rotulado                  |
| Revisão e Aprendizado  | Pós-trade, métricas e melhoria do sistema                        | Base para evolução contínua                               |

### Componentes centrais

#### 1. Orquestrador LLM

O orquestrador é o “cérebro conversacional” do sistema. Ele recebe a tua pergunta, seleciona motores e fontes, solicita análises especializadas, identifica conflitos e devolve uma resposta estruturada com tese, invalidação, risco e observações.

Responsabilidades:

- decidir quais motores precisam ser acionados;
- pedir imagens e screenshots quando necessário;
- sintetizar resultados técnicos, macro e de microestrutura;
- detectar contradições entre especialistas;
- salvar aprendizados úteis no sistema de memória.

Limite importante: o orquestrador não deve gerar análise “do nada”. Ele deve operar sobre saídas estruturadas de ferramentas e motores, porque o próprio modelo é mais confiável quando usado em fluxos de tool calling bem definidos.[cite:25]

#### 2. Data Plane

O Data Plane é a camada mais importante depois do risco. Ele fornece matéria-prima para todos os módulos analíticos e precisa ser robusto, versionado e observável.

Fontes mínimas:

- MetaTrader 5 via Python para bars, ticks, book, símbolos, posições, histórico, margem e profit.[cite:40]
- TradingView para alertas webhook e eventos de estratégia/gráfico.[cite:36]
- Fontes de calendário macro e notícias.
- Dados correlacionados de índices, commodities, yields e dólar.
- Screenshots de gráficos, perfis de volume e painéis.

Pontos técnicos relevantes:

- O MT5 expõe funções para obter barras, ticks, market book, ordens e estado da conta em Python, o que viabiliza um pipeline de análise local centrado em dados estruturados.[cite:40]
- Webhooks do TradingView enviam um POST para uma URL definida pelo utilizador, o que é útil para acionar rotinas de análise, mas devem ser tratados como gatilhos de evento e não como o cérebro do sistema.[cite:36]

#### 3. Motores Analíticos

Cada classe de análise precisa de um motor próprio, com entrada, features, score e explicação. O erro comum é misturar tudo num prompt gigante; o desenho correto é decompor em módulos.

##### Motor técnico

Escopo:

- tendência e regime;
- suportes e resistências;
- consolidações e ranges;
- padrões gráficos;
- indicadores auxiliares.

Saídas esperadas:

- direção provável;
- estado de tendência;
- níveis relevantes;
- score de continuidade ou reversão.

##### Motor de price action

Escopo:

- leitura de candles;
- compressão e expansão;
- rejeição e aceitação;
- estrutura e contexto;
- qualidade do pullback e da continuação.

Objetivo:

- traduzir o comportamento cru do preço em primitives reutilizáveis, como `rejection`, `acceptance`, `displacement` e `failed_breakout`.

##### Motor fundamental

Escopo:

- juros, inflação, PIB, emprego e bancos centrais;
- eventos macro de alto impacto;
- risco geopolítico;
- alinhamento macro do dólar e moedas relacionadas.

Melhor prática:

- este motor não deve “prever candles”; deve classificar regime macro, risco de evento e viés de fundo.

##### Motor de sentimento

Escopo:

- humor do mercado;
- mudança de consenso;
- posicionamento agregado quando disponível;
- contexto narrativo dominante.

Limite:

- sentimento deve atuar como filtro e contexto, e não como gatilho isolado.

##### Motor intermarket

Escopo:

- relação entre forex, índices, commodities e yields;
- força relativa do dólar;
- correlações e descorrelações;
- confirmação ou conflito entre ativos relacionados.

Este motor é especialmente importante para evitar trades tecnicamente “bonitos” mas desalinhados com o resto do mercado.

##### Motor de volume

Escopo:

- análise de participação;
- expansão de volume;
- absorção e confirmação;
- força do movimento versus esforço.

Limite crítico:

- em forex spot/CFD, “volume” muitas vezes será proxy e não volume centralizado real, o que exige cuidado metodológico.[cite:57][cite:59]

##### Motor de Market Profile / Volume Profile

Escopo:

- POC;
- value area;
- HVN e LVN;
- zonas de aceitação e rejeição;
- contexto de leilão.

Fundamento prático:

- ferramentas como FX Market Profile da CME são baseadas em volume por nível de preço, reforçando que esta disciplina ganha mais robustez quando a fonte de dados é centralizada e de qualidade.[cite:57][cite:59]

##### Motor Wyckoff

Escopo:

- acumulação e distribuição;
- esforço versus resultado;
- absorção;
- manipulação e redistribuição;
- fase do ciclo operacional.

Objetivo:

- transformar leitura subjetiva em hipóteses rotuláveis, como `possible_accumulation`, `upthrust`, `spring`, `absorption_zone` e `effort_result_divergence`.

##### Motor ICT / SMC

Escopo:

- liquidez;
- killzones;
- displacement;
- fair value gaps;
- order blocks;
- market structure shifts;
- sweep de máxima/mínima;
- desequilíbrios.

Melhoria importante:

- ICT e SMC devem ser reduzidos a entidades de dados comuns, evitando jargão solto. Em vez de texto subjetivo, o motor deve devolver eventos explícitos como `liquidity_sweep`, `bullish_displacement`, `bearish_fvg` e `mss_confirmed`.

##### Motor de microestrutura

Escopo:

- ticks;
- spread;
- velocidade do tape;
- aceleração;
- burst de atividade;
- market book quando disponível no MT5.[cite:40]

Este motor é o substituto pragmático do “order flow perfeito” quando o projeto está restrito a forex/CFD via prop firm. Ele não entrega a mesma riqueza de um footprint de futuros, mas ainda pode medir qualidade de entrada, deterioração de spread e comportamento de curtíssimo prazo.[cite:40][cite:57]

##### Motor visual

O Gemma pode interpretar imagens, OCR e conteúdo visual, o que permite usar screenshots de gráfico, profile, dashboards e marcações visuais como evidência complementar.[cite:46][cite:47]

Uso correto:

- confirmação de padrões;
- leitura de estrutura visual;
- inspeção de screenshots anotados;
- detecção de conflito entre marcação humana e dados estruturados.

Uso incorreto:

- confiar apenas na imagem para decisões de scalping.

#### 4. Motor de tese

Este motor recebe a saída de todos os especialistas e monta um “case” operacional. A resposta final precisa ser estruturada e sempre incluir:

- ativo e timeframe;
- viés principal;
- cenário alternativo;
- invalidação;
- força do contexto;
- grau de alinhamento entre motores;
- riscos e motivos de veto;
- checklist operacional.

Formato recomendado de saída:

```json
{
  "symbol": "EURUSD",
  "timeframe": "M15",
  "bias": "bullish_but_fragile",
  "setup_type": "liquidity_sweep_reclaim",
  "confidence": 0.68,
  "alignment_score": 0.61,
  "invalidations": ["M15 close below X", "macro event in 20m"],
  "risk_notes": ["spread elevated", "USD intermarket mixed"],
  "verdict": "watch_only"
}
```

#### 5. Guardião de risco e prop firm

Esta camada deve ser determinística, auditável e mais forte do que qualquer tese analítica. Como regras de daily drawdown e max drawdown variam entre prop firms e podem ser calculadas em termos de saldo, equity ou modelos trailing, o sistema precisa modelar a firma específica antes de qualquer automação decisória.[cite:33][cite:38]

Regras mínimas:

- risco por trade entre 0.5% e 1%;
- limite de perda diária;
- limite de perda total;
- bloqueio por correlação excessiva;
- blackout em notícia de alto impacto;
- bloqueio por excesso de operações;
- veto quando a qualidade do contexto estiver abaixo do limiar.

Saídas do guardião:

- `allowed`;
- `watch_only`;
- `blocked`.

#### 6. Memória e aprendizado

O sistema deve ter **duas memórias distintas**.

##### Obsidian: memória semiestruturada e legível

Pastas sugeridas:

- `playbooks/`
- `pairs/`
- `indices/`
- `macro/`
- `sentiment/`
- `prop-rules/`
- `journals/`
- `postmortems/`
- `mistakes/`
- `screenshots/`
- `theses/`

Conteúdo ideal para o Obsidian:

- regras de setup;
- lições aprendidas;
- estudos de caso;
- resumos de pesquisa;
- revisões semanais;
- erros recorrentes;
- tese e pós-análise.

##### Banco estruturado: memória analítica

Campos sugeridos:

- símbolo;
- timeframe;
- timestamp;
- features calculadas;
- scores dos motores;
- tese final;
- veto ou aprovação;
- resultado posterior;
- drawdown virtual;
- rótulo do setup;
- qualidade da execução;
- comentários humanos.

Esta separação é essencial: Obsidian serve para conhecimento humano navegável; o banco serve para aprendizagem operacional, filtros e análise quantitativa.

## Fluxo operacional do sistema

### 1. Ingestão contínua

- Receber dados do MT5, alerts do TradingView e calendário macro.[cite:40][cite:36]
- Atualizar séries, ticks, spreads e book local quando disponível.[cite:40]
- Salvar snapshots e screenshots relevantes.

### 2. Pré-processamento

- Limpar e normalizar dados por ativo e timeframe.
- Extrair features de estrutura, volatilidade, regime, liquidez, spread e tempo de sessão.
- Gerar imagens e painéis para inspeção visual.

### 3. Análise especializada

- Rodar todos os motores aplicáveis ao ativo e ao contexto.
- Cada motor devolve score, explicação curta e evidência.
- Conflitos entre motores são marcados explicitamente.

### 4. Síntese da tese

- O orquestrador pede parecer ao motor de tese.
- O motor de tese identifica consenso, divergências e fragilidades.
- O guardião de risco decide se a tese pode ser tratada como observação, setup observável ou ideia vetada.[cite:33][cite:38]

### 5. Saída para o utilizador

Formato recomendado:

- resumo executivo;
- contexto multi-timeframe;
- visão macro;
- confirmação ou conflito intermarket;
- leitura de volume/profile/microestrutura;
- tese principal e tese alternativa;
- invalidação;
- observações de risco;
- conclusão: observar, esperar, evitar ou preparar cenário.

### 6. Pós-análise

- Registrar o que aconteceu depois.
- Comparar tese versus comportamento real.
- Salvar erro, acerto, contexto e lição em memória.
- Atualizar playbooks e filtros.

## Onde o projeto pode falhar

### 1. Excesso de ambição no MVP

Tentar cobrir todos os pares, todos os índices, todas as escolas de análise e múltiplas integrações logo no início tende a produzir um sistema frágil, lento e difícil de validar.

**Melhoria:** começar com 2 ou 3 pares, 1 índice, 3 ou 4 timeframes e um conjunto reduzido de motores, depois expandir de forma orientada por métricas.

### 2. Dependência excessiva do LLM

Se o modelo for tratado como motor de cálculo, de microestrutura e de decisão ao mesmo tempo, o sistema vai alucinar, generalizar demais e misturar narrativa com evidência. O uso correto do Gemma aqui é como orquestrador multimodal com ferramentas e não como substituto de toda a engenharia analítica.[cite:25][cite:46]

**Melhoria:** manter cálculos, regras e pontuações em módulos determinísticos, deixando ao LLM a síntese, comparação e explicação.

### 3. Ilusão de “order flow completo” em spot forex/CFD

Volume profile, order flow e footprint dependem muito da qualidade e centralização do dado. As referências da CME sobre FX Market Profile deixam claro que a lógica do profile está fortemente amarrada a volume por preço em contratos, algo estruturalmente diferente da visão parcial comum em spot/CFD.[cite:57][cite:59]

**Melhoria:** assumir uma arquitetura híbrida de `profile real quando houver fonte centralizada` e `microestrutura proxy quando a operação estiver no MT5 da prop firm`.

### 4. Falha de governança de risco

Prop firms costumam impor regras duras de drawdown e consistência, e essas regras variam de firma para firma.[cite:33][cite:38]

**Melhoria:** modelar uma firma específica primeiro, com simulador de regras, logs e testes de veto antes de expandir para outras.

### 5. Memória mal curada

Salvar tudo no Obsidian transforma o vault em lixo semântico. Quando a memória é ruidosa, a recuperação piora e o agente começa a citar notas irrelevantes ou contraditórias.

**Melhoria:** salvar apenas fatos persistentes, playbooks, teses, revisões e padrões de erro; usar templates fixos e taxonomia controlada.

### 6. Dados visuais sem contexto estruturado

A análise visual do Gemma é útil, mas não substitui série temporal, ticks e spread em operações rápidas.[cite:46]

**Melhoria:** usar visão como camada confirmatória e de auditoria visual, não como fonte primária de decisão.

### 7. Falta de rótulos e avaliação

Sem base histórica rotulada, o sistema vai parecer inteligente mas não terá feedback real para melhorar.

**Melhoria:** desde o início, guardar tese, score, resultado posterior, erro operacional e contexto de mercado em banco estruturado.

### 8. Mistura de escolas sem ontologia comum

Wyckoff, ICT, SMC, price action e volume profile podem descrever eventos semelhantes com nomes diferentes, o que causa redundância e conflito.

**Melhoria:** traduzir todas as escolas para uma ontologia comum de eventos e estados de mercado.

## Como melhorar cada parte

### Melhorias na camada de dados

- Criar snapshots por timeframe e ativo.
- Versionar features e indicadores.
- Registrar spread, slippage teórico e volatilidade por sessão.
- Associar cada tese a um pacote de dados reproduzível.

### Melhorias na camada analítica

- Definir contratos de entrada e saída para cada motor.
- Forçar cada motor a emitir score, explicação curta e evidência.
- Medir conflito entre motores e não esconder divergências.
- Manter um conjunto mínimo de primitives comuns entre todas as escolas.

### Melhorias na camada de tese

- Separar `bias`, `setup`, `timing`, `risk` e `confidence`.
- Criar score de alinhamento entre motores.
- Obrigar a presença de cenário alternativo e invalidação.
- Proibir conclusões binárias sem evidência multi-camada.

### Melhorias na memória

- Criar templates de notas no Obsidian.
- Criar rotina de revisão semanal e mensal.
- Separar conhecimento permanente de observações transitórias.
- Marcar notas com `confidence`, `source`, `symbol`, `setup_type` e `review_status`.

### Melhorias no aprendizado do sistema

- Alimentar com teus próprios journals e também journals externos curados.
- Adicionar screenshots anotados e pós-análises.
- Registrar divergência entre o que a IA sugeriu e o que o mercado fez.
- Atualizar playbooks com base em erros repetidos, não em um trade isolado.

### Melhorias na interface

- Criar uma vista “pré-trade” com resumo do setup.
- Criar uma vista “debate” com opiniões dos motores.
- Criar uma vista “post-mortem” com comparação entre tese e resultado.
- Criar uma vista “memória” para consulta das lições aprendidas.

## Roadmap recomendado

### Fase 1 — Fundação

- Escolher a prop firm inicial e modelar suas regras.[cite:33][cite:38]
- Integrar MT5 via Python para dados de mercado.[cite:37][cite:40]
- Integrar TradingView via webhook para alertas.[cite:36]
- Criar estrutura inicial do Obsidian.
- Implementar os motores: técnico, price action, fundamental e risco.

### Fase 2 — Profundidade

- Adicionar intermarket, sentimento e microestrutura.
- Adicionar motor visual com screenshots para Gemma.[cite:46][cite:47]
- Implementar score de consenso e score de conflito.
- Registrar tudo em banco estruturado.

### Fase 3 — Especialização

- Adicionar profile, Wyckoff, ICT e SMC.
- Consolidar ontologia comum de eventos.
- Criar playbooks por ativo e por setup.
- Iniciar revisão semanal assistida pela IA.

### Fase 4 — Maturidade

- Adicionar avaliação histórica de setups.
- Criar ranking por qualidade de contexto.
- Implementar bloqueios automáticos de baixa qualidade.
- Refinar prompts, ferramentas e templates com base em métricas.

## Requisitos técnicos iniciais

### Stack sugerida

- Python para integração MT5, cálculos, features, ETL e scoring.[cite:37][cite:40]
- Gemma local para orquestração, visão e síntese multimodal.[cite:25][cite:46][cite:47]
- Banco local como SQLite ou Postgres para memória estruturada.
- Obsidian para memória humana e gestão de conhecimento.
- Painel web local para chat, dashboards e revisão.

### Dados mínimos para o MVP

- OHLC multi-timeframe;
- ticks;
- spread;
- book local se disponível no broker/MT5.[cite:40]
- calendário macro;
- notícias;
- ativos correlacionados;
- screenshots de gráfico;
- journal manual.

## Definição de sucesso

O projeto estará no caminho certo quando conseguir:

- produzir análises consistentes e auditáveis;
- vetar setups ruins com mais frequência do que incentiva operações impulsivas;
- manter memória útil e reutilizável no Obsidian;
- melhorar a qualidade do teu processo, mesmo sem prometer prever mercado;
- criar uma base histórica suficientemente rica para revisão e refinamento.

## Conclusão

A melhor forma de construir uma IA especializada em trading não é tentar criar um modelo que “vira trader” sozinho, mas montar um sistema em que o LLM opera como coordenador multimodal de dados, motores e memória. O Gemma oferece compreensão de imagens e uso de ferramentas, o MT5 fornece acesso programático a dados e estado de mercado, o TradingView funciona como camada de eventos, e a disciplina de prop firm exige uma camada forte de veto e governança.[cite:25][cite:36][cite:40][cite:46]

O ponto mais crítico para o sucesso do projeto é aceitar que profundidade analítica vem de arquitetura e dados, não apenas do modelo. Se cada camada for bem desenhada, o sistema pode tornar-se um analista de trading realmente útil, especializado e cumulativo, sem cair na armadilha de prometer certeza onde o mercado oferece apenas probabilidade.[cite:24][cite:57][cite:59]
