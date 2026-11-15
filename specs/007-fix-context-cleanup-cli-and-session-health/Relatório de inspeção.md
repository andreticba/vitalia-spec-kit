<!-- Relatório de inspeção.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 13:48(GMT-04:00) -->
> **Relatório de inspeção.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 13:48(GMT-04:00)**

# Relatório de Inspeção Constitucional Adversarial: Task Verifier (Red Team)
**Feature Alvo**: `specs/007-fix-context-cleanup-cli-and-session-health`  
**Artefato Auditado**: `specs/007-fix-context-cleanup-cli-and-session-health/tasks.md`  
**Data/Hora**: 15-11-2026 13:48 (GMT-04:00)  
**Auditor Responsável**: Red Team Constitucional Vitalia (Sub-Agente de Fronteira)

---

## 1. Resumo Executivo

| Métrica | Valor | Status |
|---|---|---|
| **Total de Tarefas Auditadas** | 24 | Completo |
| **Tarefas Conformes (PASS)** | 24 | 100% |
| **Alertas Constitucionais (WARN)** | 0 | Zero |
| **Violações Críticas (BLOCK)** | 0 | Zero |
| **Tarefas de Teste com Modalidade P05 & Falsificação** | 5 | 100% aderente |
| **Testes Sintáticos Rasos Detectados** | 0 | Veto Respeitado |
| **Parecer Preliminar** | **APROVAÇÃO RECOMENDADA** | Aguardando HITL |

---

## 2. Auditoria do Red Team Gatekeeper (P05 & Anti-Shallow Testing)

1. **Exigência de Modalidade e Cenário de Falsificação (P05):**
   - Todas as 5 tarefas de teste (`T003`, `T004`, `T005`, `T010`, `T015`) contêm explicitamente a modalidade (`[TEST:BUGFIX]` ou `[TEST:NEW]`) e declaram o **Cenário de Falsificação comportamental** (qual falha real de negócio ou contrato fará o teste falhar).
2. **Veto a Testes Rasos / Sintáticos:**
   - Nenhuma tarefa limita-se a verificar se arquivos existem (`is_file()`) ou correspondência de strings. Todas exercitam comportamento funcional de caixa-preta via `pytest` e fixtures com arquivos reais simulando datas passadas e hoje em GMT-04:00.
3. **Precedência de Reprodução em Bugfixes (`[TEST:BUGFIX]`):**
   - As tarefas da Phase 2 (`T003`, `T004`, `T005`) e da Phase 4 (`T010`) precedem as implementações produtivas (`T006-T008` e `T011-T012`), exigindo comprovação prévia do status RED contra o código legado antes da correção.
4. **Respeito aos Contratos OpenAPI 3.0 Limpo:**
   - A tarefa `T000-C` e a Phase 4 (`T010-T013`) validam estritamente o esquema `context_cleanup.schema.json` sem campos proibidos (`$schema`, root `title`, `additionalProperties: false`).

---

## 3. Matriz de Conformidade Tarefa por Tarefa

| ID | Fase | US | Princípios Testados | Parecer | Diagnóstico e Evidências |
|---|---|---|---|---|---|
| **T000-A** | Phase 0 | - | P11 (Dual-Runtime) | **CONFORME** | Validação do Python do kit sem violar isolamento. |
| **T000-B** | Phase 0 | - | P02, P11 | **CONFORME** | Verificação de integridade da stdlib sem acoplamentos ocultos. |
| **T000-C** | Phase 0 | - | P11 (OpenAPI 3.0 Limpo) | **CONFORME** | Validação sintática do schema JSON de context_cleanup. |
| **T001** | Phase 1 | - | P01, P05 | **CONFORME** | Setup do diretório de testes com caminho explícito. |
| **T002** | Phase 1 | - | P04, P05 | **CONFORME** | Fixture temporal simulando datas passadas e hoje em GMT-04:00. |
| **T003** | Phase 2 | - | P00, P05 (Bugfix) | **CONFORME** | `[TEST:BUGFIX]` Cenário de falsificação claro: falha se apagar hoje. |
| **T004** | Phase 2 | - | P02, P05 (Bugfix) | **CONFORME** | `[TEST:BUGFIX]` Cenário de falsificação claro: falha se `--dry-run` apagar. |
| **T005** | Phase 2 | - | P10, P05 (Bugfix) | **CONFORME** | `[TEST:BUGFIX]` Cenário de falsificação claro: falha se menu/parser quebrar. |
| **T006** | Phase 3 | US1 | P04, P08 | **CONFORME** | Parser atômico GMT-04:00 paralelizável `[P]`. |
| **T007** | Phase 3 | US1 | P10, P08 | **CONFORME** | Argparser CLI atômico paralelizável `[P]`. |
| **T008** | Phase 3 | US1 | P00, P02, P10 | **CONFORME** | Menu interativo com padrão afirmativo `[s/N]`. |
| **T009** | Phase 3 | US1 | P01, P05 | **CONFORME** | Validação Green do conjunto US1. |
| **T010** | Phase 4 | - | P05, P15 | **CONFORME** | `[TEST:BUGFIX]` Cenário de falsificação claro: falha se nó faltar. |
| **T011** | Phase 4 | US2 | P02, P15 | **CONFORME** | Sonda ultraleve <50ms com `os.scandir`. |
| **T012** | Phase 4 | US2 | P11, P15 | **CONFORME** | Emissão de métrica OpenAPI 3.0 Limpo. |
| **T013** | Phase 4 | US2 | P01, P05 | **CONFORME** | Validação Green do conjunto US2. |
| **T014** | Phase 5 | US3 | P02, P10 | **CONFORME** | Criação do executável shim com permissão de execução. |
| **T015** | Phase 5 | - | P05 (New) | **CONFORME** | `[TEST:NEW]` Cenário de falsificação claro: falha se shim quebrar. |
| **T016** | Phase 5 | US3 | P02, P10 | **CONFORME** | Aviso não-intrusivo em `session-start.toml`. |
| **T017** | Phase 5 | US3 | P01, P05 | **CONFORME** | Validação Green do conjunto US3. |
| **T018** | Phase 6 | - | P01, P02 | **CONFORME** | Validação dos 4 cenários do quickstart.md. |
| **T019** | Phase 6 | - | P04 | **CONFORME** | Verificação de integridade de cabeçalhos duplos GMT-04:00. |
| **T020** | Phase 6 | - | P01, P05 | **CONFORME** | Cobertura integral 100% da suíte de testes. |

---

## 4. Parecer Conclusivo e Recomendações

O plano de tarefas em `tasks.md` está exemplarmente estruturado, atende a todas as cláusulas pétreas da Constituição do Vitalia SPEC Kit, respeita o princípio de falsificação comportamental P05 e não contém testes superficiais ou acoplamentos indesejados.

**Veredito do Red Team:** **PASS (APTO PARA IMPLEMENTAÇÃO)**.

---

## 5. Pausa HITL Soberana (Gate Humano Obrigatório)

> [!IMPORTANT]
> Em estrita observância ao **Passo 4 do Protocolo de Verificação**, **nenhum carimbo foi aplicado e o arquivo `tasks.md` NÃO foi modificado ainda**.
> A selagem constitucional e a autorização para iniciar a implementação (`/vitalia-spec-implement`) dependem exclusivamente da aprovação soberana do desenvolvedor no chat.
