<!-- ADR-0004-dual-runtime-architecture-and-runner-inviolability.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 06:40(GMT-04:00) -->
> **ADR-0004-dual-runtime-architecture-and-runner-inviolability.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 06:40(GMT-04:00)**

# ADR-0004: Arquitetura Dual-Runtime por Domínio, Inviolabilidade do Hook Runner e Governança Anti-Loop de Sandbox

- **Status:** Proposto (Pausa HITL Soberana)
- **Data:** 11-11-2026
- **Autor:** Vitalia Architect (`/vitalia-architect`)
- **Feature:** `specs/005-runtime-discrepancy-and-dual-venv`
- **Fontes Canônicas:**
  - [`specs/005-runtime-discrepancy-and-dual-venv/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/research-brainstorming.md)
  - [`docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md)
  - [`docs/adr/ADR-0003-installer-preflight-isolated-venv-observability.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0003-installer-preflight-isolated-venv-observability.md)

---

## 1. Contexto e Problema

A entrega da Spec 004 blindou o ciclo de instalação (`kit-bootstrap.sh` e `install-project`) introduzindo um ambiente virtual isolado e puro em `${VITALIA_KIT_DIR}/.venv`. Contudo, a validação de uso prático na inicialização de sessões (`/vitalia-session-start`) revelou três falhas interligadas que provocavam erros de execução e tentativas reflexas de auto-reinstalação do kit por modelos de IA:

1. **Discrepância de Contratos nos Workflows:** Os 16 arquivos `.toml` em `source/extensions/` continuavam invocando `python3` genérico nos hooks `before` e prompts operacionais, ignorando o interpretador isolado do kit.
2. **Subprocessos Desvinculados em `vitalia_hook_runner.py`:** Mesmo disparado pelo executável do `.venv`, o `hook_runner` executava comandos de hooks via `subprocess.run(cmd, shell=True)` usando o `python3` resolvido pelo `$PATH` do shell ativo (herdando o Python global ou o ambiente do projeto local desprovido de `pyyaml`, `jinja2` e `jsonschema`).
3. **Fronteira de Isolamento de Sandbox e Reação Reflexa da IA:** No terminal da IDE Antigravity (modo sandbox padrão `BypassSandbox: false`), acessos a caminhos fora do workspace (`/home/andre/.vitalia-spec-kit`) falhavam com `No such file or directory` (código 127). Diante dessa mensagem, os modelos de IA erroneamente supunham ausência do kit e tentavam disparar reflexivamente `./kit-bootstrap.sh`.
4. **Conflacuação de Runtimes em `kit_env_bootstrap.py`:** O diagnóstico misturava o `.venv` do projeto com o do kit (`venv_ok = kit_venv_ok or proj_venv_ok`), mascarando falhas e impedindo a descoberta de ambientes virtuais com caminhos não-padronizados (Poetry, Pipenv, caminhos customizados).

---

## 2. Decisões Arquiteturais Estruturantes

### 2.1. Arquitetura Dual-Runtime Especializada por Domínio de Responsabilidade
Fica estritamente estabelecida a separação dos interpretadores Python em dois domínios inegociáveis:

1. **Runtime de Governança Interna do Kit (`{{KIT_PYTHON}}`):**
   - Mapeado diretamente para `${VITALIA_KIT_DIR}/.venv/bin/python3`.
   - Responsável exclusivo por 100% dos utilitários do kit: `vitalia_hook_runner.py`, `scan_environment.py`, `vitalia_context_engine.py`, `vitalia_handoff.py`, `guardian_context.py`, renderizadores de markdown e suíte de sensores VRSS.
   - **Garantia de Pureza:** Nunca depende de dependências instaladas no projeto cliente e nunca polui o projeto cliente com pacotes do kit.
2. **Runtime do Projeto do Usuário (`{{PROJECT_PYTHON}}`):**
   - Descoberto dinamicamente no início da sessão.
   - Reservado exclusivamente para tarefas, comandos e suítes de teste da aplicação do usuário (ex: `pytest` do projeto, migrações de banco, build).
   - **Fallback Dinâmico:** Se o projeto do usuário não possuir ambiente virtual próprio, adota fallback para `{{KIT_PYTHON}}` ou emite aviso diagnóstico orientativo.

### 2.2. Algoritmo de Descoberta em 4 Níveis (`project_runtime`)
O módulo `source/src/kit_env_bootstrap.py` implementa a função `find_project_python()` com resolução defensiva em cascata:
1. **Nível 1 (Shell Ativo):** Inspeciona a variável `$VIRTUAL_ENV`.
2. **Nível 2 (Configuração Local):** Inspeciona a chave `PROJECT_VENV_PATH` no `.env` da raiz do projeto.
3. **Nível 3 (Padrões Canônicos):** Varre pastas locais na raiz do projeto (`.venv`, `venv`, `env`, `.env_py`).
4. **Nível 4 (Resolução do Binário):** Localiza o binário executável (`bin/python3` ou `bin/python` em POSIX; `Scripts/python.exe` em Windows).

O diagnóstico emitido por `scan_environment.py` passa a conter nós independentes: `kit_runtime` e `project_runtime`.

### 2.3. Inviolabilidade do Hook Runner e Resolução Defensiva
- O módulo `vitalia_hook_runner.py` estende `resolve_placeholders` para suportar `{{KIT_PYTHON}}` e `{{PROJECT_PYTHON}}`.
- **Auto-Substituição Defensiva:** Antes de executar qualquer comando de hook via subprocesso, se a linha de comando iniciar com `python3 ` ou contiver referências diretas a scripts do kit, o runner substitui automaticamente `python3` por `sys.executable` (o interpretador real que instanciou o runner), blindando o processo contra desvios de `$PATH`.

### 2.4. Normalização Global de Workflows e Prompts
- Todos os 16 arquivos em `source/extensions/*.toml` têm seus hooks `before` atualizados para:
  `before = ["{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/hooks/scan_environment.py"]`
- Prompts operacionais que instruem comandos para a IA (`session-start`, `session-end`, `session-consolidate`, `brainstorming`, `route`) são atualizados para especificar `{{KIT_PYTHON}}` (ou `{{VITALIA_KIT_DIR}}/.venv/bin/python3`).
- Workflows voltados à aplicação (`spec-implement`, `spec-tasks`) orientam o uso contextual de `{{PROJECT_PYTHON}}`.

### 2.5. Governança Anti-Loop de Sandbox na IDE Antigravity
- Inclusão de regra mandatória em `source/AGENTS.md` e `source/integrations/antigravity/SKILL.md.template`:
  - Instruir que falhas de acesso a `${VITALIA_KIT_DIR}` (código 127) decorrem de isolamento de sandbox do terminal e exigem reexecução com `BypassSandbox: true`.
  - **Veto Absoluto de Auto-Reinstalação:** Proibir expressamente o modelo de invocar `kit-bootstrap.sh` por iniciativa própria quando uma ferramenta falhar.

---

## 3. Consequências e Trade-Offs

### Positivas
- **Isolamento Absoluto:** Elimina colisões de dependências entre projetos de clientes e as ferramentas internas do kit.
- **Resiliência a Ambientes Heterogêneos:** Suporte nativo a projetos com Poetry, Pipenv, Conda ou paths customizados.
- **Fim dos Loops de Reinstalação:** Modelos de IA não tentam reinstalar o kit global desnecessariamente.

### Neutras / Mitigações
- Exige que `vitalia_hook_runner.py` inspecione e substitua placeholders adicionais, mitigado com testes unitários rigorosos (`test_hook_runner_clean.py`).

