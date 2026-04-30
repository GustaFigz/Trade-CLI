# Treino — Material de Aprendizado

Base de conhecimento estruturada para alimentar Trade-CLI com conceitos e padrões.

## Estrutura

### [[treino/livros]]
PDFs, transcrições de vídeos, materiais de estudo estruturados.

### [[treino/videos-resumos]]
Resumos em markdown de vídeos educativos e webinars.

### [[treino/journals-externos]]
Diários de trading de outros traders para aprendizado.

### [[treino/estudos-de-caso]]
Análises detalhadas de trades históricos: setup, execução, resultado, lição.

## Processo de Treinamento

1. **Ingerir** → Colocar material em uma subpasta
2. **Processar** → `python main.py train --file "arquivo.pdf" --topic "ict"`
3. **Revisar** → Abrir em Obsidian, validar, adicionar links
4. **Ativar** → `python main.py knowledge activate --id NOTE_ID`
5. **Usar** → Disponível para RAG durante análises

## Material Prioritário para Alimentar

### High Priority (FTMO Critical)
- [ ] Regras FTMO completas
- [ ] Drawdown management
- [ ] Risk sizing rules

### High Priority (Methodology)
- [ ] ICT concepts (Killzones, FVG, Order Blocks)
- [ ] SMC concepts (MSS, Displacement)
- [ ] Wyckoff phases

### Medium Priority
- [ ] Price Action patterns
- [ ] Volume Profile
- [ ] Your own trading journal

## Status de Treinamento

| Tópico | Docs | Status | Confiança |
|--------|------|--------|-----------|
| ICT | 0 | Pendente | - |
| SMC | 0 | Pendente | - |
| Wyckoff | 0 | Pendente | - |
| FTMO | 0 | Pendente | - |
| Price Action | 0 | Pendente | - |

---

*Quanto mais conhecimento alimentar, melhor o sistema fica*  
*Qualidade > Quantidade — notas bem estruturadas valem mais que dumps*

Atualizado: {{data}}
