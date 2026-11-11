<!-- research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 06:22(GMT-04:00) -->
> **research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 06:22(GMT-04:00)**

# Síntese de Concepção — Spec 005: Resolução de Discrepância de Runtime e Arquitetura Dual-Virtualenv

---

## 1. Resumo Executivo e Decisões de Arquitetura

Esta especificação resolve a discrepância identificada no ciclo de inicialização do Vitalia SPEC Kit (`/vitalia-session-start`) após a entrega da Spec 004, eliminando o comportamento reflexo em que agentes de IA tentavam reinstalar o kit global em vez de utilizar o interpretador provisionado.

### Decisões Acordadas (Consenso HITL)
1. **Modelo Dual de Runtime por Domínio de Responsabilidade:**
   - **Runtime Interno do Kit (`{{KIT_PYTHON}}`):** Reside exclusivamente em `${VITALIA_KIT_DIR}/.venv/bin/python3`. É soberano e auto-contido para 100% dos utilitários internos do kit (`vitalia_hook_runner.py`, `scan_environment.py`, `vitalia_context_engine.py`, `vitalia_handoff.py`, `guardian_context.py`, renderers de markdown e suíte de sensores VRSS). Não depende nem polui o projeto cliente com `pyyaml`, `jinja2` ou `jsonschema`.
   - **Runtime do Projeto Local (`{{PROJECT_PYTHON}}`):** Descoberto dinamicamente no início da sessão (`scan_environment.py`), reservado para a execução de tarefas e comandos do projeto cliente (ex: testes de aplicação do cliente, migrações Django/Alembic, build da aplicação).
   - **Fallback Dinâmico:** Comandos de projeto utilizam `{{PROJECT_PYTHON}}` como primário; se o projeto hospedeiro não possuir ambiente virtual configurado, adota fallback para `{{KIT_PYTHON}}` ou emite aviso diagnóstico didático.
2. **Cadeia Defensiva de Descoberta em 4 Níveis (`project_runtime`):**
   - Nível 1: `$VIRTUAL_ENV` ativo no ambiente do shell.
   - Nível 2: `PROJECT_VENV_PATH` explicitamente declarado no `.env` do projeto.
   - Nível 3: Varredura de diretórios canônicos locais (`.venv`, `venv`, `env`, `.env_py`).
   - Nível 4: Resolução determinística do binário (`bin/python3` ou `bin/python` em POSIX; `Scripts/python.exe` em Windows).
3. **Inviolabilidade do Runner e Resolução de Placeholders em `vitalia_hook_runner.py`:**
   - Suporte nativo a `{{KIT_PYTHON}}` e `{{PROJECT_PYTHON}}` em `resolve_placeholders`.
   - Auto-substituição defensiva: se um comando de hook ou script do kit iniciar com `python3 `, o runner substitui por `sys.executable` (o interpretador real do `.venv` que disparou o processo).
4. **Atualização Abrangente de Workflows (`extensions/*.toml`):**
   - Substituição de `python3 {{VITALIA_KIT_DIR}}/...` por `{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/...` em todos os 16 workflows do kit e seus respectivos prompts operacionais (`session-start`, `session-end`, `session-consolidate`, `brainstorming`, `route`).
5. **Diretriz Anti-Loop de Sandbox na IDE Antigravity:**
   - Registro em `AGENTS.md` e `SKILL.md.template` instruindo que acessos a caminhos fora do workspace exigem elevação (`BypassSandbox: true`), proibindo terminantemente que o agente tente rodar `kit-bootstrap.sh` se o kit já estiver instalado no disco.

---

## 2. Relatório de Varredura Completa do Repositório (Mapeamento de Invocação)

Auditoria exaustiva em 100% dos arquivos do repositório (`source/`, `extensions/`, `profiles/`, `integrations/`, `scripts/`, `sensors/`, `tests/` e arquivos de configuração) para mapear todos os pontos de chamada e execução:

### 2.1. Camada de Hooks e Subprocessos Internos do Kit
| Arquivo / Linha | Chamada Atual | Diagnóstico de Risco | Cobertura pela Estratégia Definida |
| :--- | :--- | :--- | :--- |
| **`source/src/vitalia_hook_runner.py`** (L73-90) | `resolve_placeholders` só trata `{{cwd}}`, `{{VITALIA_KIT_DIR}}`, `{{FEATURE_DIR}}` | Não substitui interpretadores Python; deixa `python3` cru na string do comando. | **Inclusão de `{{KIT_PYTHON}}` e `{{PROJECT_PYTHON}}`** na tabela de substituição direta do runner. |
| **`source/src/vitalia_hook_runner.py`** (L182-184) | `subprocess.run(cmd, shell=True, ...)` | O shell herda o `$PATH` do ambiente hospedeiro e executa o `python3` global/sistema. | **Auto-substituição defensiva em runtime:** se `cmd` contiver chamadas a scripts do kit iniciadas por `python3 `, o runner reescreve automaticamente para `sys.executable` (o interpretador do `.venv` ativo no processo pai). |
| **`source/src/vitalia_hook_runner.py`** (L133-144) | Importação dinâmica de `vitalia_handoff.py` via `importlib.util` | Executa in-process no interpretador do processo pai. | ✅ **Já coberto:** roda 100% no `.venv` do kit sem chamar subprocessos. |

### 2.2. Camada de Workflows (16 arquivos em `source/extensions/*.toml`)
| Arquivo | Localização | Chamada Atual | Cobertura pela Estratégia Definida |
| :--- | :--- | :--- | :--- |
| **Todos os 16 workflows `.toml`** (`analyze`, `architect`, `brainstorming`, `clarify`, `converge`, `judge`, `research`, `route`, `session-consolidate`, `session-end`, `session-start`, `spec-implement`, `spec-plan`, `spec-specify`, `spec-tasks`, `task-verifier`) | Bloco `[hooks.before]` (L10-14) | `before = ["python3 {{VITALIA_KIT_DIR}}/src/hooks/scan_environment.py"]` | Substituição em lote para:<br>`before = ["{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/hooks/scan_environment.py"]` |
| **`session-start.toml`** | Prompt (L68-69) | `execute python3 {{VITALIA_KIT_DIR}}/src/vitalia_context_engine.py --action init/consolidate` | Atualização do prompt para instruir explicitamente:<br>`{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/vitalia_context_engine.py --action ...` |
| **`session-end.toml`** | Prompt (L112) | `python3 {{VITALIA_KIT_DIR}}/src/vitalia_context_engine.py --action end ...` | Atualização do prompt para instruir explicitamente:<br>`{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/vitalia_context_engine.py --action end ...` |
| **`session-consolidate.toml`** | Prompt (L66, 110) | `python3 {{VITALIA_KIT_DIR}}/src/vitalia_context_engine.py --action consolidate` | Atualização do prompt para instruir explicitamente:<br>`{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/vitalia_context_engine.py --action consolidate` |
| **`brainstorming.toml`** | Prompt (L183) | `python3 {{VITALIA_KIT_DIR}}/src/vitalia_handoff.py create ...` | Atualização do prompt para instruir explicitamente:<br>`{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/vitalia_handoff.py create ...` |
| **`route.toml`** | Prompt (L100, 104) | `python3 {{VITALIA_KIT_DIR}}/src/vitalia_handoff.py consume/create ...` | Atualização do prompt para instruir explicitamente:<br>`{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/vitalia_handoff.py ...` |
| **`spec-implement.toml`** | Prompt (L92-93, 119) | `python --version`<br>`pytest no terminal` | **Domínio do Projeto Local:** o prompt passa a instruir o uso do `{{PROJECT_PYTHON}}` descoberto pelo kit (ex: `{{PROJECT_PYTHON}} -m pytest ...`). |
| **`spec-tasks.toml`** | Prompt (L148) | `- [ ] T000-B Verificar versão Python do venv: python --version` | Orientação contextualizada para validar o `{{PROJECT_PYTHON}}` do projeto hospedeiro. |

### 2.3. Camada de Descoberta e Diagnóstico (`kit_env_bootstrap.py` e `scan_environment.py`)
| Arquivo / Linha | Comportamento Atual | Risco | Cobertura pela Estratégia Definida |
| :--- | :--- | :--- | :--- |
| **`source/src/kit_env_bootstrap.py`** (L107-108) | `if (script_kit_root / "profiles" / "constitution.yaml").exists(): return script_kit_root` | Se executado no repositório do kit sem `VITALIA_KIT_DIR` setado, resolvia para `source/` (que não tem `.venv`), em vez de `~/.vitalia-spec-kit`. | **Ordem de precedência corrigida:** prioriza `VITALIA_KIT_DIR` (env $\to$ `.env`) e `~/.vitalia-spec-kit` antes de recorrer a `script_kit_root`. |
| **`source/src/kit_env_bootstrap.py`** (L161-163) | `venv_ok = kit_venv_ok or proj_venv_ok`<br>`venv_path = kit_venv_path or proj_venv_path` | Conflacionava os dois mundos. Se o kit não tivesse venv mas o projeto tivesse, reportava `HEALTHY`. | **Separação estrita em 2 nós:**<br>1. `kit_runtime` (status exclusivo do `.venv` do kit);<br>2. `project_runtime` (descoberta em 4 níveis do ambiente do cliente com caminho do binário). |
| **`source/src/kit_env_bootstrap.py`** (Nova função) | Ausência de descoberta em 4 níveis para o projeto local | Projetos com Poetry, Pipenv, Conda ou paths customizados eram ignorados. | **Implementação de `find_project_python()`** cobrindo `$VIRTUAL_ENV`, `PROJECT_VENV_PATH`, pastas canônicas e binário executável. |

### 2.4. Camada de Integração de Skills e IDE (`install-project`, `skill_generator.sh`, `SKILL.md.template`)
| Arquivo / Linha | Comportamento Atual | Risco | Cobertura pela Estratégia Definida |
| :--- | :--- | :--- | :--- |
| **`source/integrations/antigravity/SKILL.md.template`** (L15) | `{{VITALIA_KIT_DIR}}/.venv/bin/python3 ...` | Usa caminho absoluto hardcoded; falha silenciosamente no sandbox da IDE. | **Adição do placeholder `{{KIT_PYTHON}}`** normalizado no gerador de skills + diretriz de sandbox no texto de instrução. |
| **`source/bin/lib/skill_generator.sh`** (L89-94) | `sed` substitui `{{NAME}}`, `{{DESCRIPTION}}`, `{{VERSION}}`, `{{VITALIA_KIT_DIR}}` | Não resolvia `{{KIT_PYTHON}}` explicitamente. | **Adição de substituição:**<br>`-e "s|{{KIT_PYTHON}}|${kit_dir}/.venv/bin/python3|g"`. |
| **`source/bin/install-project`** (L10-11) | `DEFAULT_KIT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"` | Quando rodado de dentro de `source/bin/`, definia `KIT_DIR` como `source/`. | **Fallback robusto:** se `SCRIPT_DIR` for dentro de `source/`, define `DEFAULT_KIT_DIR="${HOME}/.vitalia-spec-kit"`. |

### 2.5. Camada de Sensores e Utilitários de Linha de Comando
| Componente | Tipo de Invocação | Diagnóstico | Cobertura pela Estratégia |
| :--- | :--- | :--- | :--- |
| **`source/src/sensors/*.py`** (5 sensores) | Python puro (stdlib `pathlib`, `json`, `argparse`) | Não utilizam subprocessos nem importam pacotes pesados externos. | ✅ **Totalmente seguros:** rodam com qualquer interpretador, mas por padrão são invocados com `{{KIT_PYTHON}}`. |
| **`source/src/vitalia_context_engine.py`** | Módulo CLI com `kit_env_bootstrap.init()` | Importa `yaml` e `jinja2`. | ✅ **Garantido:** será chamado estritamente via `{{KIT_PYTHON}}` nos prompts atualizados. |
| **`source/src/vitalia_handoff.py`** | Módulo CLI stdlib (`json`, `hashlib`) | Gera e consome envelopes JSON de transição. | ✅ **Garantido:** será chamado estritamente via `{{KIT_PYTHON}}` nos prompts atualizados. |
| **`source/src/vitalia_tmp_cleanup.py`** | Módulo CLI stdlib (`shutil`, `pathlib`) | Remove temporários obsoletos de `context/`. | ✅ **Garantido:** executado internamente com `{{KIT_PYTHON}}`. |

### 2.6. Camada de Governança de Agentes (`AGENTS.md`) — Prevenção de Loops Reflexos
| Regra / Seção | Estado Atual | Comportamento do Modelo | Cobertura pela Estratégia |
| :--- | :--- | :--- | :--- |
| **Seção 8 (Isolamento de Runtime)** | Menciona `${VITALIA_KIT_DIR}/.venv`, mas não menciona a fronteira do sandbox da IDE. | Ao receber código 127 (`No such file or directory`) para `/home/andre/.vitalia-spec-kit`, a IA assume que o kit não existe e tenta rodar `kit-bootstrap.sh`. | **Inclusão da Regra Constitucional Anti-Loop:**<br>1. Falhas em caminhos de `${VITALIA_KIT_DIR}` devem ser reexecutadas com `BypassSandbox: true`;<br>2. **É estritamente proibido** ao agente acionar `kit-bootstrap.sh` por conta própria sem instrução humana expressa. |

---

## 3. Engenharia Reversa Funcional em 3 Camadas

| Componente Afetado | Intenção a Preservar (Negócio Puro) | Legado a Purgar (Débito Técnico) | Contrato do Consumidor (Cliente/IDE) |
| :--- | :--- | :--- | :--- |
| **`vitalia_hook_runner.py`** | Executar hooks `before`/`after` e construir envelopes sem perda de integridade | Subprocessos cegos via `shell=True` com `python3` cru do `$PATH` global | Retornar stub JSON limpo com `workflow_context_file` físico |
| **`source/extensions/*.toml`** (16 workflows) | Declarar pré-condições, ferramentas e prompt de cada comando SDD | Chamadas a `python3` genérico nos hooks e nos blocos de instrução dos prompts | Fornecer comandos executáveis exatos sem exigir resolução ad-hoc pela IA |
| **`kit_env_bootstrap.py` & `scan_environment.py`** | Diagnosticar a saúde do ambiente local e do kit sem containers locais | Conflacionar o `.venv` do projeto com o do kit (`venv_ok = kit_venv_ok or proj_venv_ok`) | Payload estruturado separando `kit_runtime` de `project_runtime` |
| **`AGENTS.md` & `SKILL.md.template`** | Orientar a IA sobre o ciclo de vida e comandos da IDE Antigravity | Omissão quanto ao erro de sandbox (código 127), causando auto-reinstalação reflexa | Instruções claras com `BypassSandbox: true` e veto a `kit-bootstrap.sh` desnecessário |

---

## 4. Matriz de Testes P05 e Cenários de Falsificação

| ID | Modalidade | Componente | Comportamento Validado | Cenário de Falsificação (O que fará falhar) |
| :--- | :--- | :--- | :--- | :--- |
| **T-005-01** | `[TEST:BUGFIX]` | `vitalia_hook_runner.py` | Hooks `before` executam exclusivamente com `sys.executable` / `{{KIT_PYTHON}}`, mesmo se `python3` no `$PATH` estiver quebrado ou ausente. | Mock de `python3` quebrado no `$PATH` (exit code 127). O teste falha se o hook runner invocar o mock em vez do `.venv`. |
| **T-005-02** | `[TEST:NEW]` | `kit_env_bootstrap.py` | Descoberta em 4 níveis de `project_runtime` (VIRTUAL_ENV, .env, pastas locais, fallback). | Falha se `PROJECT_VENV_PATH` customizado não for reconhecido ou se a ausência de `.venv` no projeto mascarar falha no kit. |
| **T-005-03** | `[TEST:REFACTOR]` | `extensions/*.toml` | 100% dos 16 workflows usam `{{KIT_PYTHON}}` nos hooks `before` e prompts sem nenhuma ocorrência de `python3 {{VITALIA_KIT_DIR}}`. | Sensor/linter falha se qualquer `.toml` contiver `python3 {{VITALIA_KIT_DIR}}`. |
| **T-005-04** | `[TEST:MIGRATION]` | `install-project` & Skills | `install-project` gera `.agents/skills/*/SKILL.md` com resolução íntegra sem caminhos órfãos e com diretrizes de sandbox. | Falha se `{{KIT_PYTHON}}` não for resolvido ou se a regra anti-loop estiver ausente de `AGENTS.md`. |

---

## 5. Requisitos Funcionais Preliminares e Escopo

### No Escopo (MVP da Spec 005)
- **FR-01:** Implementar em `kit_env_bootstrap.py` a resolução em 4 níveis do `project_runtime` e a separação estrita de `kit_runtime` no JSON de diagnóstico.
- **FR-02:** Implementar em `vitalia_hook_runner.py` a substituição dos placeholders `{{KIT_PYTHON}}` e `{{PROJECT_PYTHON}}`, com substituição defensiva de `python3 ` por `sys.executable` para scripts do kit.
- **FR-03:** Atualizar as 16 extensões canônicas em `source/extensions/*.toml` (hooks e prompts operacionais).
- **FR-04:** Atualizar `source/integrations/antigravity/SKILL.md.template` e `source/AGENTS.md` com as diretrizes de sandbox e veto à reinstalação não-solicitada.
- **FR-05:** Atualizar `tests/test_bootstrap_and_install.py` e suíte de testes com a validação das 4 modalidades P05.

### 🚧 Ideias Estacionadas (Out of Scope)
- Suporte a ambientes virtuais remotos (SSH/DevContainer/Docker) — estacionado para release v0.1.0+.
- Gerenciador automático de pacotes do projeto cliente (`pip install` automático na aplicação) — responsabilidade do desenvolvedor.

---

## 6. Rastro de Pesquisa e Grounding (P03)

| # | Afirmação / Tecnologia | Fonte Canônica | URL Validada (HTTP 200) | Status Temporal | Data |
| :---: | :--- | :--- | :--- | :---: | :---: |
| 1 | Python `sys.executable` e subprocess isolation | Python Standard Library Documentation (`sys`, `subprocess`) | `https://docs.python.org/3/library/sys.html` | Ativo (Python 3.10+) | 11-11-2026 |
| 2 | PEP 405 — Virtual Environments (`pyvenv.cfg`, `VIRTUAL_ENV`) | Python Enhancement Proposals | `https://peps.python.org/pep-0405/` | Canônico | 11-11-2026 |
| 3 | Antigravity IDE Sandbox & Execution Model | Antigravity Built-in Documentation & AGY Guidelines | Antigravity System Context Guidelines | Canônico v2.0 | 11-11-2026 |
