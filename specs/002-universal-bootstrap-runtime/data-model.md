<!-- data-model.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:49(GMT-04:00) -->
> **data-model.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:49(GMT-04:00)**

# Data Model: Universal Bootstrap, Runtime Autônomo em 4 Camadas & Blindagem SDD (`specs/002-universal-bootstrap-runtime`)

- **Fontes Canônicas:**
  - [`.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md)
  - [`specs/002-universal-bootstrap-runtime/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/spec.md)

---

## 1. Visão Geral do Armazenamento em 4 Camadas (Filesystem-Only — P07, P11)

O Vitalia SPEC Kit v0.0.1 persiste estado exclusivamente em arquivos estruturados (`JSON`, `JSONL`, `YAML`, `TOML` e `Markdown`) distribuídos nas camadas isoladas:

- **Camada 2 (`${VITALIA_KIT_DIR}/`):** Catálogos e perfis imutáveis em runtime (`profiles/*.yaml`, `extensions/*.toml`, `src/schemas/*.json`, `templates/dashboard_template.md`).
- **Camada 3 (`<project_root>/.vitalia/memory/session/`):** Repositório Git dedicado ao contexto de sessão 3-Tier (`shards/<machine_id>.yaml`, `data/{decisions,learnings,session_history}.jsonl`, `README.md`, `SESSION_STATE.md`, `DECISIONS.md`, `LEARNINGS.md`, `SESSION_HISTORY.md`).
- **Camada 4 (`<project_root>/.vitalia/memory/data_storage/`):** Repositório Git dedicado aos dados operacionais (`context/<machine_id>/<workflow>_<ts>_<hash>.json`, `handoffs/handoff_<src>_to_<dst>_<uuid8>.json`, `research/*.md`).

---

## 2. Entidades Persistidas

### Entity: `ContextLiftingEnvelope`
- **Localização:** `<project_root>/.vitalia/memory/data_storage/context/<machine_id>/<workflow>_<YYYYMMDD_HHMMSS>_<hash12>.json`
- **Campos:**
  - `description`: `string` — descrição do workflow extraída do `.toml`.
  - `meta`: `object` (`version: "0.0.1"`, `hardware_profile: "frontier"`, `domain_gates: string[]`, `model_profile: "flash" | "pro"`).
  - `hooks`: `object` (`before: string[]`, `after: string[]`).
  - `tools`: `object` (`required: string[]`, `optional: string[]`).
  - `context`: `object` (`reads: string[]`, `writes: string[]`).
  - `variables`: `object` (`input: string[]`, `output: string[]`).
  - `transport`: `object` (`preferred: "filesystem"`, `file_path: string`, `session_shard: boolean`).
  - `guardian`: `object` (`yaml_sources: string[]`, `guardian_profile: string`, `prompt: string`, `hardware_profile: "frontier"`).
  - `guardian_json`: `GuardianPayload` — contexto dinâmico injetado sem poda.
- **Relacionamentos:** Gerado por `vitalia_hook_runner.py` + `guardian_context.py` a partir de `extensions/<workflow>.toml`, `profiles/gp_*.yaml`, `profiles/*.yaml` e `.vitalia/memory/session/data/*.jsonl`.
- **Ciclo de Vida:** Criado na fase `--phase before` de qualquer workflow `/vitalia-*`; lido pela IA via `view_file`/`read_file` a partir do Stub JSON emitido no `stdout`.

---

### Entity: `GuardianPayload` (`guardian_json`)
- **Localização:** Embutido dentro de `ContextLiftingEnvelope.guardian_json`.
- **Campos:**
  - `schema_version`: `string` (`"0.0.1"`).
  - `workflow`: `string` — identificador do workflow ativo.
  - `timestamp`: `string` — formato estrito `DD-MM-YYYY HH:MM:SS(GMT-04:00)`.
  - `sources`: `object` — mapa contendo 100% das fontes solicitadas em `yaml_sources` **sem poda** (`constitution` com todos os 18 princípios `P00`–`P17`, `grounding_domains`, `dynamic_questioning`, `brainstorming_intents`, `agents_catalog`, `routing_table`).
  - `phase_guardrails`: `object` — guardrails mandatórios da lente `gp_*.yaml` da fase.
  - `phase_profiles`: `object` — sub-perfis de inspeção por modo (ex: `specify`, `plan`, `tasks`, `after_task`, `clarify`, `converge`).
  - `grounding_status`: `object` — status de validade temporal dos domínios de `grounding_domains.yaml` (`ACTIVE` vs `STALE`).
  - `session_context`: `object` (`p0`, `active_feature`, `user_input`, `handoff`, `agents_queue`).
  - `env_summary`: `object` — resultado de `scan_environment.py` (`status: "HEALTHY" | "OK"`).
  - `context_decisions`: `DecisionEntry[]` — 100% das decisões históricas (sem limite `n=5`).
  - `context_learnings`: `LearningEntry[]` — 100% dos aprendizados históricos (sem limite `n=5`).
  - `estimated_tokens`: `integer`.
  - `token_budget`: `integer` (`0` — indicando ausência de poda em 100% dos workflows).

---

### Entity: `GuardianProfile` (`source/profiles/gp_*.yaml`)
- **Localização:** `${VITALIA_KIT_DIR}/profiles/gp_<workflow>.yaml` (14 arquivos cobrindo os 16 workflows).
- **Campos:**
  - `schema_type`: `"guardian_profile"`.
  - `schema_version`: `"0.0.1"`.
  - `workflow`: `string`.
  - `hardware_profile`: `"frontier"`.
  - `tokens`: `object` (`total_budget: 0`, `source_weights: object`).
  - `constitution`: `object` (`no_prune: true`, `domains: []`, `severity_filter: ["BLOCKING", "WARNING", "INFO"]`, `principles_include: []`).
  - `phase_guardrails`: `object` (`phase: string`, `role: string`, `mandatory_checks: string[]` ou `mandatory_fmea_questions: string[]`).
  - `phase_profiles`: `object` (opcional, usado em `gp_sdd-judge.yaml`).
  - `session_context`: `object` (`include_p0: boolean`, `include_active_feature: boolean`, `include_agents_queue: boolean`, `include_user_input: boolean`).

---

### Entity: `HandoffEnvelope`
- **Localização:** `<project_root>/.vitalia/memory/data_storage/handoffs/handoff_<source>_to_<target>_<uuid8>.json`
- **Campos:**
  - `id`: `string` — hash curto de 8 caracteres.
  - `schema_version`: `"1.0"`.
  - `timestamp`: `string` — `DD-MM-YYYY HH:MM:SS(GMT-04:00)`.
  - `machine_id`: `string` — SHA256[:8] da máquina hospedeira.
  - `source_workflow`: `string`.
  - `target_workflow`: `string`.
  - `intent_type`: `enum` (`brainstorming_to_route`, `route_to_brainstorming`, `route_dispatch`, `brainstorming_delegate`, `subagent_response`, `sdd_pipeline_advance`, `session_action`).
  - `status`: `enum` (`pending`, `consumed`, `expired`, `failed`).
  - `consumed_at`: `string` (opcional).
  - `payload`: `object` (`summary: string`, `artifacts_paths: string[]`, `context_notes: string`).
- **Ciclo de Vida:** Criado com `status: "pending"` via `vitalia_handoff.py create`; injetado automaticamente em `session_context.handoff` quando o workflow de destino é invocado; marcado como `status: "consumed"` atomicamente via `vitalia_handoff.py consume`.

---

### Entity: `MachineShard`
- **Localização:** `<project_root>/.vitalia/memory/session/shards/<machine_id>.yaml`
- **Campos:**
  - `machine_id`: `string` — SHA256[:8] derivado de `VITALIA_MACHINE_NAME` ou `socket.gethostname()`.
  - `hostname`: `string` — nome legível da estação (ex: `srv_master`, `ai-control`, `andrenote`).
  - `last_sync`: `string` — `DD-MM-YYYY HH:MM:SS(GMT-04:00)` (chave primária de ordenação decrescente em `ShardManager.load_all_shards()`).
  - `active_branch`: `string`.
  - `active_feature`: `string`.
  - `p0`: `string` — próximo passo prioritário.
  - `pending_tasks`: `string[]`.
  - `recent_commits`: `string[]`.
  - `session_summary`: `string`.

---

### Entities: `DecisionEntry`, `LearningEntry`, `SessionHistoryEntry`
- **Localização:** `<project_root>/.vitalia/memory/session/data/{decisions,learnings,session_history}.jsonl`
- **Campos Comuns:**
  - `id`: `string` (8 hex chars).
  - `timestamp`: `string` (`DD-MM-YYYY HH:MM:SS(GMT-04:00)`).
  - `machine_id`: `string` (8 hex chars).
- **Campos de `DecisionEntry`:** `category` (`string`), `decision` (`string`), `rationale` (`string`), `alternatives` (`string[]`).
- **Campos de `LearningEntry`:** `source_origin` (`string`), `category` (`string`), `learning` (`string`), `rationale` (`string`), `trigger_event` (`string`).
- **Campos de `SessionHistoryEntry`:** `hostname` (`string`), `feature` (`string`), `summary` (`string`), `p0_next` (`string`), `commits` (`string[]`).
- **Invariante (Regra da Cerca Elétrica):** Mutados exclusivamente por `vitalia_context_engine.py` em cronologia reversa na renderização das visões Markdown.

