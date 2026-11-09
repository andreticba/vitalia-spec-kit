<!-- Relatório de inspeção.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:34(GMT-04:00) -->
> **Relatório de inspeção.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:34(GMT-04:00)**

# 🛡️ Relatório de Inspeção Constitucional de Tarefas — Red Team Vitalia (`/vitalia-task-verifier`)

- **Sub-Agente:** Auditor Adversarial Red Team Constitucional (`/vitalia-task-verifier`)
- **Artefato Auditado:** [`specs/002-universal-bootstrap-runtime/tasks.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/tasks.md)
- **Artefatos de Confronto:**
  - [`specs/002-universal-bootstrap-runtime/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/spec.md)
  - [`specs/002-universal-bootstrap-runtime/plan.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/plan.md)
  - [`.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md)
  - [`specs/002-universal-bootstrap-runtime/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research-brainstorming.md)

---

## 1. Resumo Executivo

| Métrica | Quantidade |
|---|---|
| **Total de Tarefas Auditadas** | `38` (`T000-A` a `T000-E` + `T001` a `T033`) |
| **Tarefas de Teste Auditadas (Gatekeeper P05)** | `9` (`T011`, `T012`, `T014`, `T015`, `T020`, `T021`, `T025`, `T026`, `T030`) |
| **Tarefas CONFORMES (`PASS`)** | `38 / 38` (`100%`) |
| **Alertas (`WARN`)** | `0` |
| **Violações Críticas (`BLOCK`)** | `0` |

### Verificação dos 4 Gates Bloqueantes do Red Team Gatekeeper (`gp_task-verifier.yaml`)
1. **Modalidade P05 e Cenário de Falsificação Explícito:** `9/9` tarefas de teste declaram sua modalidade (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:MIGRATION]`) e descrevem o Cenário de Falsificação comportamental que fará o teste falhar.
2. **Veto a Testes Sintáticos Rasos (`is_file()`):** `0` tarefas baseadas em presença estática de arquivo; 100% exercitam subprocessos reais (`kit-bootstrap.sh`, `install-project`, `git_storage_manager.sh`, `scan_environment.py`, `vitalia_hook_runner.py` nos 16 workflows, `vitalia_context_engine.py`, `vitalia_handoff.py`).
3. **Correspondência 1-a-1 com a Matriz de Migração (`AC-PLAN-03`) e TDA (`TDA-01` a `TDA-08`):**
   - `TDA-01` $\rightarrow$ `T011` (`[TEST:NEW]`)
   - `TDA-02` $\rightarrow$ `T012` (`[TEST:BUGFIX]` — `RCA-02`)
   - `TDA-03` $\rightarrow$ `T014` (`[TEST:BUGFIX]` — `RCA-04a`)
   - `TDA-04` $\rightarrow$ `T015` (`[TEST:MIGRATION]` — `RCA-04b`)
   - `TDA-05` $\rightarrow$ `T020` (`[TEST:BUGFIX]` — `Pivô 1`)
   - `TDA-06` $\rightarrow$ `T021` (`[TEST:MIGRATION]` — 16 workflows 100% sem poda + Context Lifting isolado)
   - `TDA-07` $\rightarrow$ `T025` (`[TEST:BUGFIX]`) + `T026` (`[TEST:MIGRATION]` — `RCA-05` + Bug `shards[0]`)
   - `TDA-08` $\rightarrow$ `T030` (`[TEST:MIGRATION]` — handoff + OpenAPI 3.0 + `--help` P10)
4. **Precedência TDD / Bug Reproduction First:** Todas as tarefas de teste (`T011`–`T012`, `T014`–`T015`, `T020`–`T021`, `T025`–`T026`, `T030`) precedem imediatamente suas respectivas tarefas de implementação dentro de cada fase.

---

## 2. Matriz de Conformidade Tarefa por Tarefa (`T000-A` a `T033`)

| ID | Fase | US | Princípios Avaliados | Parecer | Diagnóstico Técnico e Evidência |
|---|---|---|---|---|---|
| `T000-A` | Phase 0 | — | P03, P11 | `CONFORME` | Verifica o interpretador Python sem criar `~/.vitalia-spec-kit` nem tocar em `~/.vitalia`. |
| `T000-B` | Phase 0 | — | P03, P11 | `CONFORME` | Valida disponibilidade de `python3 -m venv` e `git` para subprocessos de teste em `tmp_path`. |
| `T000-C` | Phase 0 | — | P03, P11 | `CONFORME` | Audita pacotes instalados (`PyYAML`, `Jinja2`, `jsonschema`, `pytest`) contra `requirements.txt`. |
| `T000-D` | Phase 0 | — | P03, P04 | `CONFORME` | Confirma vigência temporal (`valid_until`) das fontes verificadas em `research.md`. |
| `T000-E` | Phase 0 | — | P03, P11 | `CONFORME` | Executa `pip check` garantindo integridade do ambiente de testes. |
| `T001` | Phase 1 | — | P04, P11 | `CONFORME` | Caminho explícito (`requirements.txt`), cabeçalho P04 `Vitalia SPEC Kit v0.0.1` e dependências enxutas sem Redis. |
| `T002` | Phase 1 | — | P00, P04, P08 | `CONFORME` | Cria `source/AGENTS.md` e `source/integrations/antigravity/SKILL.md.template` com `Vitalia SPEC Kit v0.0.1` e política de Zero Poda. |
| `T003` | Phase 1 | — | P11, P12 | `CONFORME` | Cria/atualiza todos os 9 `.schema.json` em `source/src/schemas/` no dialeto OpenAPI 3.0 limpo (zero `$schema`, `title` raiz ou `additionalProperties: false`). |
| `T004` | Phase 1 | — | P01, P11 | `CONFORME` | Remove artefatos legados obsoletos (`sdd_judge.py`, `telemetry_worker.py`, `redis_detector.sh`) de `source/`. |
| `T005` | Phase 2 | — | P04, P05 | `CONFORME` | Atualiza `source/profiles/constitution.yaml` com `P04` padronizado em `Vitalia SPEC Kit v0.0.1` e `P05` Matriz de 4 Modalidades. |
| `T006` | Phase 2 | — | P03, P04, P09 | `CONFORME` | Consolida `source/profiles/grounding_domains.yaml` com os 10 domínios canônicos e validade temporal. |
| `T007` | Phase 2 | — | P03, P08, P09 | `CONFORME` | Consolida `source/profiles/dynamic_questioning.yaml` (9 domínios) e `source/profiles/brainstorming_intents.yaml` (7 domínios). |
| `T008` | Phase 2 | — | P08, P12 | `CONFORME` | Sincroniza `source/profiles/agents_catalog.yaml` e `source/profiles/routing_table.yaml` com os 16 workflows. |
| `T009` | Phase 2 | — | P01, P05, P11 | `CONFORME` | Consolida as **14 lentes `source/profiles/gp_*.yaml`** (incluindo `gp_session-start`, `gp_session-end` e `gp_session-consolidate`) com `no_prune: true` e `total_budget: 0`. |
| `T010` | Phase 2 | — | P01, P08, P11 | `CONFORME` | Consolida os **16 workflows `source/extensions/*.toml`** 100% sem poda, `preferred = "filesystem"`, `version = "0.0.1"` e `{{VITALIA_KIT_DIR}}`. |
| `T011` | Phase 3 | `US1` | P05 (`[TEST:NEW]`), P11 | `CONFORME` | Corresponde a `TDA-01`. Cenário de Falsificação executável testando `kit-bootstrap.sh`, `.venv`, 16 `.toml`, 14 `gp_*.yaml` e shim `vitalia-install-project`. |
| `T012` | Phase 3 | `US1` | P05 (`[TEST:BUGFIX]`) | `CONFORME` | Corresponde a `TDA-02` (`RCA-02`). Reproduz falha de `python3 -m venv` via wrapper no `PATH` e exige aborto antes de criar pastas parciais. |
| `T013` | Phase 3 | `US1` | P04, P10, P11 | `CONFORME` | Implementa `kit-bootstrap.sh` após `T011` e `T012`, respeitando `WSL2/zsh` e default `~/.vitalia-spec-kit`. |
| `T014` | Phase 4 | `US2` | P05 (`[TEST:BUGFIX]`), P16 | `CONFORME` | Corresponde a `TDA-03` (`RCA-04a`). Cenário de Falsificação exige `0` arquivos ocultos/`.trash` em `.agents/skills/` após reinstalação. |
| `T015` | Phase 4 | `US2` | P05 (`[TEST:MIGRATION]`) | `CONFORME` | Corresponde a `TDA-04` (`RCA-04b`). Cenário de Falsificação valida `git clone --depth=1` contra repositório Git bare real e fallback `git init`. |
| `T016` | Phase 4 | `US2` | P06, P15 | `CONFORME` | Implementa `source/bin/lib/logger.sh` e `source/bin/lib/env_manager.sh` sem colisão de `stderr` em subshells. |
| `T017` | Phase 4 | `US2` | P07, P16 | `CONFORME` | Implementa `source/bin/lib/git_storage_manager.sh` preservando `git ls-remote` $\rightarrow$ `git clone --depth=1` e `git init -b main`. |
| `T018` | Phase 4 | `US2` | P16 | `CONFORME` | Implementa `source/bin/lib/agent_preserver.sh` e `source/bin/lib/skill_generator.sh` mantendo `.agents/skills/` 100% puro. |
| `T019` | Phase 4 | `US2` | P10, P11 | `CONFORME` | Implementa `source/bin/install-project` integrando as 5 bibliotecas modulares e `--help`. |
| `T020` | Phase 5 | `US3` | P05 (`[TEST:BUGFIX]`), P11 | `CONFORME` | Corresponde a `TDA-05`. Cenário de Falsificação exige status `HEALTHY`/`OK` sem Redis e precedência correta de `VITALIA_KIT_DIR`. |
| `T021` | Phase 5 | `US3` | P05 (`[TEST:MIGRATION]`), P07 | `CONFORME` | Corresponde a `TDA-06`. Cenário de Falsificação executa `vitalia_hook_runner.py` sobre **todos os 16 `.toml`** exigindo `18/18` princípios (`P00`–`P17`), `token_budget: 0`, zero warnings de `gp_*.yaml` e escrita em `data_storage/context/<machine_id>/`. |
| `T022` | Phase 5 | `US3` | P10, P11, P15 | `CONFORME` | Implementa `source/src/kit_env_bootstrap.py` e `source/src/hooks/scan_environment.py` sem probes de containers. |
| `T023` | Phase 5 | `US3` | P03, P07, P10 | `CONFORME` | Implementa `source/src/hooks/domain_detector.py` e `source/src/hooks/guardian_context.py` eliminando 100% dos algoritmos legados de poda. |
| `T024` | Phase 5 | `US3` | P07, P10, P11 | `CONFORME` | Implementa `source/src/vitalia_hook_runner.py` gravando em `.vitalia/memory/data_storage/context/<machine_id>/` sem `tmp_cleanup_matrix` e sem Redis. |
| `T025` | Phase 6 | `US4` | P05 (`[TEST:BUGFIX]`), P16 | `CONFORME` | Corresponde a `TDA-07` (`RCA-05`). Reproduz o bug de `shards[0]` com `17a6f667.yaml` (`03-11-2026`) vs `eb10269b.yaml` (`07-11-2026`). |
| `T026` | Phase 6 | `US4` | P04, P05 (`[TEST:MIGRATION]`), P16 | `CONFORME` | Corresponde a `TDA-07`. Valida o ciclo `init` $\rightarrow$ `end` $\rightarrow$ `consolidate`, timestamps `GMT-04:00` e renderização completa do `README.md` rico. |
| `T027` | Phase 6 | `US4` | P04, P14, P16 | `CONFORME` | Porta e corrige `source/src/core/{__init__,utils,shard_manager,context_engine}.py` com ordenação decrescente por `parse_sync_time(last_sync)`. |
| `T028` | Phase 6 | `US4` | P03, P04, P16 | `CONFORME` | Porta e atualiza `source/src/rendering/*` e `source/templates/dashboard_template.md` (`Vitalia SPEC Kit v0.0.1` + 10 domínios). |
| `T029` | Phase 6 | `US4` | P10, P14, P16 | `CONFORME` | Atualiza `source/src/vitalia_context_engine.py` com `--help` didático e integração modular completa. |
| `T030` | Phase 7 | `US5` | P05 (`[TEST:MIGRATION]`), P10, P11 | `CONFORME` | Corresponde a `TDA-08`. Valida ciclo `create` $\rightarrow$ `pending` $\rightarrow$ `consume` de handoff, pureza OpenAPI 3.0 de todos os schemas e `--help` em todos os CLIs. |
| `T031` | Phase 7 | `US5` | P04, P10, P11, P12 | `CONFORME` | Atualiza `source/src/vitalia_handoff.py` com `kit_env_bootstrap` e cabeçalho P04 `Vitalia SPEC Kit v0.0.1`. |
| `T032` | Phase 8 | — | P04, P11 | `CONFORME` | Auditoria transversal de cabeçalhos P04 `Vitalia SPEC Kit v0.0.1` e ausência de `~/.vitalia` hardcoded em `source/`. |
| `T033` | Phase 8 | — | P01, P05, P16 | `CONFORME` | Execução final de `pytest -v tests/` e verificação da Regra da Cerca Elétrica (`git status`). |

---

## 3. Refatorações Recomendadas

Nenhuma refatoração necessária (`0` violações `BLOCK`, `0` alertas `WARN`).

---

## 4. Parecer Conclusivo (Red Team Gatekeeper)

- **Status da Inspeção:** **`APROVADO PARA SELAGEM (AGUARDANDO HITL SOBERANO)`**
- O arquivo [`specs/002-universal-bootstrap-runtime/tasks.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/tasks.md) cumpre 100% dos requisitos da Matriz Bidimensional de Testes P05, do Test Depth Agreement (`TDA-01` a `TDA-08`) e da Matriz de Migração (`AC-PLAN-03`).

