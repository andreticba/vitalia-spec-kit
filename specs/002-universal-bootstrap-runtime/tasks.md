<!-- constitutional-status: APPROVED | auditor: red-team-vitalia | timestamp: 2026-11-04T20:29:20-04:00 | report: Relatório de inspeção.md -->
<!-- tasks.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:18(GMT-04:00) -->
> **tasks.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:18(GMT-04:00)**

# Tarefas de Implementação Técnica — Spec 002: Universal Bootstrap & Runtime

* **Spec:** [specs/002-universal-bootstrap-runtime/spec.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/spec.md)
* **Plan:** [specs/002-universal-bootstrap-runtime/plan.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/plan.md)
* **Pesquisa Técnica:** [specs/002-universal-bootstrap-runtime/research.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research.md)
* **Gerado em:** 04-11-2026 20:18(GMT-04:00)

---

## MVP Scope

> O MVP da Spec 002 compreende **Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2)**.  
> Concluir estas fases entrega o produto 100% autônomo, instalável de forma idempotente via `git clone`, com isolamento de dependências, Context Lifting seguro em disco local sem vazamento para `/tmp/` e sem poluir o Git do projeto hospedeiro. As fases subsequentes consolidam a governança dos 12 TOMLs e a erradicação universal de podas de contexto.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e pré-requisitos antes de qualquer escrita de código produtivo. Sem label de US.*

- [X] T000-A [P] Verificar versão do interpretador Python do sistema host (`python3 --version >= 3.10`)
- [X] T000-B [P] Validar sintaxe dos esquemas OpenAPI 3.0 puros em `specs/002-universal-bootstrap-runtime/contracts/`
- [X] T000-C [P] Verificar versões atuais dos pacotes PyPI fixados (`pyyaml`, `jinja2`, `click`) em `pypi.org`

---

## Phase 1: Setup & Bootstrap Universal

*Inicialização do instalador e isolamento de runtime. Sem label de US.*

- [X] T001 Criar arquivo de dependências mínimas do runtime em `requirements.txt`
- [X] T002 [P] Escrever testes unitários e de ambiente para a rotina de bootstrap em `tests/test_bootstrap.py`
- [X] T003 Implementar script instalador universal idempotente em `kit-bootstrap.sh`
- [X] T004 Configurar permissões de execução e geração idempotente de shims em `~/.local/bin/` via `kit-bootstrap.sh`

---

## Phase 2: Foundational — Desacoplamento de Infraestrutura

*Dependências estruturantes e transição para filesystem puro. Sem label de US.*

- [X] T005 [P] Criar testes de caracterização (Golden Master) para o diagnóstico em `tests/test_scan_environment.py`
- [X] T006 Refatorar `source/src/hooks/scan_environment.py` eliminando totalmente sondagens TCP nas portas 6379 e 5432
- [X] T007 [P] Criar testes de isolamento e direcionamento de Context Lifting em `tests/test_hook_runner.py`
- [X] T008 Refatorar `source/src/vitalia_hook_runner.py` para gravar o contexto em `.vitalia/memory/data_storage/context/` e purgar chamadas ao Redis

---

## Phase 3: User Story 1 — Instalação e Reinstalação Segura (Idempotência)

**Story Goal**: Garantir que o desenvolvedor possa instalar, atualizar ou reparar o kit repetidas vezes sem falhas de concorrência ou conflitos de arquivos.  
**Independent Test**: Execução repetida de `./kit-bootstrap.sh` em diretório existente retornando código 0 e shims íntegros.  
**Referência**: FR-001, FR-002, FR-003, SC-001

- [X] T009 [P] [US1] Escrever testes de idempotência para reexecução de bootstrap em `tests/test_bootstrap_idempotency.py`
- [X] T010 [US1] Implementar rotina de detecção de instalação existente e reparo não-destrutivo em `kit-bootstrap.sh`
- [X] T011 [P] [US1] Refatorar utilitário de setup no projeto do usuário em `source/bin/install-project`
- [X] T012 [US1] Adicionar verificação da integridade do interpretador Python isolado em `source/src/hooks/scan_environment.py`

---

## Phase 4: User Story 2 — Armazenamento Local de Contexto e Proteção Git

**Story Goal**: Assegurar que o Context Lifting resida no disco local do projeto (sem vazar para `/tmp/`) e seja rigorosamente ignorado pelo Git da aplicação hospedeira.  
**Independent Test**: Execução de hook runner seguida de `git status` comprovando zero arquivos untracked no repositório de código.  
**Referência**: FR-005, FR-006, SC-002, SC-003

- [X] T013 [P] [US2] Escrever testes de conformidade Git em `tests/test_git_isolation.py` verificando a regra de exclusão
- [X] T014 [US2] Garantir inclusão compulsória de regra `.vitalia/memory/` no `.gitignore` via `source/bin/install-project`
- [X] T015 [P] [US2] Implementar partição determinística por `machine_id` (SHA256 de hostname) em `source/src/vitalia_hook_runner.py`
- [X] T016 [US2] Refatorar `source/src/vitalia_context_engine.py` para consolidar shards a partir do filesystem local

---

## Phase 5: User Story 3 — Condução Arquitetural Estruturada & 12 TOMLs Canônicos

**Story Goal**: Estabelecer a governança dos 12 comandos SDD, formalizando o Vitalia Architect e saneando contratos de extensão.  
**Independent Test**: Validação sintática e contratual de todos os TOMLs e perfis sem avisos de fallback do Guardian.  
**Referência**: FR-008, FR-009, FR-010, SC-005

- [X] T017 [P] [US3] Atualizar `source/profiles/constitution.yaml` com o cabeçalho `Vitalia SPEC Kit v0.0.1` e fuso GMT-04:00
- [X] T018 [P] [US3] Atualizar `source/profiles/routing_table.yaml` com o comando `/vitalia-architect`
- [X] T019 [P] [US3] Atualizar `source/profiles/brainstorming_intents.yaml` com domínio `arquitetura_software`
- [X] T020 [US3] Criar extensão canônica `source/extensions/architect.toml` conforme o contrato AC-ARCH-01/05
- [X] T021 [P] [US3] Saneamento das 11 extensões em `source/extensions/*.toml` removendo `hardware_profile = "lightweight"` e Redis

---

## Phase 6: User Story 4 — Auditoria Adversarial Precoce & Erradicação de Podas

**Story Goal**: Assegurar que o Guardian injete a totalidade da memória organizacional sem cortes e que o SDD-Judge atue nativamente com Inverted CoT.  
**Independent Test**: Execução de `/vitalia-judge` auditando artefato sem truncamento de regras ou perda de contexto.  
**Referência**: FR-007, FR-011, FR-012, SC-004

- [X] T022 [P] [US4] Refatorar `source/src/core/guardian.py` para erradicar podas de tokens e filtros de severidade restritivos
- [X] T023 [P] [US4] Atualizar `source/profiles/gp_sdd-judge.yaml` garantindo ingestão integral da constituição
- [X] T024 [US4] Atualizar extensão `source/extensions/judge.toml` com protocolo Inverted CoT e ausência total de CLIs legados
- [X] T025 [P] [US4] Validar conformidade OpenAPI 3.0 pura dos schemas em `specs/002-universal-bootstrap-runtime/contracts/`

---

## Phase 7: Polish & Cross-Cutting

*Qualidade, testes finais, documentação anti-Lost in the Middle e espelhamento. Sem label de US.*

- [X] T026 [P] Atualizar `source/AGENTS.md` com a ordem de instruções anti-Lost in the Middle (Primacy/Recency)
- [X] T027 Executar a suite completa de testes automatizados via `pytest tests/`
- [X] T028 Executar a validação manual dos cenários documentados em `specs/002-universal-bootstrap-runtime/quickstart.md`
- [X] T029 Espelhar os componentes validados de `source/` para o kit global unificado `~/.vitalia-spec-kit/`

---

## Dependency Graph

```
Phase 0 (Grounding)
       │
       ▼
Phase 1 (Setup: Bootstrap & Venv)
       │
       ▼
Phase 2 (Foundational: Desacoplamento Filesystem)
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
Phase 3 (US1: Idempotência)       Phase 4 (US2: Context Vault & Git)
       │                                 │
       └────────────────┬────────────────┘
                        ▼
       Phase 5 (US3: 12 TOMLs & Architect)
                        │
                        ▼
       Phase 6 (US4: No-Pruning & SDD-Judge)
                        │
                        ▼
       Phase 7 (Polish & Dogfooding)
```

---

## Parallel Execution

As tarefas assinaladas com `[P]` operam sobre arquivos distintos e podem ser executadas em paralelo dentro da mesma fase:
* **Fase 0:** T000-A, T000-B e T000-C.
* **Fase 1:** T002 paralelizável com preparação de documentação.
* **Fase 2:** T005 e T007 (escrita de testes de caracterização em arquivos de teste separados).
* **Fase 3:** T009 e T011.
* **Fase 4:** T013 e T015.
* **Fase 5:** T017, T018, T019 e T021.
* **Fase 6:** T022, T023 e T025.
