<!-- relatorio_schemas_e_cobertura.md | Vitalia SPEC Kit v0.0.1 | 09-11-2026 11:05(GMT-04:00) -->
> **relatorio_schemas_e_cobertura.md | Vitalia SPEC Kit v0.0.1 | 09-11-2026 11:05(GMT-04:00)**

# Relatório de Diagnóstico: Mapeamento de Schemas, Uso Atual e Lacunas para Cobertura Contratual Total

## 1. Inventário Comparativo de Schemas: `~/.vitalia/` vs. `source/`

Atualmente, o ecossistema apresenta uma bifurcação entre a instalação global legada (`~/.vitalia/`) e o repositório fonte da nova arquitetura (`source/`):

### 1.1. Schemas no Repositório Fonte (`source/src/schemas/`) — 13 Schemas Ativos

Todos os 13 schemas em `source/src/schemas/` foram auditados e cumprem estritamente o **Subset OpenAPI 3.0 Limpo** (sem `$schema`, sem `title` na raiz, sem `additionalProperties: false` em configs, e sem tipos em array):

| # | Arquivo de Schema | Tipo de Alvo | `schema_type` Declarado | Onde e Como é Utilizado Hoje |
|---|-------------------|--------------|-------------------------|------------------------------|
| 1 | `agents_catalog.schema.json` | Catálogo YAML | `agents_catalog` | Valida `source/profiles/agents_catalog.yaml` no teste `test_contracts_and_handoff.py`. |
| 2 | `brainstorming_intents.schema.json` | Catálogo YAML | `brainstorming_intents` | Valida `source/profiles/brainstorming_intents.yaml` no teste `test_contracts_and_handoff.py`. |
| 3 | `constitution.schema.json` | Catálogo YAML | `constitution` | Valida `source/profiles/constitution.yaml` no teste `test_contracts_and_handoff.py`. |
| 4 | `dynamic_questioning.schema.json` | Catálogo YAML | `dynamic_questioning` | Valida `source/profiles/dynamic_questioning.yaml` no teste `test_contracts_and_handoff.py`. |
| 5 | `grounding_domains.schema.json` | Catálogo YAML | `grounding_domains` | Valida `source/profiles/grounding_domains.yaml` no teste `test_contracts_and_handoff.py`. |
| 6 | `routing_table.schema.json` | Catálogo YAML | `routing_table` | Valida `source/profiles/routing_table.yaml` no teste `test_contracts_and_handoff.py`. |
| 7 | `guardian_profile.schema.json` | Lente YAML | `guardian_profile` | Valida todas as 14 lentes `gp_*.yaml` em `source/profiles/` no teste `test_contracts_and_handoff.py`. |
| 8 | `context-lifting-envelope.schema.json` | Envelope JSON | `context_envelope` | Define o contrato do JSON gerado por `vitalia_hook_runner.py` (validado em `test_runtime_and_guardian.py`). |
| 9 | `vitalia-handoff-v1.0.0.json` | Handoff JSON | `vitalia_handoff` | Valida arquivos de transição gerados por `vitalia_handoff.py create` (utilizado pelo CLI em tempo de execução). |
| 10 | `decision_schema.json` | Ledger JSONL | `decision` | Documenta a estrutura de `decisions.jsonl` (lido pelo prompt de `session-end.toml` e `session-consolidate.toml`). |
| 11 | `learning_schema.json` | Ledger JSONL | `learning` | Documenta a estrutura de `learnings.jsonl` (lido pelo prompt de `session-end.toml` e `session-consolidate.toml`). |
| 12 | `grounding_domain_schema.json` | Ledger JSONL | (evento/ledger) | Documenta a estrutura de `grounding-domains.jsonl` (lido por `session-end.toml` e `session-consolidate.toml`). |
| 13 | `session_history_schema.json` | Shard JSON | `session_shard` | Documenta a estrutura de `.vitalia/memory/session/data/shards/<machine_id>.json`. |

---

### 1.2. Schemas no Kit Global Legado (`~/.vitalia/`) — 14 Schemas

No ambiente `~/.vitalia/`, os schemas estão fragmentados em pastas diferentes (`config/schemas/` e `src/schemas/`), refletindo fases anteriores de desenvolvimento:

| Arquivo em `~/.vitalia/` | Status e Função |
| :--- | :--- |
| `config/schemas/agents_catalog.schema.json` | Versão intermediária do catálogo de agentes. |
| `config/schemas/ambiguity_taxonomy_schema.json` | **Exclusivo do legado:** Schema da taxonomia de 10 categorias de ambiguidades usada pelo antigo comando CLI `/vitalia-clarify`. Ausente de `source/`. |
| `config/schemas/decision_schema.json` | Cópia de estrutura de decisões. |
| `config/schemas/grounding_domain_schema.json` | Cópia do validador de eventos de domínios. |
| `config/schemas/learning_schema.json` | Cópia de estrutura de aprendizados. |
| `config/schemas/session_history_schema.json` | Cópia de estrutura de shards. |
| `src/schemas/constitution.schema.json` | Cópia da constituição com meta-campos Draft-07 (violando OpenAPI 3.0 limpo). |
| `src/schemas/guardian_payload.schema.json` | Schema do payload antigo do Guardian com podas e tokens. |
| `src/schemas/guardian_profile.schema.json` | Schema antigo de perfis `gp_*.yaml`. |
| `src/schemas/hook_runner_output.schema.json` | Schema de saída do hook runner legado. |
| `src/schemas/tmp_cleanup_matrix.schema.json` | **Exclusivo do legado:** Schema do faxineiro de disco de `tmp/` (responsável pelo ruído de contexto no hook runner antigo). |
| `src/schemas/vitalia-handoff-v1.0.0.json` | Schema de handoff v1. |
| `src/hooks/sdd_judge/contracts/section_eval_schema.json` | **Exclusivo do legado:** Schema de saída do script CLI `sdd_judge.py` fatiado em 400 tokens. |
| `src/hooks/sdd_judge/contracts/task_eval_schema.json` | **Exclusivo do legado:** Schema de avaliação de tasks do script CLI `sdd_judge.py`. |

---

## 2. Como os Schemas são Utilizados Hoje (Mapeamento de Fluxo)

Atualmente, o uso de schemas no Vitalia SPEC Kit ocorre em três camadas distintas:

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAMADA 1: Testes Automatizados (CI / Pytest)                           │
│ - test_contracts_and_handoff.py carrega os 6 catálogos YAML e as 14    │
│   lentes gp_*.yaml e valida contra os schemas via jsonschema.validate()│
│ - Garante que ninguém altere um YAML quebrando a estrutura esperada.   │
├────────────────────────────────────────────────────────────────────────┤
│ CAMADA 2: CLI Determinístico em Runtime (Handoffs)                     │
│ - vitalia_handoff.py create instancia jsonschema.validate()            │
│   contra vitalia-handoff-v1.0.0.json antes de salvar o arquivo no disco│
│ - Se inválido, o processo falha imediatamente com exit code 1.         │
├────────────────────────────────────────────────────────────────────────┤
│ CAMADA 3: Documentação Cognitiva Injetada no Prompt do LLM             │
│ - session-end.toml e session-consolidate.toml leem schemas como        │
│   arquivos de texto (context.reads) para instruir o LLM a gerar os     │
│   arquivos temporários temp_learnings.json e temp_decisions.json.      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Diagnóstico de Lacunas: Onde Falta Implantar para Cobertura Contratual Total (100% DbC)

Com base na pesquisa profunda de **Design by Contract (DbC)** realizada neste turno, identificamos **6 lacunas críticas** onde o sistema ainda opera de forma estocástica/implícita sem validação formal por schema:

### Lacuna 1: Validação de Envelopes de Context Lifting em Tempo de Execução
* **Situação Atual:** O schema `context-lifting-envelope.schema.json` existe em `source/src/schemas/`, mas é validado apenas em testes unitários (`test_runtime_and_guardian.py`).
* **Risco:** O `vitalia_hook_runner.py` gera o arquivo JSON de contexto e salva no disco sem validar contra o schema. Se houver falha de serialização, campos faltantes ou injeção nula, a IDE recebe um envelope corrompido sem aviso.
* **Cobertura Necessária:** O `vitalia_hook_runner.py` deve validar o dicionário `data` contra `context-lifting-envelope.schema.json` antes de emitir o stub para a IDE.

### Lacuna 2: Validação Determinística de Artefatos de Memória Temporária
* **Situação Atual:** No encerramento da sessão (`session-end`), o modelo cria `.vitalia/temp_learnings.json` e `.vitalia/temp_decisions.json`. Em seguida, o `vitalia_context_engine.py` lê esses arquivos e faz append nos arquivos `.jsonl`.
* **Risco:** Se o modelo alucinar uma chave (ex: `titulo` em vez de `learning` ou esquecer `rationale`), o `vitalia_context_engine.py` ingere o dado inválido e polui permanentemente a memória 3-Tier.
* **Cobertura Necessária:** O `vitalia_context_engine.py` deve validar cada item de `temp_learnings.json` contra `learning.schema.json` e `temp_decisions.json` contra `decision.schema.json` antes de persistir em `.jsonl`.

### Lacuna 3: Contratos Formais de Entrada/Saída para Artefatos SDD (Pós-Condições Estruturais)
* **Situação Atual:** Os arquivos `.toml` declaram `context.writes = ["specs/*/spec.md"]`, mas a conformidade do Markdown gerado é avaliada apenas visualmente ou por regex no `sdd-judge`.
* **Risco:** Specs sem requisitos funcionais numerados (`FR-xxx`), sem critérios de aceite (`SC-xxx`), sem tabela de rastreabilidade ou plans sem arquitetura de componentes passam despercebidos até a fase de implementação.
* **Cobertura Necessária:** Criação de schemas OpenAPI 3.0 para a estrutura mínima dos artefatos canônicos:
  - `spec_artifact.schema.json` (validação de metadados e seções obrigatórias do spec.md).
  - `plan_artifact.schema.json` (validação de componentes, decisões de stack e TDA).
  - `tasks_artifact.schema.json` (validação de formato de tarefas `Txxx [P] [USx]`).
  - `inspection_report.schema.json` (validação do relatório emitido pelo SDD-Judge).

### Lacuna 4: Cobertura dos 10 Agentes Especialistas Planejados
* **Situação Atual:** O `agents_catalog.yaml` lista 10 agentes especialistas no status `planned` (`medical-gate`, `design-thinking`, `literature-curator`, `visual-creator`, `master-ai-control`, `django-stark`, `react-vinci`, `infra-nomad`, `cortex-analyst`, `figma-maestro`), mas:
  - Não existem arquivos `.toml` para eles em `source/extensions/`.
  - Não existem lentes `gp_*.yaml` para eles em `source/profiles/`.
* **Cobertura Necessária:** Criar os contratos formais (`.toml`), schemas de entrada/saída e lentes sem poda para cada um desses agentes.

### Lacuna 5: Schemas de Domínio Específico (Saúde, Ciência e Design)
* **Situação Atual:**
  - O fluxo de saúde clínica possui o gate P09, mas não possui schema para validar o `risk_report.json` ou faixas de biomarcadores.
  - A revisão integrativa de literatura não possui schema para validar a matriz de extração PRISMA 2020 (`prisma_extraction.schema.json`).
* **Cobertura Necessária:** Formalizar os esquemas de dados de saída para os especialistas verticais.

### Lacuna 6: Dynamic Schema Registry (Descoberta Automática de Schemas)
* **Situação Atual:** A associação entre arquivo YAML e seu Schema JSON é mapeada por uma lista estática de tuplas dentro de `test_contracts_and_handoff.py`:
  ```python
  pairs = [
      ("agents_catalog.yaml", "agents_catalog.schema.json"),
      ...
  ]
  ```
* **Risco:** Qualquer novo perfil YAML ou schema adicionado exige modificar manualmente o código de teste, quebrando a dinamicidade do kit.
* **Cobertura Necessária:** Implementar um **Schema Registry Dinâmico** (`schema_registry.py`) que inspeciona o campo `schema_type` no cabeçalho do arquivo YAML e localiza dinamicamente `<schema_type>.schema.json`.

---

## 4. Tabela de Cobertura Alvo (Meta 100% DbC)

| Camada do Sistema | Schemas Atuais | Schemas Necessários para Cobertura Total | Status de Cobertura |
| :--- | :---: | :---: | :---: |
| **Configurações & Catálogos Globais** | 6 | 6 (cobertura total já atingida) | ✅ 100% |
| **Lentes Guardian (`gp_*.yaml`)** | 1 (`guardian_profile`) | 1 (valida todas as lentes dinamicamente) | ✅ 100% |
| **Handoff Inter-Agentes** | 1 (`vitalia-handoff-v1`) | 1 (valida qualquer transição) | ✅ 100% |
| **Envelopes de Context Lifting** | 1 (`context-lifting`) | 1 (necessário ativar validação em runtime no hook runner) | 🟡 50% (falta hook ativo) |
| **Ledgers de Memória 3-Tier** | 4 (`decision`, `learning`, etc.) | 4 (necessário ativar validação em runtime no context engine) | 🟡 50% (falta hook ativo) |
| **Artefatos do Pipeline SDD** | 0 | 4 (`spec_artifact`, `plan_artifact`, `tasks_artifact`, `inspection_report`) | 🔴 0% (lacuna estrutural) |
| **Especialistas Verticais (Saúde/Ciência)** | 0 | 2 (`clinical_risk_report`, `prisma_extraction`) | 🔴 0% (lacuna estrutural) |

---
<sub>Documento gerado para fundamentação da revisão contratual em `TEMP/`.</sub>

