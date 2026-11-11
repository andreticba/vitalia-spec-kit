<!-- spec.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 06:45(GMT-04:00) -->
> **spec.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 06:45(GMT-04:00)**

# Especificação Funcional — Spec 005: Resolução de Discrepância de Runtime, Arquitetura Dual-Virtualenv e Inviolabilidade do Hook Runner

- **Data:** 11-11-2026
- **Versão:** 0.0.1
- **Autor/Agente:** Vitalia SPEC Kit Architect & Requirements Engineer
- **Feature:** `specs/005-runtime-discrepancy-and-dual-venv`
- **Status:** DRAFT (Submetido à Auditoria `/vitalia-judge --mode=specify` e Aprovação HITL)
- **Fontes Canônicas Obrigatórias:**
  - [`specs/005-runtime-discrepancy-and-dual-venv/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/research-brainstorming.md)
  - [`docs/adr/ADR-0004-dual-runtime-architecture-and-runner-inviolability.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0004-dual-runtime-architecture-and-runner-inviolability.md)
  - [`specs/005-runtime-discrepancy-and-dual-venv/regencia-architect-plano-turno.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/regencia-architect-plano-turno.md)

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

### 1.1 Problema de Negócio e Engenharia
Após a conclusão bem-sucedida da Spec 004, que blindou o ciclo de bootstrap com pre-flight check e ambiente virtual puro em `${VITALIA_KIT_DIR}/.venv`, a inicialização de sessões de trabalho (`/vitalia-session-start`) em estações reais continuou apresentando falhas graves de execução e induzindo agentes de IA em loops reflexos:

1. **Discrepância de Chamada nos Workflows:** Os 16 arquivos `.toml` em `source/extensions/` continuavam declarando hooks e instruções de prompt referenciando `python3` genérico, contornando o `.venv` do kit recém-criado.
2. **Evasão de Runtime no Hook Runner:** O componente `vitalia_hook_runner.py` invocava os comandos de hooks via `subprocess.run(cmd, shell=True)` usando o executável `python3` encontrado no `$PATH` do terminal corrente (o Python do sistema ou o ambiente local do projeto hospedeiro, desprovido de `pyyaml`, `jinja2` e `jsonschema`).
3. **Fronteira de Sandbox da IDE e Reação Reflexa da IA:** Na IDE Antigravity, comandos de terminal executam sob sandbox restrito ao workspace local (`${PWD}`). Ao tentar acessar `/home/andre/.vitalia-spec-kit/.venv/bin/python3` sem elevação (`BypassSandbox: true`), o shell reporta código 127 (`No such file or directory`). Diante desse erro, o modelo assume falsamente que o kit não está instalado e dispara reflexivamente `./kit-bootstrap.sh`, gerando atrito e falhas em cascata.
4. **Conflacuação de Runtimes no Diagnóstico:** O módulo `kit_env_bootstrap.py` mesclava a saúde do `.venv` do kit com o do projeto (`venv_ok = kit_venv_ok or proj_venv_ok`), mascarando anomalias e falhando em reconhecer projetos com ambientes virtuais customizados (Poetry, Pipenv, caminhos arbitrários).

### 1.2 Declaração de Impacto e Princípios Constitucionais (P02, P10, P11, P15)
- **Impacto ao Desenvolvedor (P02):** Sessão inicia sem erros e sem pausas artificiais causadas por reinstalações redundantes do kit global.
- **Isolamento de Runtime e Agnosticismo (P11):** O kit opera estritamente em seu próprio `.venv` (Camada 2), e o projeto cliente opera no seu próprio `.venv` (Camada 1), eliminando 100% de colisões de dependências.
- **Engenharia Didática (P10):** Mensagens de diagnóstico orientam claramente sobre a separação dos dois ambientes e indicam a necessidade de elevação de sandbox sem induzir a IA em loop.
- **Observabilidade Estruturada (P15):** O JSON de saúde separa explicitamente `kit_runtime` e `project_runtime`.

---

## 2. Requisitos Funcionais

### FR-001: Arquitetura Dual-Runtime e Descoberta em 4 Níveis (`kit_env_bootstrap.py`)
O sistema **MUST** diagnosticar e gerenciar dois runtimes Python independentes sem misturar seus ambientes de execução:
- **FR-001.1 (Nó `kit_runtime`):** O módulo **MUST** auditar a integridade de `${VITALIA_KIT_DIR}/.venv` e reportar o status `HEALTHY` do kit exclusivamente com base na presença e capacidade de importação de `yaml, jinja2, jsonschema` pelo interpretador `${VITALIA_KIT_DIR}/.venv/bin/python3`.
- **FR-001.2 (Descoberta em 4 Níveis de `project_runtime`):** O módulo **MUST** implementar o algoritmo `find_project_python()` para identificar o ambiente virtual do projeto hospedeiro na seguinte precedência:
  1. *Nível 1:* Variável de ambiente `$VIRTUAL_ENV` se ativa no shell.
  2. *Nível 2:* Chave `PROJECT_VENV_PATH` declarada no arquivo `.env` da raiz do projeto. Caso o caminho informado seja relativo (ex: `./custom_venv` ou `.venv_app`), o módulo **MUST** ancorá-lo deterministicamente em relação a `project_root` (`(project_root / path).resolve()`), garantindo resolução íntegra independentemente do diretório de trabalho do processo (`cwd`).
  3. *Nível 3:* Varredura na raiz do projeto pelos diretórios canônicos `.venv`, `venv`, `env`, `.env_py`.
  4. *Nível 4:* Resolução determinística do executável (`bin/python3` ou `bin/python` em sistemas POSIX; `Scripts/python.exe` em Windows).
- **FR-001.3 (Payload Estruturado em 2 Nós):** O retorno de `check_environment_health` **MUST** conter os objetos `kit_runtime` (`kit_dir`, `python_bin`, `status`) e `project_runtime` (`project_root`, `has_venv`, `python_bin`, `source_detected`), sem mesclar `venv_ok`.
- **FR-001.4 (Precedência de Resolução de `VITALIA_KIT_DIR`):** A função `resolve_kit_dir` **MUST** priorizar a variável de ambiente `VITALIA_KIT_DIR`, seguida da chave `VITALIA_KIT_DIR` no `.env` e do diretório global padrão `~/.vitalia-spec-kit`, antes de qualquer fallback em `script_kit_root`.

### FR-002: Inviolabilidade do Hook Runner e Placeholders Semânticos (`vitalia_hook_runner.py`)
O executor de hooks **MUST** garantir que os comandos internos do kit rodem no interpretador isolado do kit:
- **FR-002.1 (Placeholders Semânticos):** A função `resolve_placeholders` **MUST** resolver:
  - `{{KIT_PYTHON}}`: Caminho absoluto do interpretador Python do kit (`${VITALIA_KIT_DIR}/.venv/bin/python3`).
  - `{{PROJECT_PYTHON}}`: Caminho absoluto do interpretador do projeto hospedeiro (com fallback dinâmico para `{{KIT_PYTHON}}` se o projeto não possuir ambiente virtual).
- **FR-002.2 (Auto-Substituição Defensiva de Runtime):** Antes de invocar `subprocess.run(cmd, shell=True)`, o runner **MUST** inspecionar o alvo `.py` do comando: se o caminho do script resolver dentro de `${VITALIA_KIT_DIR}` (ou contiver `{{VITALIA_KIT_DIR}}`), o runner **MUST** reescrever defensivamente `python3` para `sys.executable` (o interpretador ativo do processo pai). Caso o script resida fora de `${VITALIA_KIT_DIR}` (ex: hooks customizados do projeto em `.vitalia/extensions.yml`), o runner **MUST** despachar para `{{PROJECT_PYTHON}}`, impedindo que scripts do cliente sejam forçados a executar no virtualenv interno do kit.
- **FR-002.3 (Injeção de Variáveis de Ambiente):** O runner **MUST** injetar `VITALIA_KIT_PYTHON` e `VITALIA_PROJECT_PYTHON` no dicionário de variáveis de ambiente transmitido aos subprocessos.

### FR-003: Normalização dos 16 Workflows (`source/extensions/*.toml`)
Todos os 16 workflows do kit **MUST** ser padronizados:
- **FR-003.1 (Hooks `before`):** O hook `before` de todos os 16 arquivos `.toml` **MUST** ser alterado de `python3 {{VITALIA_KIT_DIR}}/src/hooks/scan_environment.py` para `{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/hooks/scan_environment.py`.
- **FR-003.2 (Prompts Operacionais de Governança):** Os prompts dos workflows `session-start.toml`, `session-end.toml`, `session-consolidate.toml`, `brainstorming.toml` e `route.toml` **MUST** instruir explicitamente o uso de `{{KIT_PYTHON}}` (ou `{{VITALIA_KIT_DIR}}/.venv/bin/python3`) para invocar `vitalia_context_engine.py` e `vitalia_handoff.py`.
- **FR-003.3 (Prompts Operacionais de Aplicação):** Os prompts de `spec-implement.toml` e `spec-tasks.toml` **MUST** instruir expressamente o uso de `{{PROJECT_PYTHON}}` para validar dependências e executar a suíte de testes de negócio da aplicação (ex: `{{PROJECT_PYTHON}} -m pytest`).

### FR-004: Geração de Skills e Resolução de Ativação (`skill_generator.sh` e `install-project`)
A integração de agentes da IDE **MUST**:
- **FR-004.1 (`skill_generator.sh`):** Substituir o placeholder `{{KIT_PYTHON}}` pelo caminho real `${kit_dir}/.venv/bin/python3` durante a compilação de `.agents/skills/*/SKILL.md`.
- **FR-004.2 (`install-project`):** Corrigir a definição de `DEFAULT_KIT_DIR` para que, se invocado a partir de `source/bin/install-project` no repositório clone sem `VITALIA_KIT_DIR` setado, assuma `${HOME}/.vitalia-spec-kit` como padrão em vez de `source/`.

### FR-005: Governança Constitucional Anti-Loop e Diretriz de Sandbox
O sistema **MUST** blindar os agentes de IA contra execuções redundantes:
- **FR-005.1 (`source/AGENTS.md` e `.agents/AGENTS.md`):** **MUST** conter na Seção 8 instrução mandatória informando que códigos de erro 127 (`No such file or directory`) ao invocar `${VITALIA_KIT_DIR}` decorrem do isolamento de sandbox do terminal da IDE Antigravity e exigem reexecução com elevação (`BypassSandbox: true`).
- **FR-005.2 (Veto a `kit-bootstrap.sh`):** A regra **MUST** proibir explicitamente o agente de disparar `./kit-bootstrap.sh` ou tentar reinstalar o kit por iniciativa própria diante de falhas de permissão ou sandbox.
- **FR-005.3 (`SKILL.md.template`):** **MUST** incluir no item 1 a nota orientando o tratamento de sandbox.

---

## 3. Critérios de Sucesso e Cenários BDD (Given/When/Then)

### SC-001: Isolamento de Runtime em Ambiente com PATH Hostil
- **Cenário:** O `$PATH` do terminal possui um script `python3` quebrado ou incompatível (mock retornando erro).
- **Given** que o ambiente do sistema possui um executável `python3` defeituoso no `$PATH`,
- **When** o `vitalia_hook_runner.py` for acionado via `${VITALIA_KIT_DIR}/.venv/bin/python3`,
- **Then** os hooks `before` executam com sucesso utilizando `sys.executable` e o processo conclui com status `ready` sem acionar o mock do `$PATH`.

### SC-002: Descoberta Flexível de Ambientes Virtuais de Projeto
- **Cenário:** Projeto hospedeiro configurado com ambiente virtual em caminho customizado via `PROJECT_VENV_PATH`.
- **Given** um projeto com `.env` contendo `PROJECT_VENV_PATH=/custom/path/venv`,
- **When** `kit_env_bootstrap.init()` for executado,
- **Then** o nó `project_runtime.python_bin` aponta exatamente para `/custom/path/venv/bin/python3` e `has_venv` é `true`.

### SC-003: Pureza de Contratos nos 16 Workflows
- **Cenário:** Inspeção estática de conformidade em todos os `.toml` de `source/extensions/`.
- **Given** os 16 arquivos `.toml` em `source/extensions/`,
- **When** uma varredura por expressões regulares for realizada,
- **Then** zero ocorrências da string `python3 {{VITALIA_KIT_DIR}}` devem existir nos blocos de hooks.

### SC-004: Inexistência de Colisão de Dependências do Projeto
- **Cenário:** Projeto hospedeiro com ambiente virtual sem `pyyaml` nem `jsonschema`.
- **Given** um projeto hospedeiro cujo `.venv` local contenha apenas bibliotecas próprias sem `pyyaml`,
- **When** o comando `/vitalia-session-start` for executado,
- **Then** as operações do kit (`vitalia_context_engine.py`) são concluídas com sucesso usando `{{KIT_PYTHON}}` sem gerar `ModuleNotFoundError`.

### SC-005: Neutralização do Loop de Sandbox da IDE
- **Cenário:** Agente de IA recebe código 127 ao tentar ler `/home/andre/.vitalia-spec-kit` sem permissão de sandbox.
- **Given** o agente executando um comando do kit sob sandbox restrito,
- **When** o comando falhar por restrição de caminho fora do workspace,
- **Then** a diretriz em `AGENTS.md` instrui o agente a reexecutar com `BypassSandbox: true` sem tentar invocar `kit-bootstrap.sh`.

---

## 4. Comportamentos Existentes a Preservar & Defeitos a Reproduzir

### Comportamentos a Preservar
- Manter a emissão do stub JSON contendo `workflow_context_file` físico em `.vitalia/memory/data_storage/context/<machine_id>/`.
- Preservar a integridade de `AGENTS.md` (formato sem comentários soltos antes de frontmatter).
- Preservar a pureza 100% de `.agents/skills/` (sem pastas ocultas residuais).
- Preservar a persistência de histórico e aprendizados compilados em `.vitalia/memory/session/`.

### Defeitos a Reproduzir e Eliminar (Bug Reproduction)
- **Defeito 1:** `vitalia_hook_runner.py` chamando `python3` via `shell=True` falha caso o Python do `$PATH` não possua os pacotes do kit.
- **Defeito 2:** `session-start.toml` orientando o agente a rodar `python3 {{VITALIA_KIT_DIR}}/src/vitalia_context_engine.py` faz o agente executar o Python local do projeto em vez do virtualenv do kit.

---

## 5. Suposições Verificadas e Grounding (Princípio P03)

- **`sys.executable` (Python 3.10+):** Garantido pela especificação da stdlib como o caminho absoluto do interpretador em execução no processo. Verificado em `https://docs.python.org/3/library/sys.html`.
- **PEP 405 (Virtual Environments):** A variável `$VIRTUAL_ENV` e a presença do arquivo `pyvenv.cfg` constituem o padrão canônico de descoberta de ambientes virtuais Python. Verificado em `https://peps.python.org/pep-0405/`.
- **Antigravity IDE Sandbox Model:** Ambientes de execução em sandbox restringem o acesso de filesystem ao workspace ativo, exigindo `BypassSandbox: true` para interagir com utilitários instalados em diretórios ancestrais (`~/.vitalia-spec-kit`).

