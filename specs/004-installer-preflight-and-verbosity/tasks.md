<!-- constitutional-status: APPROVED | auditor: red-team-vitalia | timestamp: 2026-11-10T19:44:02-04:00 | report: Relatório de inspeção.md -->
<!-- tasks.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:44(GMT-04:00) -->
> **tasks.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:44(GMT-04:00)**

# Tasks: Spec 004 — Pre-Flight Check, Isolamento Estrito do `.venv` e Observabilidade Passo a Passo na Instalação

**Spec**: [`specs/004-installer-preflight-and-verbosity/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/004-installer-preflight-and-verbosity/spec.md)  
**Plan**: [`specs/004-installer-preflight-and-verbosity/plan.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/004-installer-preflight-and-verbosity/plan.md)  
**Relatório de Inspeção**: [`specs/004-installer-preflight-and-verbosity/Relatório de inspeção.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/004-installer-preflight-and-verbosity/Relatório de inspeção.md)  
**Status**: APPROVED (Auditado pelo Sub-Agente Red Team Constitucional)  
**Homologado em**: 10-11-2026 19:44(GMT-04:00)

---

## MVP Scope

> O **MVP Scope** compreende a implementação integral de **Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) + Phase 5 (US3)**.  
> Este conjunto entrega o instalador blindado, com pre-flight preventivo, observabilidade contínua, isolamento inviolável de dependências Python e ativação segura de projetos hospedeiros.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e grounding ANTES de qualquer implementação. Sem label de US.*

- [X] T000-A Verificar interpretador Python ativo no ambiente: `python3 --version` garantindo versão `>= 3.10`
- [X] T000-B Verificar integridade do ambiente de teste com `pytest --version` e `git --version`
- [X] T000-C Executar linha base da suíte de testes existente: `pytest tests/` comprovando integridade prévia antes de qualquer alteração

---

## Phase 1: Setup

*Inicialização da estrutura de diretórios e arquivos de suporte. Sem label de US.*

- [X] T001 Garantir a criação da pasta de bibliotecas de shell em `source/bin/lib`
- [X] T002 Preparar scaffold e fixtures de teste em `tests/test_bootstrap_and_install.py` para isolamento de subprocessos e diretórios temporários

---

## Phase 2: Foundational

*Utilitários compartilhados de teste e mock para subprocessos de shell. Sem label de US.*

- [X] T003 [P] Implementar helpers de teste em `tests/test_bootstrap_and_install.py` para execução de scripts Bash sob isolamento (`subprocess.run`), captura de streams stdout/stderr e simulação de diretórios somente-leitura (`chmod 555`)

---

## Phase 3: User Story 1 — Pre-Flight Check Modular (`preflight.sh`) (FR-001)

**Story Goal**: Fornecer a biblioteca modular `source/bin/lib/preflight.sh` com validações determinísticas de versão semântica de Python, suporte a venv executável, capacidade real de escrita em ancestrais existentes (via probe temporário) e requisitos de Git antes de qualquer mutação de disco.  
**Independent Test**: Executar `pytest tests/test_bootstrap_and_install.py -k test_preflight` isoladamente.  
**Referência**: FR-001.1, FR-001.2, FR-001.3, FR-001.4, SC-001

- [X] T004 [P] [US1] [TEST:NEW] Implementar testes unitários para a biblioteca `preflight.sh` em `tests/test_bootstrap_and_install.py` cobrindo `check_python_version_semver`, `check_venv_capability`, `check_writable_target` e `check_git_requirements` — Cenário de Falsificação: o teste falha se mock de Python 3.9 for aceito, se caminho inexistente dentro de diretório `chmod 555` for aprovado pelo teste de escrita, se arquivos temporários probe não forem limpos em disco ou se falha no `python3 -m venv` não emitir a mensagem prescritiva de instalação (`python3-venv`)
- [X] T005 [P] [US1] Implementar o módulo `source/bin/lib/preflight.sh` com as funções `check_python_version_semver`, `check_venv_capability`, `check_writable_target` (inspeção recursiva de ancestral existente com probe `mktemp`) e `check_git_requirements` em estrita conformidade com o contrato em `contracts/cli-contracts.md`

---

## Phase 4: User Story 2 — Blindagem do `.venv` Puro e Observabilidade no `kit-bootstrap.sh` (FR-002, FR-003, FR-004)

**Story Goal**: Garantir que o instalador global `kit-bootstrap.sh` execute o pre-flight no Passo 0, purgue incondicionalmente `--system-site-packages`, direcione logs completos para `/tmp/vitalia-bootstrap-${UID}.log`, forneça feedback contínuo passo a passo (`⏳`, `✅`, `❌`, `⚠️`), suporte a flag `-v`/`--verbose` e exiba banner final com comando exato para o shell ativo.  
**Independent Test**: Executar `pytest tests/test_bootstrap_and_install.py -k test_bootstrap` cobrindo cenários de sucesso, erro de escrita e falha simulada de pip.  
**Referência**: FR-002, FR-003, FR-004, SC-001, SC-002, SC-003, SC-004

- [X] T006 [P] [US2] [TEST:BUGFIX] Implementar testes de regressão e falha de isolamento para `kit-bootstrap.sh` em `tests/test_bootstrap_and_install.py` — Cenário de Falsificação: o teste falha se o script recorrer a `--system-site-packages` quando `pip install` falhar, se o log detalhado não for salvo em `/tmp/vitalia-bootstrap-${UID}.log`, se `--target-dir` somente-leitura não for abortado no Passo 0 antes de criar pastas parciais, ou se a flag `-v`/`--verbose` não emitir streaming direto
- [X] T007 [US2] Refatorar `kit-bootstrap.sh` integrando `source/bin/lib/preflight.sh` no Passo 0, purgando incondicionalmente `--system-site-packages`, direcionando logs para `/tmp/vitalia-bootstrap-${UID:-$(id -u)}.log`, adicionando feedback visual passo a passo (`⏳`, `✅`), suporte a `-v`/`--verbose` e banner final com detecção dinâmica de shell ativo (`$SHELL`, `$ZSH_VERSION`, `$BASH_VERSION`)

---

## Phase 5: User Story 3 — Integração do Pre-Flight no Ativador de Projetos (`install-project`) (FR-005)

**Story Goal**: Garantir que a ativação de projetos hospedeiros valide a capacidade de escrita e requisitos de ambiente antes de criar `.vitalia/` ou `.agents/skills/`, reportando com clareza o status de clonagem ou inicialização dos repositórios de memória de sessão e dados.  
**Independent Test**: Executar `pytest tests/test_bootstrap_and_install.py -k test_install_project` em ambiente limpo e em diretório com restrição de permissão.  
**Referência**: FR-005

- [X] T008 [P] [US3] [TEST:REFACTOR] Implementar testes de integração de pre-flight para `install-project` em `tests/test_bootstrap_and_install.py` — Cenário de Falsificação: o teste falha se `install-project` tentar criar `.vitalia/` ou `.agents/skills/` em projeto sem permissão de escrita, ou se omitir mensagens sobre clonagem vs init local de sessão/dados
- [X] T009 [US3] Atualizar `source/bin/install-project` para carregar `lib/preflight.sh`, invocar pré-validações de escrita e Git, e reportar o status claro de detecção/clonagem dos repositórios de memória

---

## Phase 6: Polish & Cross-Cutting

*Qualidade, purga residual de código e validação de regressão ponta a ponta. Sem label de US.*

- [X] T010 [TEST:MIGRATION] Executar a suíte completa de testes do repositório (`pytest tests/`) e validar purga completa de `--system-site-packages` via grep em arquivos shell — Cenário de Falsificação: falha se qualquer teste unitário ou e2e existente quebrar, se o tempo de pre-flight exceder 2 segundos ou se o grep encontrar ocorrências ativas de `--system-site-packages` no repositório
- [X] T011 [P] Atribuir permissão de execução (`chmod +x`) em `source/bin/lib/preflight.sh` e validar cenários de uso manual documentados em `specs/004-installer-preflight-and-verbosity/quickstart.md`

---

## Dependency Graph

```text
Phase 0 (Grounding)
   ↓
Phase 1 (Setup: T001, T002)
   ↓
Phase 2 (Foundational: T003)
   ↓
Phase 3 (US1: T004 [TEST:NEW] → T005)
   ↓
Phase 4 (US2: T006 [TEST:BUGFIX] → T007)
   ↓
Phase 5 (US3: T008 [TEST:REFACTOR] → T009)
   ↓
Phase 6 (Polish: T010 [TEST:MIGRATION], T011)
```

---

## Parallel Execution

As seguintes tarefas marcadas com `[P]` não possuem dependências entre si e podem ser desenvolvidas ou executadas em paralelo dentro de suas respectivas fases:
- `T003` (Foundational: helpers de teste) pode ser implementado em paralelo com a estrutura de arquivos.
- `T004` (US1 Tests) e `T005` (US1 Code) podem ser desenvolvidos com estrita adesão ao ciclo Red-Green.
- `T006` (US2 Tests) pode ser preparado em paralelo com `T008` (US3 Tests).
- `T011` (Permissões e documentação rápida) pode ser executado em paralelo com `T010`.
