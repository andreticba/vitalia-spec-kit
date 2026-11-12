<!-- constitutional-status: APPROVED | auditor: red-team-vitalia | timestamp: 2026-11-11T21:56:00-04:00 | report: Relatório de inspeção.md -->
<!-- tasks.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:55(GMT-04:00) -->
> **tasks.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:55(GMT-04:00)**

# Tasks: Spec 006 — Sandbox Elevation, Minimalist AGENTS.md, Variable Purge & Dynamic Constitution

- **Spec:** [`specs/006-sandbox-elevation-and-dynamic-constitution/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/006-sandbox-elevation-and-dynamic-constitution/spec.md)
- **Plan:** [`specs/006-sandbox-elevation-and-dynamic-constitution/plan.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/006-sandbox-elevation-and-dynamic-constitution/plan.md)
- **Gerado em:** 11-11-2026 21:55(GMT-04:00)

---

## MVP Scope

> O MVP consiste na implementação das **Fases 0, 1, 2 e 3 (US1)**:
> 1. Verificações de ambiente e testes Red-First das invariantes de sandbox e preservação.
> 2. Elevação proativa de sandbox no `SKILL.md.template` e nas skills geradas (`BypassSandbox: true` inicial).
> 3. Manifesto `AGENTS.md` minimalista agnóstico (~35 linhas) com Topologia Real de 3 Camadas.
> 4. Deduplicação e idempotência estrita de preservação em `agent_preserver.sh` (FR-002.5).
> As fases subsequentes (Purga de variável do `.env`, Saneamento dos 26 pontos e Padrão Afirmativo) expandem a robustez e a integridade da governança.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e runtime isolado antes da execução.*

- [X] T000-A Verificar interpretador Python do kit: `/home/andre/.vitalia-spec-kit/.venv/bin/python3 --version`
- [X] T000-B Verificar integridade dos pacotes do kit (`pyyaml`, `jinja2`, `jsonschema`): `/home/andre/.vitalia-spec-kit/.venv/bin/python3 -m pip check`
- [X] T000-C Validar fontes de Grounding em `specs/006-sandbox-elevation-and-dynamic-constitution/research.md` (HTTP 200 comprovado)

---

## Phase 1: Setup & Red-First Test Harness (P05)

*Construção prévia de testes de caracterização e falsificação antes de alterar código.*

- [X] T001 [P] [TEST:BUGFIX] Implementar teste em `tests/test_skills_pure.py` verificando a presença mandatória da diretiva `BypassSandbox: true` no Passo 1 de `SKILL.md.template` e nas skills compiladas — Cenário de Falsificação: falha se o Passo 1 do template ou de qualquer skill omitir a cláusula explícita de elevação de sandbox.
- [X] T002 [P] [TEST:BUGFIX] Implementar teste em `tests/test_agent_preserver.py` reproduzindo a duplicação de blocos em `update_agents_md` — Cenário de Falsificação: falha se invocar a atualização de AGENTS.md sobre um arquivo com blocos repetidos ou sem marcador inicial não resultar em exatamente 1 único bloco delimitado por `START_MARKER` e `END_MARKER`.
- [X] T003 [P] [TEST:MIGRATION] Implementar teste em `tests/test_env_bootstrap.py` validando auto-descoberta do kit sem variável no `.env` — Cenário de Falsificação: falha se `resolve_kit_dir()` e `resolve_project_root()` não localizarem os diretórios corretos quando a chave `VITALIA_KIT_DIR` estiver ausente do `.env`.

---

## Phase 2: Foundational — Idempotência e Template de Elevação

*Ajustes estruturais nas ferramentas de preservação e geração de skills.*

- [X] T004 Atualizar `source/integrations/antigravity/SKILL.md.template` prescrevendo no Passo 1 a execução com elevação de sandbox mandatória e inicial (`BypassSandbox: true`) conforme FR-001.1.
- [X] T005 Atualizar `source/bin/lib/skill_generator.sh` para injetar a prescrição de elevação no Passo 1 de todas as skills geradas conforme FR-001.2.
- [X] T006 Corrigir o algoritmo de substituição em `source/bin/lib/agent_preserver.sh` para sanitizar e deduplicar blocos orfãos/repetidos de marcadores antes de gravar, garantindo idempotência estrita conforme FR-002.5.

---

## Phase 3: User Story 1 — Elevação de Sandbox e AGENTS.md Minimalista Agnóstico

**Story Goal**: Eliminar o erro de cold-start 127 na IDE Antigravity e fornecer um manifesto de agentes minimalista (~35 linhas) agnóstico de domínio com Topologia Real de 3 Camadas.  
**Independent Test**: Invocar `/vitalia-session-start` em um terminal limpo e validar execução imediata no turno 1 com código 0 e inspecionar `.agents/AGENTS.md` com exatamente 1 bloco de ~35 linhas.  
**Referência**: FR-001, FR-002, FR-002.5

- [X] T007 [P] [US1] Redigir o novo `source/AGENTS.md` minimalista (~35 linhas), declarando a Topologia Real de 3 Camadas do cliente (`<project_root>/`, `<kit_dir>/`, `<project_root>/.vitalia/`), delegando TDD à Constituição e sem âncoras semânticas negativas (`sdd_judge.py`, `kit-bootstrap.sh`).
- [X] T008 [US1] Sincronizar o arquivo `.agents/AGENTS.md` na raiz do workspace com o novo conteúdo minimalista deduplicado.
- [X] T009 [US1] Executar `tests/test_agent_preserver.py` comprovando transição Red ➔ Green para a idempotência de preservação.

---

## Phase 4: User Story 2 — Purga de VITALIA_KIT_DIR do .env do Cliente

**Story Goal**: Manter o `.env` do projeto cliente 100% limpo de caminhos absolutos locais do kit, confiando na auto-descoberta intrínseca.  
**Independent Test**: Executar `install-project` em pasta temporária e asserir que o `.env` resultante não contém a chave `VITALIA_KIT_DIR`.  
**Referência**: FR-003

- [X] T010 [US2] Modificar `source/bin/lib/env_manager.sh` para expurgar a linha que injeta `VITALIA_KIT_DIR` no `.env` do projeto cliente durante a instalação ou atualização.
- [X] T011 [US2] Revisar `source/src/kit_env_bootstrap.py` garantindo que `resolve_kit_dir()` resolva deterministicamente via parent path sem emitir avisos na ausência da variável no `.env`.
- [X] T012 [US2] Executar `tests/test_env_bootstrap.py` comprovando transição Red ➔ Green para auto-localização limpa.

---

## Phase 5: User Story 3 — Saneamento Dinâmico de Números Mágicos (FR-006)

**Story Goal**: Erradicar faixas e contadores fixos (`P00–P17`, `16 workflows`, etc.) nos 26 pontos mapeados do sistema, tornando a governança dinamicamente extensível.  
**Independent Test**: Adicionar um princípio mock a `constitution.yaml` em teste e comprovar que nenhuma suíte quebra por contagem estática.  
**Referência**: FR-004

- [X] T013 [P] [US3] [TEST:REFACTOR] Implementar teste em `tests/test_dynamic_governance.py` validando que a contagem de princípios e workflows deriva dinamicamente do tamanho das estruturas — Cenário de Falsificação: falha se qualquer asserção no sistema esperar contagem estática de 18 princípios ou 16 workflows.
- [X] T014 [P] [US3] Saneamento dos pontos de governança e perfis em `source/profiles/constitution.yaml`, `source/profiles/gp_*.yaml` e `source/profiles/agents_catalog.yaml`.
- [X] T015 [P] [US3] Saneamento dos 16 arquivos `.toml` em `source/extensions/*.toml`.
- [X] T016 [US3] Saneamento dos scripts Python internos (`source/src/core/guardian_context.py`, `source/src/hooks/scan_environment.py` e renderizadores de contexto).
- [X] T017 [US3] Saneamento das suítes de teste em `tests/` substituindo asserções estáticas por contagens dinâmicas.

---

## Phase 6: User Story 4 — Adoção Integral do Padrão Afirmativo e Barreira Síncrona

**Story Goal**: Converter todas as diretrizes negativas proibitivas em prescrições afirmativas da forma desejada e blindar a barreira síncrona de Grounding P03.  
**Independent Test**: Varredura semântica confirmando ausência de formulações proibitivas negativas e execução de teste validando que citações externas exigem confirmação HTTP 200.  
**Referência**: FR-005, FR-006

- [X] T018 [P] [US4] Reformular as diretrizes em `source/profiles/constitution.yaml` e `source/profiles/gp_*.yaml` no padrão afirmativo canônico (*"Describe the shape you want, not the hole"*).
- [X] T019 [P] [US4] Padronizar o Princípio P03 com a fórmula oficial: *"Toda citação de versão, documentação, endpoint ou alegação científica exige confirmação de link ativo (HTTP 200) seguida de leitura integral da fonte."*
- [X] T020 [US4] Atualizar `source/extensions/research.toml` e `source/extensions/spec-specify.toml` formalizando a barreira síncrona obrigatória de orquestração.

---

## Phase 7: Polish, Regeneração de Skills e Validação Final

*Compilação dos artefatos em Camada 2, sincronização e validação de regressão.*

- [X] T021 Regenerar todas as 16 skills em `.agents/skills/*/SKILL.md` via `source/bin/lib/skill_generator.sh` garantindo Passo 1 com `BypassSandbox: true` e pureza total.
- [X] T022 Executar suíte completa de testes (`/home/andre/.vitalia-spec-kit/.venv/bin/pytest tests/`) comprovando 100% de aprovação verde.
- [X] T023 Disparar sub-agente auditor `/vitalia-judge --mode=converge` e compilar o Relatório de Inspeção final.

---

## Dependency Graph

```
Phase 0 (Grounding) 
       │
       ▼
Phase 1 (Red-First Tests: T001, T002, T003)
       │
       ▼
Phase 2 (Foundational: T004, T005, T006)
       │
       ▼
Phase 3 (US1 — Sandbox & AGENTS.md: T007, T008, T009)
       │
       ▼
Phase 4 (US2 — Purga .env: T010, T011, T012)
       │
       ▼
Phase 5 (US3 — Saneamento 26 Pontos: T013, T014, T015, T016, T017)
       │
       ▼
Phase 6 (US4 — Padrão Afirmativo & Grounding: T018, T019, T020)
       │
       ▼
Phase 7 (Polish & Dogfooding: T021, T022, T023)
```

---

## Parallel Execution

As seguintes tarefas dentro de suas respectivas fases são independentes e paralelizáveis:
- **Phase 1:** T001, T002 e T003 podem ser criados em paralelo.
- **Phase 3:** T007 pode ser redigido em paralelo com a revisão das skills.
- **Phase 5:** T014, T015 e T016 operam sobre arquivos distintos e podem ser executadas em paralelo.
- **Phase 6:** T018 e T019 podem ser refinados em paralelo.
