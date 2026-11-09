<!-- tasks.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:35(GMT-04:00) -->
> **tasks.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:35(GMT-04:00)**
<!-- constitutional-status: APPROVED | auditor: red-team-vitalia | timestamp: 08-11-2026 19:35:00(GMT-04:00) | report: Relatório de inspeção.md -->

# Tasks: Universal Bootstrap, Runtime Autônomo em 4 Camadas & Blindagem SDD

**Spec**: [`specs/002-universal-bootstrap-runtime/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/spec.md) | **Plan**: [`specs/002-universal-bootstrap-runtime/plan.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/plan.md)  
**Fontes Canônicas**: [`.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md) | [`specs/002-universal-bootstrap-runtime/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research-brainstorming.md)  
**Gerado em**: 08-11-2026

---

## MVP Scope

> Implementar **Phase 0 + Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1) + Phase 4 (US2) + Phase 5 (US3) + Phase 6 (US4)** entrega o Vitalia SPEC Kit v0.0.1 completo, autônomo em 4 camadas, 100% sem poda nos 16 workflows e pronto para o teste E2E em `WSL2/zsh`.  
> **Phase 7 (US5)** e **Phase 8 (Polish & Cross-Cutting)** consolidam a blindagem final de contratos OpenAPI 3.0, handoffs e higiene P04/P10.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e dependências antes de qualquer implementação em `source/`. Sem label de US.*

- [X] T000-A Verificar interpretador Python do toolchain vigente (`/home/andre/.vitalia/.venv/bin/python3 --version` e `python3 --version`) garantindo compatibilidade Python 3.11+ sem tocar em `~/.vitalia` nem criar `~/.vitalia-spec-kit`
- [X] T000-B Verificar disponibilidade do módulo `venv` (`python3 -m venv --help`) e `git` (`git --version`) na máquina de desenvolvimento para execução de subprocessos isolados em `tmp_path`
- [X] T000-C Verificar pacotes instalados no ambiente de execução de testes (`PyYAML`, `Jinja2`, `jsonschema`, `pytest`) contra `requirements.txt`
- [X] T000-D Confirmar vigência temporal (`valid_until` > `08-11-2026`) das fontes de Grounding P03 verificadas em `specs/002-universal-bootstrap-runtime/research.md` (`venv`, `tomllib`, `git-clone`, `PyYAML`, `Jinja2`, `jsonschema`, `pytest`, `OpenAPI 3.0.3`)
- [X] T000-E Verificar ausência de conflitos de dependências via `pip check` no interpretador de testes

---

## Phase 1: Setup

*Estrutura base do repositório raiz (Camada 1), dependências, schemas OpenAPI 3.0 puros e contrato global `source/AGENTS.md`. Sem label de US.*

- [X] T001 Atualizar `requirements.txt` na raiz do repositório com as dependências estritas do kit isolado (`PyYAML>=6.0.1`, `Jinja2>=3.1.3`, `jsonschema>=4.21.1`, `pytest>=8.0.0`) e cabeçalho P04 `Vitalia SPEC Kit v0.0.1`
- [X] T002 [P] Criar/atualizar `source/AGENTS.md` e `source/integrations/antigravity/SKILL.md.template` estruturados por Primacy & Recency (`Vitalia SPEC Kit v0.0.1`), documentando a topologia de 4 camadas, a política de Zero Poda em 100% dos workflows, a Regra da Cerca Elétrica e o uso de `{{VITALIA_KIT_DIR}}`
- [X] T003 [P] Atualizar e criar os schemas JSON em `source/src/schemas/` (`constitution.schema.json`, `guardian_profile.schema.json`, `grounding_domains.schema.json`, `dynamic_questioning.schema.json`, `brainstorming_intents.schema.json`, `agents_catalog.schema.json`, `routing_table.schema.json`, `context-lifting-envelope.schema.json`, `vitalia-handoff-v1.0.0.json`) estritamente no dialeto OpenAPI 3.0 limpo (zero `$schema`, zero `title` raiz e zero `additionalProperties: false` — P11)
- [X] T004 Remover arquivos legados obsoletos de `source/src/` e `source/bin/lib/` (como `source/src/sdd_judge.py`, `source/src/telemetry_worker.py` ou `source/bin/lib/redis_detector.sh` caso existam) para garantir pureza da Camada 1

---

## Phase 2: Foundational — Catálogos YAML, 14 Lentes `gp_*.yaml` Sem Poda e 16 Workflows `.toml`

*Catálogos constitucionais, lentes de fase 100% sem poda e extensões `.toml` compartilhados por todas as User Stories. Sem label de US.*

- [X] T005 [P] Atualizar `source/profiles/constitution.yaml` com cabeçalho P04 `Vitalia SPEC Kit v0.0.1`, regra `P04` exigindo `Vitalia SPEC Kit v0.0.1` com `GMT-04:00` e regra `P05` instituindo a Matriz Bidimensional de 4 Modalidades (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`), Cenário de Falsificação obrigatório e veto `BLOCKING` a asserções sintáticas `is_file()`
- [X] T006 [P] Criar/atualizar `source/profiles/grounding_domains.yaml` com os 10 domínios canônicos (`provedores_de_ia`, `python_packages`, `web_technologies`, `external_apis`, `security_practices`, `regulations_compliance`, `cloud_services`, `scientific_claims`, `clinical_safety`, `software_architecture`) e metadados de validade temporal (`last_verified_at`, `valid_until`, `validity_window_days`, `status`, `last_update_source`, `update_history`)
- [X] T007 [P] Criar/atualizar `source/profiles/dynamic_questioning.yaml` (9 domínios socráticos livres de Redis/Celery/Ollama/VRAM e com metadados temporais) e `source/profiles/brainstorming_intents.yaml` (7 domínios semânticos estruturados)
- [X] T008 [P] Atualizar `source/profiles/agents_catalog.yaml` e `source/profiles/routing_table.yaml` sincronizados com os 16 workflows canônicos (incluindo `architect` e `research`) e mantendo os 5 especialistas verticais de domínio com `status: "planned"`
- [X] T009 Consolidar em `source/profiles/` todas as 14 lentes de fase sem poda (`gp_session-start.yaml`, `gp_session-end.yaml`, `gp_session-consolidate.yaml`, `gp_brainstorming.yaml`, `gp_vitalia-route.yaml`, `gp_architect.yaml`, `gp_research.yaml`, `gp_spec-specify.yaml`, `gp_spec-plan.yaml`, `gp_spec-tasks.yaml`, `gp_task-verifier.yaml`, `gp_analyze.yaml`, `gp_spec-implement.yaml`, `gp_sdd-judge.yaml`), garantindo que 100% declarem `no_prune: true`, `total_budget: 0`, `schema_version: "0.0.1"` e `hardware_profile: "frontier"`
- [X] T010 Consolidar em `source/extensions/` os 16 workflows canônicos (`session-start.toml`, `session-end.toml`, `session-consolidate.toml`, `brainstorming.toml`, `route.toml`, `architect.toml`, `research.toml`, `spec-specify.toml`, `clarify.toml`, `spec-plan.toml`, `spec-tasks.toml`, `task-verifier.toml`, `analyze.toml`, `spec-implement.toml`, `converge.toml`, `judge.toml`) com `version = "0.0.1"`, `hardware_profile = "frontier"`, `preferred = "filesystem"`, `{{VITALIA_KIT_DIR}}`, zero menção a `sdd_judge.py` e `guardian_profile` mapeado para as 14 lentes sem poda

---

## Phase 3: User Story 1 — Bootstrap Universal e Instalação em Máquina Limpa (`WSL2/zsh`) [Prioridade: P1]

**Story Goal**: Permitir que o desenvolvedor instale o kit completo em qualquer diretório escolhido (padrão `~/.vitalia-spec-kit`) com `.venv` isolado e pré-checagem de `python3 -m venv`.  
**Independent Test**: Executar `./kit-bootstrap.sh --target-dir <tmp_path>/kit --non-interactive` e validar importação de pacotes no `.venv` e presença funcional dos 16 workflows e 14 lentes.  
**Referência**: `FR-001`, `FR-002`, `RN-001`, `RN-002`, `TDA-01`, `TDA-02`

- [X] T011 [P] [US1] [TEST:NEW] Criar teste de bootstrap completo parametrizado em `tests/test_bootstrap_and_install.py` (`test_kit_bootstrap_clean_machine_e2e`) — Cenário de Falsificação: falha se `./kit-bootstrap.sh --target-dir <tmp_path>/kit --non-interactive` retornar código `!= 0`, se `<tmp_path>/kit/.venv/bin/python3 -c "import yaml, jinja2, jsonschema"` falhar, se faltar qualquer um dos 16 `.toml`, 14 `gp_*.yaml`, `templates/dashboard_template.md`, `SKILL.md.template`, `AGENTS.md`, ou se o shim `vitalia-install-project` não resolver `VITALIA_KIT_DIR`
- [X] T012 [P] [US1] [TEST:BUGFIX] Criar teste de reprodução de falha de `python3 -m venv` (`RCA-02`) em `tests/test_bootstrap_and_install.py` (`test_kit_bootstrap_aborts_cleanly_when_venv_missing`) — Cenário de Falsificação: falha se `./kit-bootstrap.sh` executado com um wrapper `python3` sem módulo `venv` retornar código `0`, criar diretórios parciais no `<target_dir>` ou omitir mensagem diagnóstica sobre `python3-venv` no `stderr`
- [X] T013 [US1] Implementar `kit-bootstrap.sh` na raiz do repositório com suporte a `--target-dir`, `--non-interactive`, `--help` e `VITALIA_KIT_DIR` (default `~/.vitalia-spec-kit`, expansão segura de `~` em `zsh`/`bash`), pré-validação de `python3 -m venv` antes de criar diretórios, cópia integral de `source/{bin,extensions,profiles,src,integrations,templates,AGENTS.md}`, criação de `.venv`, injeção idempotente em `.bashrc`/`.zshrc` e geração de `~/.local/bin/vitalia-install-project`

---

## Phase 4: User Story 2 — Pureza de `.agents/skills/` e Preservação de Clonagem Git Remota [Prioridade: P1]

**Story Goal**: Garantir que `install-project` mantenha `.agents/skills/` 100% puro para o indexador da Antigravity IDE e preserve `git clone --depth=1` quando houver URL remota (com fallback `git init` local quando vazio).  
**Independent Test**: Executar `install-project` contra um projeto com skills customizadas e um repositório Git bare local com commit prévio, verificando `0` arquivos ocultos em `.agents/skills/` e presença do commit clonado em `.vitalia/memory/session/`.  
**Referência**: `FR-003`, `PRES-02/BUG-02`, `PRES-03/BUG-03`, `TDA-03`, `TDA-04`

- [X] T014 [P] [US2] [TEST:BUGFIX] Criar teste de invariante de pureza de `.agents/skills/` (`RCA-04a`) em `tests/test_bootstrap_and_install.py` (`test_install_project_skills_directory_purity`) — Cenário de Falsificação: falha se após múltiplas execuções de `install-project` sobre projeto com skills pré-existentes existir qualquer arquivo ou diretório oculto (`.trash`, `.vitalia-manifest`) dentro de `.agents/skills/` ou se as 16 skills `vitalia-*/SKILL.md` não tiverem `{{VITALIA_KIT_DIR}}` resolvido
- [X] T015 [P] [US2] [TEST:MIGRATION] Criar teste de preservação de `git clone --depth=1` e fallback `git init` (`RCA-04b`) em `tests/test_bootstrap_and_install.py` (`test_git_storage_manager_remote_clone_and_local_init_fallback`) — Cenário de Falsificação: falha se `git_storage_manager.sh` não clonar o commit existente de um repositório Git bare remoto (`git clone --depth=1`), se falhar ao inicializar com `git init -b main` quando nenhuma URL remota for fornecida, ou se vazar `redis_detector.sh`
- [X] T016 [P] [US2] Implementar `source/bin/lib/logger.sh` e `source/bin/lib/env_manager.sh` compatíveis com POSIX/`zsh`/`bash` sem colisão de `stderr` em subshells e persistindo `VITALIA_KIT_DIR`, `SESSION_REPO` e `DATA_REPO` no `.env` do projeto hospedeiro
- [X] T017 [P] [US2] Implementar `source/bin/lib/git_storage_manager.sh` preservando `git ls-remote` $\rightarrow$ `git clone --depth=1` para repositórios remotos com histórico e fallback `git init -b main` para repositórios vazios ou sem URL remota
- [X] T018 [P] [US2] Implementar `source/bin/lib/agent_preserver.sh` e `source/bin/lib/skill_generator.sh` salvando manifestos e backups exclusivamente em `.vitalia/` (`.vitalia/.vitalia-manifest` e `.vitalia/backups/`) e gerando `.agents/AGENTS.md` + `.agents/skills/vitalia-*/SKILL.md` sem poluir `.agents/skills/`
- [X] T019 [US2] Implementar `source/bin/install-project` orquestrando `logger.sh`, `env_manager.sh`, `git_storage_manager.sh`, `agent_preserver.sh` e `skill_generator.sh` com suporte a `--session-repo`, `--data-repo`, `--non-interactive` e `--help` (sem `redis_detector.sh`)

---

## Phase 5: User Story 3 — Context Lifting Isolado e Governança 100% Sem Poda em Todos os Workflows [Prioridade: P1]

**Story Goal**: Garantir que todos os 16 workflows operem 100% sem poda de contexto (`18/18` princípios `P00`–`P17`, `token_budget: 0`), gravem envelopes exclusivamente em `.vitalia/memory/data_storage/context/<machine_id>/` e reportem saúde `HEALTHY`/`OK` sem Redis/Docker.  
**Independent Test**: Executar `vitalia_hook_runner.py` para todos os 16 arquivos `.toml` em projeto isolado sem Redis e inspecionar os 16 envelopes JSON gerados.  
**Referência**: `FR-004`, `FR-005`, `FR-008`, `PRES-05/BUG-05`, `TDA-05`, `TDA-06`

- [X] T020 [P] [US3] [TEST:BUGFIX] Criar teste de descoberta de ambiente e inspeção de saúde sem containers em `tests/test_runtime_and_guardian.py` (`test_scan_environment_and_kit_bootstrap_healthy_without_redis`) — Cenário de Falsificação: falha se `scan_environment.py` reportar `DEGRADED` na ausência de Redis (6379) ou `.venv` no projeto hospedeiro, ou se `kit_env_bootstrap.py` usar `~/.vitalia` em vez da precedência `VITALIA_KIT_DIR` $\rightarrow$ `.env` $\rightarrow$ `~/.vitalia-spec-kit`
- [X] T021 [P] [US3] [TEST:MIGRATION] Criar teste de Context Lifting e Zero Poda nos 16 workflows em `tests/test_runtime_and_guardian.py` (`test_all_16_workflows_execute_with_zero_pruning_and_isolated_context`) — Cenário de Falsificação: falha se qualquer um dos 16 workflows em `source/extensions/*.toml` retornar código `!= 0`, emitir erro de Redis ou warning de `gp_*.yaml` ausente, gravar arquivos em `tmp/`, injetar `tmp_cleanup_matrix`, ter `token_budget != 0` ou contiver menos de 18 princípios (`P00`–`P17`) em `guardian_json.sources.constitution.principles`
- [X] T022 [P] [US3] Implementar `source/src/kit_env_bootstrap.py` e `source/src/hooks/scan_environment.py` com resolução determinística de `VITALIA_KIT_DIR` (precedência: env var $\rightarrow$ `.env` $\rightarrow$ `~/.vitalia-spec-kit`), validação exclusiva de `.env`, `.agents/AGENTS.md`, pureza de `.agents/skills/` e `${VITALIA_KIT_DIR}/.venv/bin/python3`, e flag `--help`
- [X] T023 [P] [US3] Implementar `source/src/hooks/domain_detector.py` e `source/src/hooks/guardian_context.py` eliminando todos os algoritmos e adaptadores legados de poda, injetando incondicionalmente 100% de `constitution.yaml` (`P00`–`P17`), 100% de `yaml_sources`, 100% de `decisions.jsonl`/`learnings.jsonl`, `phase_guardrails`/`phase_profiles` e checagem temporal `valid_until` de `grounding_domains.yaml`, gravando em `.vitalia/memory/data_storage/context/<machine_id>/`
- [X] T024 [US3] Implementar `source/src/vitalia_hook_runner.py` integrando `kit_env_bootstrap`, `scan_environment` e `guardian_context`, gravando o envelope completo exclusivamente em `<project_root>/.vitalia/memory/data_storage/context/<machine_id>/<workflow>_<ts>_<hash>.json` (sem `tmp/`, sem `tmp_cleanup_matrix` e sem Redis) e emitindo o Stub JSON no `stdout`

---

## Phase 6: User Story 4 — Motor de Sessão 3-Tier Fiel com Destaque Cronológico Correto [Prioridade: P1]

**Story Goal**: Preservar a renderização rica do dashboard (`vitalia-spec-kit-context`) via `core/*`, `rendering/*` e `templates/dashboard_template.md`, corrigindo a ordenação de shards por `last_sync` decrescente para que `shards[0]` seja sempre a estação mais recente.  
**Independent Test**: Executar `vitalia_context_engine.py --action consolidate` sobre diretório contendo `17a6f667.yaml` (`03-11-2026`) e `eb10269b.yaml` (`07-11-2026`) e verificar que `eb10269b` (`srv_master`) é destacada como Estação Ativa em `SESSION_STATE.md` e `README.md`.  
**Referência**: `FR-006`, `PRES-04/BUG-04`, `TDA-07`

- [X] T025 [P] [US4] [TEST:BUGFIX] Criar teste de reprodução do bug de ordenação de `shards[0]` (`RCA-05`) em `tests/test_context_engine_3tier.py` (`test_shard_manager_orders_by_last_sync_descending`) — Cenário de Falsificação: falha se, dados `17a6f667.yaml` (`last_sync: "03-11-2026 05:47:37(GMT-04:00)"`) e `eb10269b.yaml` (`last_sync: "07-11-2026 21:38:04(GMT-04:00)"`), `ShardManager.load_all_shards()[0]` retornar `17a6f667` em vez de `eb10269b` ou destacar a máquina antiga em `SESSION_STATE.md` e `README.md`
- [X] T026 [P] [US4] [TEST:MIGRATION] Criar teste do ciclo completo `init` $\rightarrow$ `end` $\rightarrow$ `consolidate` e fidelidade do dashboard rico em `tests/test_context_engine_3tier.py` (`test_context_engine_full_cycle_and_rich_dashboard_rendering`) — Cenário de Falsificação: falha se `vitalia_context_engine.py` gerar qualquer timestamp ISO 8601 bruto fora do padrão `DD-MM-YYYY HH:MM:SS(GMT-04:00)`, se `README.md` omitir o grafo Mermaid com labels entre aspas duplas (P16), a tabela HTML de máquinas, a seção `🎯 Sessão Ativa em Destaque` ou os 10 domínios canônicos de `grounding_domains.yaml`
- [X] T027 [P] [US4] Portar e higienizar `source/src/core/__init__.py`, `source/src/core/utils.py`, `source/src/core/shard_manager.py` e `source/src/core/context_engine.py`, corrigindo `ShardManager.load_all_shards()` para ordenar por `parse_sync_time(shard.get("last_sync", ""))` decrescente, removendo acoplamento com Redis e padronizando cabeçalhos P04 em `Vitalia SPEC Kit v0.0.1`
- [X] T028 [P] [US4] Portar e atualizar `source/src/rendering/__init__.py`, `source/src/rendering/dashboard_renderer.py`, `source/src/rendering/view_renderer.py`, `source/src/rendering/grounding_renderer.py`, `source/src/rendering/constitution_renderer.py` e `source/templates/dashboard_template.md` para `Vitalia SPEC Kit v0.0.1` e os 10 domínios de `grounding_domains.yaml`
- [X] T029 [US4] Implementar/atualizar `source/src/vitalia_context_engine.py` integrando `core/context_engine.py`, `rendering/*` e `kit_env_bootstrap.py` com suporte completo a `--action init|end|consolidate`, `--decisions-json`, `--learnings-json` e `--help`

---

## Phase 7: User Story 5 — Handoff Determinístico e Suíte Comportamental de Contratos P05 [Prioridade: P2]

**Story Goal**: Garantir que `vitalia_handoff.py`, todos os schemas OpenAPI 3.0, os 6 catálogos YAML, as 14 lentes `gp_*.yaml` e os flags `--help` (P10) sejam validados comportamentalmente.  
**Independent Test**: Executar `pytest tests/test_contracts_and_handoff.py` exercitando `create` $\rightarrow$ `pending` $\rightarrow$ `consume` de handoffs, validação `jsonschema` OpenAPI 3.0 e invocação `--help` de todos os scripts CLI.  
**Referência**: `FR-007`, `FR-009`, `RN-003`, `RN-004`, `RN-005`, `TDA-08`

- [X] T030 [P] [US5] [TEST:MIGRATION] Criar testes comportamentais de handoff (`create` $\rightarrow$ `pending` $\rightarrow$ `consume` a partir de subdiretório), validação OpenAPI 3.0 de todos os schemas/catálogos e execução de `--help` (P10) em `tests/test_contracts_and_handoff.py` — Cenário de Falsificação: falha se `vitalia_handoff.py` não resolver a raiz do projeto hospedeiro, se qualquer `.schema.json` contiver `$schema`, `title` raiz ou `additionalProperties: false`, se algum catálogo YAML falhar na validação de schema ou se qualquer script em `source/src/` falhar ao receber `--help`
- [X] T031 [US5] Atualizar `source/src/vitalia_handoff.py` integrando `kit_env_bootstrap.py` (`VITALIA_KIT_DIR` / `~/.vitalia-spec-kit`), cabeçalho P04 `Vitalia SPEC Kit v0.0.1` e validação contra `source/src/schemas/vitalia-handoff-v1.0.0.json`

---

## Phase 8: Polish & Cross-Cutting

*Auditoria transversal de cabeçalhos P04 (`Vitalia SPEC Kit v0.0.1`), pureza Git e execução integral da suíte E2E. Sem label de US.*

- [X] T032 Auditar e padronizar o cabeçalho P04 (`Vitalia SPEC Kit v0.0.1` com `GMT-04:00`) em 100% dos arquivos de `source/`, `kit-bootstrap.sh`, `requirements.txt` e `tests/`, garantindo zero referências residuais a `Vitalia SDD v0.6.0` ou `~/.vitalia` hardcoded
- [X] T033 Executar a suíte completa `pytest -v tests/` validando os 6 Acceptance Scenarios da `spec.md` (`SC-001` a `SC-006`) e verificar com `git status` que `~/.vitalia-spec-kit` não foi criado na máquina local e que `.vitalia/memory/session/` permaneceu intocado (Regra da Cerca Elétrica)

---

## Dependency Graph

```text
Phase 0 (Grounding & Env)
  └──► Phase 1 (Setup: requirements.txt, AGENTS.md, OpenAPI 3.0 schemas)
         └──► Phase 2 (Foundational: 6 YAML catalogs, 14 no-prune gp_*.yaml, 16 .toml)
                ├──► Phase 3 (US1: kit-bootstrap.sh) ──► Phase 4 (US2: install-project & bin/lib/*)
                ├──► Phase 5 (US3: kit_env_bootstrap, scan_environment, guardian_context, vitalia_hook_runner)
                ├──► Phase 6 (US4: vitalia_context_engine, core/*, rendering/*, dashboard_template.md)
                └──► Phase 7 (US5: vitalia_handoff & contract suite)
                       └──► Phase 8 (Polish & Full E2E Verification)
```

## Parallel Execution

- **Na Phase 1:** `T002` e `T003` podem ser executadas em paralelo (`[P]`).
- **Na Phase 2:** `T005`, `T006`, `T007` e `T008` podem ser executadas em paralelo (`[P]`).
- **Entre Fases de User Stories (após Phase 2):** Os testes e implementações de **Phase 3/4 (`US1`/`US2` em `source/bin/`)**, **Phase 5 (`US3` em `source/src/hooks/`)**, **Phase 6 (`US4` em `source/src/core/` e `source/src/rendering/`)** e **Phase 7 (`US5` em `source/src/vitalia_handoff.py`)** atuam em arquivos distintos e possuem tarefas marcadas com `[P]`.

