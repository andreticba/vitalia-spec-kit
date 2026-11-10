<!-- inventario.md | Vitalia SPEC Kit v0.0.1 | 09-11-2026 23:20(GMT-04:00) -->
# 📋 Inventário Geral dos Artefatos de Concepção e Revisão Técnica (Pasta `TEMP/`)

> **Data de Consolidação:** 09-11-2026 23:20 (GMT-04:00)  
> **Status do Repositório:** `source/` e `~/.vitalia/` 100% limpos e preservados  
> **Finalidade:** Servir como índice executivo e referência unificada para a elaboração e implementação da próxima especificação SDD formal.

---

## 1. Tabela-Mestra de Artefatos Gerados

| Arquivo | Tamanho | Categoria | Finalidade e Escopo |
| :--- | :---: | :---: | :--- |
| [`revisao_contratual_workflows_sdd.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/TEMP/revisao_contratual_workflows_sdd.md) | ~98 KB | Contratos & Governança | **Documento central do ciclo SDD.** Contém os 16 workflows `.toml` revisados com blocos quádruplos de código, o Motor Dinâmico de Sub-Agentes no Arquiteto, os 14 perfis `gp_*.yaml` sanitizados de números estáticos, a separação do `ambiguity_scoring.yaml` e a suíte de sensores VRSS. |
| [`revisao_contratual_agentes_especialistas.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/TEMP/revisao_contratual_agentes_especialistas.md) | ~27 KB | Arquitetura de Agentes | **Catálogo das 4 Verticais Especialistas.** Apresenta diagrama vertical desacoplado (Saúde Clínica $\to$ Pesquisa & Ciência $\to$ Design & Produto $\to$ Engenharia & SDD), contratos dos 10 agentes especialistas planejados e 8 extensões complementares de suporte. |
| [`relatorio_contratos_sdd_e_faxineiro.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/TEMP/relatorio_contratos_sdd_e_faxineiro.md) | ~12 KB | Pesquisa & Manutenção | **Padrões da Indústria e Faxineiro de Contexto.** Consolidação de OpenSpec, GitHub Spec Kit, Google AIPs e AWS Smithy; especificação formal do `vitalia_tmp_cleanup.py` interativo por data `[a/d/n/t]`. |
| [`relatorio_schemas_e_cobertura.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/TEMP/relatorio_schemas_e_cobertura.md) | ~13 KB | Qualidade & DbC | **Auditoria Comparativa de Schemas JSON.** Diagnóstico dos 4 schemas ativos vs 9 schemas de teste; roteiro de centralização e migração em `source/src/schemas/` para cobertura total DbC. |
| [`roteiro_testes_maquina_limpa_wsl2.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/TEMP/roteiro_testes_maquina_limpa_wsl2.md) | ~8 KB | Validação & QA | **Roteiro de Testes em Ambiente Limpo.** Guia executável para validação no WSL2/zsh: bootstrap isolado, `install-project`, isolamento de Git, pytest e teste automatizado da flag `--help` didática. |

---

## 2. Síntese das Decisões Arquiteturais e Contratuais Assentadas

### 2.1. Dinamicidade Constitucional e Erradicação de Números Mágicos
- **Constituição Viva:** Banimento de qualquer referência a contagens fixas ("P00 a P17", "P01", "P03", "P05", etc.) nos arquivos `.toml`, perfis `gp_*.yaml` e código. O Guardian (§11) injeta 100% da Constituição ativa em runtime sem cortes (`total_budget: 0`, `no_prune: true`).
- **Taxonomia Viva:** Banimento de "10 categorias". A inspeção consome dinamicamente o catálogo injetado no contexto.
- **Inverted Chain-of-Thought (Inverted CoT):** No `judge.toml`, vereditos (`PASS`, `WARN`, `BLOCK`) são emitidos estritamente ao final da crítica detalhada.

### 2.2. Porta de Entrada Socrática Universal e Portão HITL
- O workflow `/vitalia-brainstorming` é a porta de entrada socrática para qualquer intenção humana.
- Turnos socráticos com no máximo 3 perguntas aguardam obrigatoriamente a resposta do usuário antes de prosseguir.
- A emissão de `research-brainstorming.md` é terminantemente condicionada à aprovação explícita e soberana do usuário.

### 2.3. Motor Dinâmico de Sub-Agentes no `vitalia-architect` (Padrão `vitalia-route`)
- O `architect.toml` opera o despacho de especialistas via catálogo dinâmico (`agents_catalog.yaml`), sem acoplamento de agentes em seu prompt.
- Ao detectar um spike técnico (ORM, Frontend, DevOps, Segurança, Clínico, Científico), define dinamicamente (`define_subagent`), invoca com Bounded Spike (`invoke_subagent`), suspende a execução e acorda reativamente sem polling.
- Novos especialistas adicionados a `agents_catalog.yaml` tornam-se imediatamente utilizáveis pelo Arquiteto sem alterar seu prompt.

### 2.4. Trilha de Auditoria de Handoffs de Sub-Agentes
- Os handoffs criados pelo Arquiteto para especialistas efêmeros são assentados em disco em `.vitalia/memory/data_storage/context/`.
- Diagnóstico de `vitalia_handoff.py`: O script atual fixa o salvamento em `handoffs/`. Foi planejada a adição de `--storage-subdir context` e extensões de `intent_type` (`architect_spike_dispatch` e `specialist_spike_response`) para a spec formal de implementação.

### 2.5. Separação de Responsabilidade Única (SRP) no Cálculo de Ambiguidades
- **`grounding_domains.yaml`:** Preserva sua responsabilidade exclusiva de autoridade de pesquisa temporal, URLs oficiais (HTTP 200), fontes autoritativas e janelas de validade.
- **`source/profiles/ambiguity_scoring.yaml` (Novo):** Perfil dedicado contendo a escala de impacto (1 a 5, ISO 29148 / FMEA), escala de incerteza (1 a 5, NASA ARM), multiplicadores regulatórios por domínio e limiares de severidade.
- **`source/src/schemas/ambiguity_scoring.schema.json` (Novo):** Schema formal de validação do arquivo de pontuação.
- **`sdd_ambiguity_scorer.py` (Novo Script Python):** Utilitário CLI determinístico que realiza o cálculo puro de `Priority Score` ($Impacto \times Incerteza \times PesoDomínio$) e densidade formal, validando o JSON final via `jsonschema` contra `ambiguity_taxonomy_schema.json` (eliminando cálculos mentais por LLM).

### 2.6. Princípio Constitucional Mandatório: `--help` Didático com Exemplos
- **Regra Instituída:** 100% dos scripts executáveis e ferramentas CLI do Kit DEVEM implementar a flag `--help` detalhada com exemplos práticos de uso.
- **Fiscalização Contínua:** Integrada às diretrizes normativas gerais, ao perfil adversarial `gp_task-verifier.yaml` e ao roteiro de testes em máquina limpa.

### 2.7. Suíte de Sensores em Tempo Real (Vitalia Runtime Sensor Suite — VRSS)
- Estruturação de 5 sensores essenciais:
  1. *Contrato & DbC:* Validação de esquemas JSON, OpenAPI 3.0 e invariantes.
  2. *Execução Comportamental:* Exit code sentinel, poda de tracebacks do Pytest e detecção de testes flaky.
  3. *Estático & Código:* AST parse imediato pós-escrita, Git diff churn (blast radius) e bloqueio de anti-patterns.
  4. *Cognitivo & Contexto:* Saturação de tokens, mitigação de Lost-in-the-Middle e circuit breaker para loops de repetição.
  5. *Limpeza & Preservação:* Detecção de arquivos órfãos e blindagem de pastas de contrato (`.agents/skills/`).
- Pipeline de feedback anti-ruído: *Slicing & Redaction* $\to$ *Structured Error Envelope (JSON)* $\to$ *§11 Context Lifting* $\to$ *Inverted CoT Guardrail*.

### 2.8. Novo Faxineiro de Contexto Interativo (`vitalia_tmp_cleanup.py`)
- Substitui a exclusão indiscriminada de arquivos de contexto.
- Agrupa arquivos de sessões anteriores por data em `.vitalia/memory/data_storage/context/<machine_id>/`.
- Protege a sessão ativa do dia e oferece menu interativo: `[a]` apagar tudo (exceto hoje), `[d]` selecionar datas específicas, `[n]` não apagar nada (padrão) e `[t]` apagar tudo.

---

## 3. Estado dos Ambientes e Diretórios

```
vitalia-spec-kit/ (Repositório Local)
├── source/                  [100% INTACTO E PRESERVADO — sem modificações precipitadas]
├── specs/                   [Contratos e especificações SDD anteriores preservados]
├── .vitalia/                [Metadados locais de desenvolvimento]
└── TEMP/                    [ÁREA DE CONCEPÇÃO ATUAL — 5 relatórios técnicos + este inventário]
    ├── inventario.md                                (Este inventário consolidado)
    ├── revisao_contratual_workflows_sdd.md          (Contratos dos 16 workflows, perfis e sensores)
    ├── revisao_contratual_agentes_especialistas.md  (Contratos dos 10 especialistas e 8 extensões)
    ├── relatorio_contratos_sdd_e_faxineiro.md       (Padrões SDD e especificação do faxineiro)
    ├── relatorio_schemas_e_cobertura.md             (Mapeamento de 100% DbC dos schemas)
    └── roteiro_testes_maquina_limpa_wsl2.md         (Runbook de validação em WSL2/zsh)
```

---
<sub>Inventário formal concluído. Todo o arcabouço técnico e contratual está pronto para ser consumido na elaboração da nova especificação SDD.</sub>

