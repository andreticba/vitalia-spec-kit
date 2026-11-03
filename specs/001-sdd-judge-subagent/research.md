<!-- research.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:20(GMT-04:00) -->
> **research.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:20(GMT-04:00)**

# Technical Research & Arquitetura: Sub-Agente SDD-Judge & Governança Constitucional

**Data:** 02-11-2026 23:20(GMT-04:00)  
**Feature:** `specs/001-sdd-judge-subagent`  
**Escopo:** Sub-Agente nativo, técnicas anti-diluição, contratos OpenAPI 3.0 e saneamento de extensões  

---

## 1. Decisão Técnica 1: Formato do Sub-Agente e Ambiente de Execução
- **Escolhido**: Sub-Agente nativo operando na IDE Antigravity acionado via slash command `/vitalia-judge` e orquestrado com perfil de inteligência `frontier` (Google Gemini 1.5/2.0/3.0 Pro com janela de 1M–2M tokens).
- **Verificado em**: [Google DeepMind — Gemini Technical Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_1_5_report.pdf) em 02-11-2026 e [Gemini Structured Outputs Guide](https://ai.google.dev/gemini-api/docs/structured-outputs) em 02-11-2026.
- **Justificativa**: A abordagem anterior baseada no script CLI `sdd_judge.py` e chamadas REST fragmentadas impunha limites de VRAM de 400 tokens e truncamentos cegos de contexto, degradando severamente a acurácia de verificação constitucional. Operar o juiz como sub-agente nativo na IDE com janela de fronteira permite carregar a Constituição integral (~3.000 tokens) sem truncamento e sem custos de infraestrutura local de GPU.
- **Alternativas**:
  - *Ollama local com modelo 7B (Mistral/Qwen)*: Rejeitado nesta fase embrionária devido à degradação comprovada em tarefas de raciocínio adversarial complexo e à restrição de VRAM de 6 GB da máquina local, postergado para fase futura com dados sensíveis on-premise.
  - *CLI script `sdd_judge.py` fatiado*: Rejeitado devido ao fenômeno crônico de rule dilution e truncamento arbitrário de regras fundamentais.

---

## 2. Decisão Técnica 2: Mitigação Industrial de Degradação de Atenção (Anti-"Lost in the Middle")
- **Escolhido**: Sanduíche Constitucional (Attention Sandwich) associado a Inverted Chain-of-Thought (Critique-First), Delimitação por Tags XML de Autoridade e Matriz de Confronto 1-a-1.
- **Verificado em**: 
  - [arXiv:2307.03172 — Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) em 02-11-2026.
  - [Anthropic Research — Constitutional AI: Harmlessness from AI Feedback (arXiv:2212.08073)](https://arxiv.org/abs/2212.08073) em 02-11-2026.
  - [NIST AI Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/itl/ai-risk-management-framework) em 02-11-2026.
- **Justificativa**: A literatura empírica comprova que modelos de linguagem apresentam degradação em formato de U ("curva de atenção posicional"), retendo informações no início (Primacy) e no final (Recency). Ao abrir o prompt com as regras constitucionais e reinjetar o checklist imperativo no fechamento imediatamente antes do veredito, neutraliza-se a diluição em contextos extensos.
- **Alternativas**:
  - *System Prompt plano único*: Rejeitado por sofrer diluição de até 40% em prompts longos com múltiplos artefatos.
  - *RAG semântico com embeddings locais*: Rejeitado por fragmentar cláusulas constitucionais que dependem de leitura contextual holística.

---

## 3. Decisão Técnica 3: Padrão Obrigatório de Schemas Contratuais (OpenAPI 3.0 Gemini-Compliant)
- **Escolhido**: Subset estrito de OpenAPI 3.0 puro (`type`, `properties`, `required`, `items`, `description`, `enum`), proibindo categoricamente `$schema`, `title` (como nó raiz de validação) e `additionalProperties: false`.
- **Verificado em**: [Google GenAI REST API Reference — Schema Object](https://ai.google.dev/api/rest/v1beta/CachedContent#Schema) em 02-11-2026.
- **Justificativa**: O compilador REST e de gramática formal do Google Gemini rejeita propriedades meta de JSON Schema Draft-07 gerando erro HTTP 400 (`Invalid JSON payload received. Unknown name "$schema"`). Schemas limpos em OpenAPI 3.0 compilam nativamente sem falhas.
- **Alternativas**:
  - *JSON Schema Draft-07 tradicional*: Rejeitado por incompatibilidade documentada com a API REST de Structured Outputs do Gemini.
  - *Pydantic direto no CLI*: Rejeitado para interfaces de artefatos estáticos, pois exige runtime Python e não serve como schema universal de transporte.

---

## 4. Decisão Técnica 4: Saneamento das Extensões em `source/extensions/`
- **Escolhido**: Refatoração cirúrgica dos 4 arquivos TOML canônicos do SDD (`spec-specify.toml`, `spec-plan.toml`, `spec-tasks.toml`, `converge.toml`), removendo chamadas ao CLI legado e estabelecendo o despacho mandatório para a IDE (/vitalia-judge).
- **Verificado em**: [GitHub Spec Kit Repository](https://github.com/github/spec-kit) em 02-11-2026.
- **Justificativa**: Garante transição fluida sem quebra de retrocompatibilidade para o desenvolvedor, ao mesmo tempo em que elimina de vez a execução do script CLI problemático.
- **Alternativas**:
  - *Manter script CLI como fallback*: Rejeitado pela regra soberana de governança (Regra 6 em `AGENTS.md`) que proíbe execução de `sdd_judge.py` no terminal.

---

## 5. Rastro de Verificação de Grounding (P03)

| # | Tecnologia / Conceito | Fonte Oficial Verificada (HTTP 200) | Data de Verificação | Status |
|---|---|---|:---:|:---:|
| 1 | Gemini Frontier & Long Context (1M-2M tokens) | [Google DeepMind Gemini Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_1_5_report.pdf) | 02-11-2026 | Confirmado |
| 2 | Fenômeno "Lost in the Middle" | [arXiv:2307.03172](https://arxiv.org/abs/2307.03172) | 02-11-2026 | Confirmado |
| 3 | Constitutional AI & Rule Hierarchies | [Anthropic Research arXiv:2212.08073](https://arxiv.org/abs/2212.08073) | 02-11-2026 | Confirmado |
| 4 | Gemini Structured Outputs & Schema Specs | [Google GenAI Docs](https://ai.google.dev/gemini-api/docs/structured-outputs) | 02-11-2026 | Confirmado |
| 5 | OpenAPI Specification 3.0.3 | [OpenAPI Initiative](https://spec.openapis.org/oas/v3.0.3) | 02-11-2026 | Confirmado |
| 6 | Spec Kit Convention (`specs/<NNN>-<slug>/`) | [GitHub Spec Kit Repository](https://github.com/github/spec-kit) | 02-11-2026 | Confirmado |
