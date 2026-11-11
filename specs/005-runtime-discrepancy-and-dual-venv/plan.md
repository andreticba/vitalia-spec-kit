<!-- plan.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:00(GMT-04:00) -->
> **plan.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:00(GMT-04:00)**

# Implementation Plan: Spec 005 — Runtime Discrepancy, Dual-Virtualenv and Runner Inviolability

**Branch**: `005-runtime-discrepancy-and-dual-venv` | **Date**: 11-11-2026 | **Spec**: [`specs/005-runtime-discrepancy-and-dual-venv/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/spec.md)

---

## 1. Summary

Implementação da arquitetura Dual-Runtime e blindagem definitiva de execução do Vitalia SPEC Kit. O plano compreende:
1. Desacoplamento estrito entre o runtime de governança interna do kit (`{{KIT_PYTHON}}` em `${VITALIA_KIT_DIR}/.venv`) e o runtime da aplicação hospedeira (`{{PROJECT_PYTHON}}`), resolvido em 4 níveis de descoberta dinâmica no `kit_env_bootstrap.py`.
2. Inviolabilidade do executor `vitalia_hook_runner.py` via suporte nativo aos novos placeholders e auto-substituição defensiva de comandos `python3` para `sys.executable` quando o alvo for um utilitário interno do kit.
3. Normalização abrangente dos 16 workflows canônicos em `source/extensions/*.toml` e seus prompts operacionais.
4. Governança constitucional anti-loop no `AGENTS.md` e `SKILL.md.template`, neutralizando a tentativa reflexa de reinstalar o kit em caso de restrição de sandbox na IDE Antigravity.

---

## 2. Technical Context

- **Linguagem / Runtime**: Python >= 3.10 (stdlib pura para módulos de bootstrap e runner; dependências `pyyaml`, `jinja2`, `jsonschema` isoladas no `.venv` do kit).
- **Ambiente de Testes**: `pytest >= 8.0.0` com testes comportamentais de caixa-preta via `subprocess.run` em ambientes isolados `tmp_path`.
- **Plataforma Alvo**: Linux padrão, WSL2/Ubuntu e compatibilidade Windows (`Scripts/python.exe`).
- **Tipo de Projeto**: Arquitetura de 4 Camadas / Ferramental de Linha de Comando e Agentes para IDE.
- **Metas de Performance**: Descoberta em 4 níveis de `project_runtime` executada em $< 50\text{ ms}$; overhead de resolução de placeholders no runner $< 5\text{ ms}$.
- **Restrições**: Proibição de injeção mista de `sys.path` que polua o kit com pacotes do projeto cliente; pureza 100% de `.agents/skills/`; contratos de diagnóstico estritamente sem meta-schemas (subset OpenAPI 3.0 limpo).

---

## 3. Constitution Check

- **P00 (Purpose Arbiter):** Aprovado. Elimina falhas de inicialização e frustração de desenvolvedores com falsos loops de bootstrap.
- **P01 (SDD Inviolability):** Aprovado. Pipeline rigorosamente seguido a partir de `spec.md` e clarificação aprovada.
- **P03 (External Grounding):** Aprovado. Grounding em PEP 405, `sys.executable` e modelo de sandbox validado na Seção 5 de `spec.md` e em `research.md`.
- **P04 (Timestamp GMT-04:00):** Aprovado. Cabeçalho duplo-stamp em 100% dos documentos gerados.
- **P05 (TDD & Falsificação):** Aprovado. Test Depth Agreement (TDA) formalizado com 4 modalidades e cenários de falsificação black-box.
- **P10 (Didactics-First):** Aprovado. Diagnósticos e avisos claros de fallback orientam o desenvolvedor sem mensagens crípticas.
- **P11 (Runtime Autonomy):** Aprovado. O cerne da Spec 005: isolamento incondicional entre Camada 2 (Kit) e Camada 1 (Projeto).
- **P15 (Observability):** Aprovado. Estruturação em 2 nós (`kit_runtime` e `project_runtime`) em `scan_environment.py`.
- **P16 (Mermaid Integrity):** Aprovado. Labels entre aspas duplas em todos os diagramas.

---

## 4. Technical Decisions

Consolidadas em [`specs/005-runtime-discrepancy-and-dual-venv/research.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/research.md):
- **D1:** Uso de `sys.executable` e inspeção de caminhos para auto-substituição de comandos `python3` no runner.
- **D2:** Algoritmo de descoberta em 4 níveis para `project_runtime` (`$VIRTUAL_ENV` $\to$ `.env` $\to$ pastas locais $\to$ resolução de binário).
- **D3:** Resolução dos placeholders `{{KIT_PYTHON}}` e `{{PROJECT_PYTHON}}` com fallback dinâmico transparente.
- **D4:** Regra cognitiva anti-loop de sandbox em `AGENTS.md` instruindo `BypassSandbox: true` e vetando `./kit-bootstrap.sh`.

---

## 5. Matriz de Migração e Preservação Comportamental

| Componente | Comportamento Existente a Preservar (Invariante de Negócio) | Acoplamento / Defeito a Remover | Contrato do Consumidor & Estratégia de Teste (`[TEST:MIGRATION]`) |
| :--- | :--- | :--- | :--- |
| [`source/src/vitalia_hook_runner.py`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/src/vitalia_hook_runner.py) | Parse de TOML, execução de hooks `before`/`after`, persistência do envelope JSON físico e ejeção de stub no stdout. | Purgar execução cega de `python3` via `shell=True` sem vínculo com o interpretador ativo. | `[TEST:MIGRATION]`: Executar `test_hook_runner_clean.py` garantindo que os envelopes continuem gerados com integridade e que os hooks executem via `sys.executable`. |
| [`source/src/kit_env_bootstrap.py`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/src/kit_env_bootstrap.py) | Localização da raiz do projeto (`find_project_root`), parser stdlib de `.env` e injeção dinâmica de `site-packages` do kit. | Purgar resolução falha de `resolve_kit_dir` para `source/` local e descontinuar a união indistinta `venv_ok = kit_venv_ok or proj_venv_ok`. | `[TEST:MIGRATION]`: Testar projetos com e sem `.venv` local provando que o diagnóstico reporta `kit_runtime` e `project_runtime` separadamente. |
| [`source/extensions/*.toml`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/extensions/) (16 arquivos) | Definição de permissões de ferramentas, prompts, metadados e hooks de cada comando SDD. | Purgar referências cruas a `python3 {{VITALIA_KIT_DIR}}` nos hooks e prompts. | `[TEST:REFACTOR]`: Linter automatizado garantindo 0 ocorrências de `python3 {{VITALIA_KIT_DIR}}`. |
| [`source/bin/lib/skill_generator.sh`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/bin/lib/skill_generator.sh) | Pureza 100% de `.agents/skills/`, idempotência e substituição de metadados em `SKILL.md`. | Purgar ausência de resolução do placeholder `{{KIT_PYTHON}}`. | `[TEST:MIGRATION]`: Testar geração de skills provando que `{{KIT_PYTHON}}` é expandido para o caminho real do `.venv/bin/python3`. |

---

## 6. Test Depth Agreement (TDA — Matriz Constitucional P05)

| Modalidade P05 | Alvo da Mudança | Cenário de Falsificação Comportamental (Como o teste falha se a regra quebrar) |
| :--- | :--- | :--- |
| **`[TEST:BUGFIX]`** | `vitalia_hook_runner.py` | Injetar binário mock quebrado de `python3` no `$PATH` temporário retornando código 127. O teste falha se `vitalia_hook_runner.py` invocar o mock em vez de usar `sys.executable`. |
| **`[TEST:NEW]`** | `kit_env_bootstrap.py` | Criar projeto com `.env` contendo `PROJECT_VENV_PATH=./custom_dir`. O teste falha se `find_project_python()` não localizar o interpretador ou se falhar na ancoragem de caminhos relativos em `project_root`. |
| **`[TEST:REFACTOR]`** | `source/extensions/*.toml` | Linter sobre os 16 arquivos `.toml`. O teste falha se qualquer arquivo contiver a string `python3 {{VITALIA_KIT_DIR}}` no hook `before`. |
| **`[TEST:MIGRATION]`** | `install-project` & `skill_generator.sh` | Invocar `install-project` a partir do repositório clonado sem `VITALIA_KIT_DIR` setado. O teste falha se as skills geradas em `.agents/skills/` contiverem placeholders não resolvidos ou apontarem para `source/.venv` em vez de `~/.vitalia-spec-kit/.venv`. |

---

## 7. Project Structure

### Documentation (Spec 005)
```
specs/005-runtime-discrepancy-and-dual-venv/
├── research-brainstorming.md
├── regencia-architect-plano-turno.md
├── spec.md
├── ambiguity_metrics.json
├── checklists/
│   └── requirements.md
├── research.md
├── plan.md
├── contracts/
│   └── cli-contracts.md
├── quickstart.md
└── Relatório de Inspeção - plan.md  (gerado pelo SDD-Judge)
```

### Source Code Modificado
```
source/
├── src/
│   ├── kit_env_bootstrap.py          (find_project_python, resolve_kit_python, dual payload)
│   ├── vitalia_hook_runner.py        (resolve_placeholders {{KIT_PYTHON}}/{{PROJECT_PYTHON}}, auto-substituição)
│   └── hooks/
│       └── scan_environment.py       (exposição dos 2 nós kit_runtime e project_runtime)
├── extensions/
│   ├── *.toml (16 arquivos: hooks before atualizados para {{KIT_PYTHON}})
│   ├── session-start.toml            (prompts atualizados)
│   ├── session-end.toml              (prompts atualizados)
│   ├── session-consolidate.toml      (prompts atualizados)
│   ├── brainstorming.toml            (prompts atualizados)
│   ├── route.toml                    (prompts atualizados)
│   ├── spec-implement.toml           (orientação contextual {{PROJECT_PYTHON}})
│   └── spec-tasks.toml               (orientação contextual {{PROJECT_PYTHON}})
├── bin/
│   ├── install-project               (fallback de DEFAULT_KIT_DIR para ~/.vitalia-spec-kit)
│   └── lib/
│       └── skill_generator.sh        (substituição de {{KIT_PYTHON}})
├── integrations/
│   └── antigravity/
│       └── SKILL.md.template         (diretriz de sandbox no item 1)
└── AGENTS.md                         (regra constitucional anti-loop na Seção 8)
```

---

## 8. Phase Overview

- **Phase 1: Setup & TDA:** Implementação dos testes da Matriz P05 em `tests/test_bootstrap_and_install.py` comprovando a falha antes da correção (Red Phase).
- **Phase 2: Dual-Runtime Bootstrap:** Refatoração de `kit_env_bootstrap.py` e `scan_environment.py` com o algoritmo de 4 níveis.
- **Phase 3: Runner Inviolability:** Atualização de `vitalia_hook_runner.py` com resolução de placeholders e auto-substituição defensiva.
- **Phase 4: Normalização de Workflows:** Atualização em lote dos 16 arquivos `.toml` em `source/extensions/`.
- **Phase 5: Governança de Agentes e Skills:** Atualização de `install-project`, `skill_generator.sh`, `SKILL.md.template` e `AGENTS.md`.
- **Phase 6: Verificação Green & Dogfooding:** Execução da suíte de testes P05 completa e validação prática da inicialização de sessão.

