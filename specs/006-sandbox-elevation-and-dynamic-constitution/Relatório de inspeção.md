<!-- Relatório de inspeção.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:56(GMT-04:00) -->
> **Relatório de inspeção.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:56(GMT-04:00)**

# Relatório de Inspeção Constitucional — `tasks.md`

- **Feature:** `specs/006-sandbox-elevation-and-dynamic-constitution`
- **Artefato Auditado:** [`tasks.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/006-sandbox-elevation-and-dynamic-constitution/tasks.md)
- **Auditor:** Red Team Constitucional Vitalia (`vitalia-task-verifier`)
- **Data da Auditoria:** 11-11-2026 21:56 (GMT-04:00)
- **Parecer Preliminar:** **APROVADO (PASS)**

---

## 1. Resumo Executivo

| Métrica | Valor | Observação |
| :--- | :---: | :--- |
| **Total de Tarefas Auditadas** | **24** | De T000-A a T023 |
| **Tarefas Conformes (`PASS`)** | **24** | 100% de conformidade com os princípios constitucionais |
| **Alertas (`WARN`)** | **0** | Nenhum desvio não-bloqueante identificado |
| **Violações Críticas (`BLOCK`)** | **0** | Nenhuma violação estrutural ou constitucional |
| **Cobertura de Falsificação (P05)** | **100%** | Todas as tarefas de teste possuem modalidade e cenário de falsificação |
| **Rastreabilidade de Requisitos** | **100%** | FR-001 a FR-006 mapeados em histórias de usuário claras |

---

## 2. Auditoria do Gatekeeper de Profundidade e Falsificação (P05)

O Gatekeeper Red Team avaliou os 4 requisitos bloqueantes da governança P05:

1. **Exigência de Modalidade e Cenário de Falsificação (P05):**
   - **T001 [P] [TEST:BUGFIX]**: Modalidade declarada. Cenário de Falsificação: *falha se o Passo 1 do template ou de qualquer skill omitir a cláusula explícita de elevação de sandbox.* (`CONFORME`)
   - **T002 [P] [TEST:BUGFIX]**: Modalidade declarada. Cenário de Falsificação: *falha se invocar a atualização de AGENTS.md sobre um arquivo com blocos repetidos ou sem marcador inicial não resultar em exatamente 1 único bloco delimitado por `START_MARKER` e `END_MARKER`.* (`CONFORME`)
   - **T003 [P] [TEST:MIGRATION]**: Modalidade declarada. Cenário de Falsificação: *falha se `resolve_kit_dir()` e `resolve_project_root()` não localizarem os diretórios corretos quando a chave `VITALIA_KIT_DIR` estiver ausente do `.env`.* (`CONFORME`)
   - **T013 [P] [TEST:REFACTOR]**: Modalidade declarada. Cenário de Falsificação: *falha se qualquer asserção no sistema esperar contagem estática de 18 princípios ou 16 workflows.* (`CONFORME`)

2. **Veto Absoluto a Testes Rasos / Sintáticos:**
   - Nenhum teste baseia-se unicamente em `is_file()` ou existência de arquivos. Todos avaliam a semântica, parsing estruturado ou retorno comportamental. (`CONFORME`)

3. **Verificação da Matriz de Migração e TDA do `plan.md`:**
   - T003 e T013 cobrem formalmente a migração do `.env` e a substituição das contagens estáticas nos 26 pontos de código. (`CONFORME`)

4. **Precedência em Correções de Bugs (`[TEST:BUGFIX]`):**
   - T001 e T002 precedem a modificação de `SKILL.md.template`, `skill_generator.sh` e `agent_preserver.sh`. (`CONFORME`)

---

## 3. Matriz de Conformidade Tarefa por Tarefa

| ID | Fase / US | Descrição Resumida | Princípios Auditados | Parecer | Diagnóstico |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **T000-A** | Phase 0 | Verificar Python isolado do kit | P11 | **PASS** | Pré-condição de runtime isolado (Camada 2). |
| **T000-B** | Phase 0 | Checar integridade pip do kit | P11, P16 | **PASS** | Garante pacotes fundamentais (`pyyaml`, `jinja2`). |
| **T000-C** | Phase 0 | Validar Grounding HTTP 200 | P03 | **PASS** | Grounding documental e empírico comprovado. |
| **T001** | Phase 1 | [TEST:BUGFIX] Teste de elevação em skills | P01, P05, P11 | **PASS** | Red-first test para elevação proativa de sandbox. |
| **T002** | Phase 1 | [TEST:BUGFIX] Teste de idempotência em AGENTS.md | P01, P05, P16 | **PASS** | Reproduz defeito de duplicação (FR-002.5). |
| **T003** | Phase 1 | [TEST:MIGRATION] Teste de auto-descoberta sem .env | P01, P05, P11 | **PASS** | Valida desacoplamento de caminhos no cliente. |
| **T004** | Phase 2 | Atualizar `SKILL.md.template` (`BypassSandbox: true`) | P01, P11 | **PASS** | Alinha template nativo ao padrão de elevação inicial. |
| **T005** | Phase 2 | Atualizar `skill_generator.sh` | P01, P11 | **PASS** | Propaga prescrição de elevação a todas as skills. |
| **T006** | Phase 2 | Corrigir idempotência em `agent_preserver.sh` | P01, P16 | **PASS** | Implementa sanitização deduplicadora de blocos. |
| **T007** | Phase 3 (US1) | Redigir novo `source/AGENTS.md` minimalista (~35 linhas) | P01, P02, P11 | **PASS** | Topologia Real de 3 Camadas e Padrão Afirmativo. |
| **T008** | Phase 3 (US1) | Sincronizar `.agents/AGENTS.md` | P01, P02 | **PASS** | Aplica o manifesto minimalista na raiz do projeto. |
| **T009** | Phase 3 (US1) | Validar Red ➔ Green de `test_agent_preserver.py` | P05 | **PASS** | Comprova eficácia da correção de duplicação. |
| **T010** | Phase 4 (US2) | Purgar `VITALIA_KIT_DIR` em `env_manager.sh` | P11 | **PASS** | Remove contaminação de caminhos locais do kit. |
| **T011** | Phase 4 (US2) | Ajustar `kit_env_bootstrap.py` para auto-descoberta | P11, P16 | **PASS** | Resolução hierárquica determinística por parent path. |
| **T012** | Phase 4 (US2) | Validar Red ➔ Green de `test_env_bootstrap.py` | P05 | **PASS** | Comprova independência do `.env` cliente. |
| **T013** | Phase 5 (US3) | [TEST:REFACTOR] Teste de governança dinâmica | P01, P05 | **PASS** | Blinda extensibilidade contra números mágicos. |
| **T014** | Phase 5 (US3) | Saneamento em `constitution.yaml` e catálogos | P01, P02 | **PASS** | Remove menções estáticas a 18 princípios. |
| **T015** | Phase 5 (US3) | Saneamento dos 16 `.toml` em `extensions/` | P01, P02 | **PASS** | Remove menções fixas a catálogos sem poda. |
| **T016** | Phase 5 (US3) | Saneamento em `guardian_context.py` e scripts | P01, P11 | **PASS** | Torna dinâmico o cálculo de contexto do Guardian. |
| **T017** | Phase 5 (US3) | Saneamento de asserções estáticas em `tests/` | P05 | **PASS** | Adequa testes para contagem dinâmica de plugins. |
| **T018** | Phase 6 (US4) | Padrão Afirmativo canônico na governança | P01, P02 | **PASS** | Adota *"Describe the shape you want, not the hole"*. |
| **T019** | Phase 6 (US4) | Fórmula oficial afirmativa para Princípio P03 | P03 | **PASS** | Prescreve HTTP 200 + leitura integral obrigatória. |
| **T020** | Phase 6 (US4) | Barreira síncrona em `research.toml` e `spec-specify.toml` | P01, P03 | **PASS** | Impede orquestrador de responder antes de sub-agentes. |
| **T021** | Phase 7 | Regeneração das 16 skills em `.agents/skills/` | P01, P11 | **PASS** | Dogfooding imediato do compilador de skills. |
| **T022** | Phase 7 | Execução da suíte completa de testes (100% verde) | P05 | **PASS** | Validação de não-regressão global. |
| **T023** | Phase 7 | Auditoria de convergência via `/vitalia-judge` | P01 | **PASS** | Fechamento formal de ciclo com relatório físico. |

---

## 4. Refatorações Recomendadas

- **Nenhuma alteração estrutural obrigatória:** Todas as tarefas atendem integralmente aos requisitos de atomicidade, rastreabilidade, precedência TDD e Cenários de Falsificação P05.

---

## 5. Parecer Conclusivo do Red Team

O plano de tarefas em [`specs/006-sandbox-elevation-and-dynamic-constitution/tasks.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/006-sandbox-elevation-and-dynamic-constitution/tasks.md) está **ESTRITAMENTE CONFORME** com a Constituição Vitalia, os requisitos BDD de `spec.md`, as decisões técnicas de `plan.md` e os critérios de falsificação P05.

> [!IMPORTANT]
> **HITL Gate Soberano:**
> O carimbo constitucional formal:
> `<!-- constitutional-status: APPROVED | auditor: red-team-vitalia | timestamp: <ISO8601> | report: Relatório de inspeção.md -->`
> **aguarda a autorização explícita do desenvolvedor** no chat para ser gravado em `tasks.md` juntamente com a criação da cópia de segurança `tasks.md.bak`.

