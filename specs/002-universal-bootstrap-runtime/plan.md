<!-- plan.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:52(GMT-04:00) -->
> **plan.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:52(GMT-04:00)**

# Implementation Plan: Universal Bootstrap, Runtime Autônomo em 4 Camadas & Blindagem SDD

**Branch**: `002-universal-bootstrap-runtime` | **Date**: 08-11-2026 | **Spec**: [`specs/002-universal-bootstrap-runtime/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/spec.md)

**Fontes Canônicas Obrigatórias (Single Source of Truth):**
1. [`.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md)
2. [`specs/002-universal-bootstrap-runtime/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research-brainstorming.md)
3. [`specs/002-universal-bootstrap-runtime/research.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research.md)
4. [`docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md)

---

## Summary

Consolidar no repositório local (`source/`, `kit-bootstrap.sh`, `requirements.txt` e `tests/`) o produto completo e autônomo do **Vitalia SPEC Kit (v0.0.1)** sob a **Topologia Estrita de 4 Camadas** (`source/` $\rightarrow$ `${VITALIA_KIT_DIR}` padrão `~/.vitalia-spec-kit` $\rightarrow$ `.vitalia/memory/session/` $\rightarrow$ `.vitalia/memory/data_storage/`), garantindo:
1. Instalação reprodutível em estação limpa (`WSL2/zsh` ou Linux) com pré-validação de `python3 -m venv` (`RCA-02`), pureza 100% em `.agents/skills/` (`RCA-04a`) e preservação de clonagem remota `git clone --depth=1` com fallback `git init` local em `git_storage_manager.sh` (`RCA-04b`);
2. Operação **100% sem poda de contexto (`no_prune: true`, `total_budget: 0`) em todos os 16 workflows produzidos no kit novo**, com eliminação de todos os algoritmos legados de poda em `guardian_context.py`, cobertura completa pelas 14 lentes `gp_*.yaml` (incluindo `gp_session-start.yaml`, `gp_session-end.yaml` e `gp_session-consolidate.yaml`) e gravação de Context Lifting exclusivamente em `.vitalia/memory/data_storage/context/<machine_id>/` (zero `tmp/` global e zero Redis);
3. Preservação integral do motor de contexto 3-Tier rico (`vitalia_context_engine.py`, `core/*`, `rendering/*`, `templates/dashboard_template.md`) com correção da ordenação cronológica de shards por `last_sync` decrescente (`RCA-05`), cabeçalhos P04 `Vitalia SPEC Kit v0.0.1` e suíte de testes comportamentais executáveis estruturada nas 4 modalidades da Matriz P05 (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`).

---

## Technical Context

- **Language/Version**: Python 3.11+ (compatível com Python 3.10–3.14+) e POSIX/Bash (`#!/usr/bin/env bash` compatível com invocação a partir de `zsh` e `bash` em Linux e WSL2)
- **Primary Dependencies**: `PyYAML>=6.0.1`, `Jinja2>=3.1.3`, `jsonschema>=4.21.1`, `pytest>=8.0.0` (instalados no `.venv` isolado do kit `${VITALIA_KIT_DIR}/.venv`; biblioteca padrão `tomllib`)
- **Storage**: Filesystem puro estruturado em 4 camadas (`JSON`, `JSONL`, `YAML`, `TOML`, `Markdown`) e repositórios Git isolados em `.vitalia/memory/session/` e `.vitalia/memory/data_storage/` (zero Redis, zero PostgreSQL, zero containers)
- **Testing**: `pytest` com execução real de subprocessos (`subprocess.run`) em diretórios isolados (`tmp_path`), repositórios Git bare locais e validação de contratos OpenAPI 3.0
- **Target Platform**: Estações de desenvolvimento Linux e Windows Subsystem for Linux 2 (`WSL2/zsh` e `bash`) integradas à **Antigravity IDE**
- **Project Type**: CLI Toolchain, Context Compiler & Multi-Agent SDD Governance Framework
- **Performance Goals**:
  - Execução de `vitalia_hook_runner.py` + `guardian_context.py` (sem poda) < 1.5s em filesystem local (`SC-001`, `SC-003`).
  - Execução de `vitalia_context_engine.py --action consolidate` < 1.0s para até 20 shards e 500 registros `.jsonl` (`SC-005`).
- **Constraints**:
  - **Restrição Soberana do Ambiente de Desenvolvimento:** Não criar `~/.vitalia-spec-kit` nesta máquina e não alterar `~/.vitalia` (toolchain congelado do turno atual); todo código produtivo é escrito estritamente em `source/`, `kit-bootstrap.sh`, `requirements.txt` e `tests/`, e todos os testes usam `tmp_path` parametrizado via `--target-dir` / `VITALIA_KIT_DIR`.
  - **Regra da Cerca Elétrica:** Jamais editar ou commitar diretamente em `.vitalia/memory/session/` fora do `vitalia_context_engine.py`.
  - **Cabeçalho P04:** Todo arquivo criado ou modificado deve exibir `Vitalia SPEC Kit v0.0.1` com fuso `GMT-04:00`.

---

## Constitution Check

Confronto integral contra os 18 princípios de `source/profiles/constitution.yaml` (`P00`–`P17` sem poda):

| Princípio | Severidade | Status | Evidência Técnica no Plano |
|---|---|---|---|
| **P00** (Purpose Arbiter) | BLOCKING | `PASS` | Foco em eliminar falhas silenciosas de bootstrap e perda de contexto entre estações de trabalho. |
| **P01** (SDD Pipeline Inviolability) | BLOCKING | `PASS` | Preserva e instala todos os 16 workflows canônicos do ciclo SDD completo. |
| **P02** (User-Centric Validation) | WARNING | `PASS` | Isolamento multi-máquina por `machine_id`, RBAC documentado nos catálogos e Zero Data Leak. |
| **P03** (External Verification / Grounding) | WARNING | `PASS` | Decisões técnicas fundamentadas em [`research.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research.md) com URLs oficiais verificadas (`HTTP 200` em `08-11-2026`). |
| **P04** (Timestamp & GMT-04:00 Integrity) | WARNING | `PASS` | Padronização de cabeçalhos `Vitalia SPEC Kit v0.0.1` e timestamps `DD-MM-YYYY HH:MM:SS(GMT-04:00)` em `core/utils.py` e `constitution.yaml`. |
| **P05** (Behavioral Falsification Matrix) | BLOCKING | `PASS` | Seções `Matriz de Migração` e `Test Depth Agreement (TDA)` abaixo mapeiam 100% dos componentes em `[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]` e `[TEST:MIGRATION]` com veto a `is_file()`. |
| **P06** (Secrets Never in Git) | BLOCKING | `PASS` | `.gitignore` protege `.env` e `.vitalia/`; nenhum segredo em código ou logs. |
| **P07** (Privacy & Zero Data Leak) | BLOCKING | `PASS` | Envelopes de Context Lifting gravados exclusivamente em `.vitalia/memory/data_storage/context/<machine_id>/` (fim de `~/.vitalia/tmp/`). |
| **P08** (Smart Routing & Min Privilege) | INFO | `PASS` | Sincronia estrita entre `brainstorming_intents.yaml`, `agents_catalog.yaml`, `routing_table.yaml` e as 16 extensões `.toml`. |
| **P09** (Medical Safety Gate) | BLOCKING | `PASS` | Preservado em `constitution.yaml`, `grounding_domains.yaml` (`clinical_safety`) e `brainstorming_intents.yaml` (`saude_clinica`). |
| **P10** (Didactics-First & `--help`) | WARNING | `PASS` | Todos os scripts CLI Python e Bash implementam `--help` didático validado por testes de caixa-preta. |
| **P11** (Hardware-Agnostic & OpenAPI 3.0) | BLOCKING | `PASS` | `VITALIA_KIT_DIR` dinâmico, `machine_id` via SHA256[:8], e schemas JSON em [`contracts/`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/contracts/) e `source/src/schemas/` em OpenAPI 3.0 limpo. |
| **P12** (Agent Security & Output Validation) | BLOCKING | `PASS` | Validação de schemas em handoffs (`vitalia_handoff.py`) e gates HITL soberanos nos `.toml`. |
| **P13** (API Safety Gate) | BLOCKING | `PASS` | Mantido em `constitution.yaml` e `grounding_domains.yaml`. |
| **P14** (Evidence Traceability) | BLOCKING | `PASS` | Persistência rastreável em `decisions.jsonl`, `learnings.jsonl` e `session_history.jsonl`. |
| **P15** (Observability & Logging) | WARNING | `PASS` | `logger.sh` em filesystem e `scan_environment.py` sem falsos positivos de Redis/Docker. |
| **P16** (Artifact Integrity & Mermaid) | WARNING | `PASS` | Ordenação cronológica reversa (`last_sync` decrescente) em `shard_manager.py` e labels Mermaid entre aspas duplas em `dashboard_renderer.py`. |
| **P17** (EU AI Act Compliance) | BLOCKING | `PASS` | Supervisão humana (HITL) e trilha documental completa antes da implementação. |

---

## Technical Decisions

Todas as decisões técnicas foram pesquisadas e verificadas com HTTP 200 em [`specs/002-universal-bootstrap-runtime/research.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research.md):

### Decisão 1: Isolamento de Ambiente Python via `venv` Nativo com Pré-Checagem em `kit-bootstrap.sh`
- **Escolhido**: `python3 -m venv` (`ensurepip`) em `${VITALIA_KIT_DIR}/.venv` com teste prévio em diretório temporário antes de criar `${VITALIA_KIT_DIR}`.
- **Verificado em**: https://docs.python.org/3/library/venv.html em 08-11-2026
- **Justificativa**: Evita violação da PEP 668 em Linux/WSL2 e impede instalações parciais quando `python3-venv` não está instalado na máquina hospedeira (`RCA-02`).
- **Alternativas**: `pip install --user` global (rejeitado por PEP 668/P11); `conda`/`poetry` (rejeitado por exigir binários externos).

### Decisão 2: Parser Nativo de Extensões `.toml` (`tomllib` + Fallback Seguro)
- **Escolhido**: `tomllib` da biblioteca padrão do Python 3.11+ em `vitalia_hook_runner.py` e `skill_generator.sh`.
- **Verificado em**: https://docs.python.org/3/library/tomllib.html em 08-11-2026
- **Justificativa**: Faz parse exato de strings multilinhas (`prompt = """..."""`) e tabelas `[guardian]`/`[transport]` sem dependências compiladas extras.
- **Alternativas**: `toml` legado (rejeitado por falta de manutenção); `grep`/`sed` puro (rejeitado por quebrar strings multilinhas).

### Decisão 3: Clonagem Rasa (`git clone --depth=1`) com Fallback `git init` em `git_storage_manager.sh`
- **Escolhido**: `git ls-remote "$repo_url" HEAD` $\rightarrow$ `git clone --depth=1` se houver histórico remoto, ou `git init -b main` se vazio/sem URL.
- **Verificado em**: https://git-scm.com/docs/git-clone em 08-11-2026
- **Justificativa**: Preserva o contexto distribuído existente entre estações (`RCA-04b`) enquanto permite ativar projetos novos em máquina limpa sem URL remota.
- **Alternativas**: `git init` fixo ignorando remoto (rejeitado por perda de histórico); exigir URL remota obrigatória (rejeitado por inviabilizar projetos locais novos).

### Decisão 4: Compilação de Contexto 100% Sem Poda (`Zero-Pruning Policy`) em Todos os 16 Workflows
- **Escolhido**: Remoção total dos algoritmos de poda por orçamento de tokens, domínios ou severidade em `guardian_context.py`, com 14 perfis `gp_*.yaml` declarando `no_prune: true`, `total_budget: 0` e `hardware_profile: "frontier"` para cobrir 100% dos 16 workflows.
- **Verificado em**: https://ai.google.dev/gemini-api/docs/models/gemini em 08-11-2026
- **Justificativa**: Modelos de fronteira possuem janela de 1M+ tokens; injetar sempre 100% da Constituição (`P00`–`P17`), 100% das fontes `yaml_sources` e 100% de `decisions.jsonl`/`learnings.jsonl` elimina diluição de governança em qualquer etapa do kit.
- **Alternativas**: Poda condicional em `session-start` (`total_budget: 350`, rejeitado por ordem explícita do usuário e perda de regras); remoção dos `gp_*.yaml` (rejeitado por perder `phase_guardrails`).

### Decisão 5: Renderização Rica do Dashboard 3-Tier via Jinja2 e Ordenação Cronológica de Shards (`PyYAML`)
- **Escolhido**: Arquitetura modular `core/*` + `rendering/*` + `templates/dashboard_template.md` com `Jinja2` e `PyYAML`, ordenando `ShardManager.load_all_shards()` por `parse_sync_time(shard.get("last_sync", ""))` decrescente.
- **Verificado em**: https://jinja.palletsprojects.com/en/stable/ e https://pyyaml.org/wiki/PyYAMLDocumentation em 08-11-2026
- **Justificativa**: Preserva o dashboard rico do repositório `vitalia-spec-kit-context` (`RCA-05`) e corrige o bug em que `shards[0]` selecionava `17a6f667` (`03-11-2026`) em vez de `eb10269b` (`07-11-2026`).
- **Alternativas**: Markdown minimalista concatenado (rejeitado por destruir o dashboard); ordenação por `mtime` de arquivo (rejeitado por falhar após `git clone`).

### Decisão 6: Contratos Estritos em Subset OpenAPI 3.0 Puro (`jsonschema`)
- **Escolhido**: Schemas JSON sem `$schema`, sem `title` raiz e sem `additionalProperties: false`, validados com `jsonschema`.
- **Verificado em**: https://spec.openapis.org/oas/v3.0.3.html e https://python-jsonschema.readthedocs.io/en/stable/ em 08-11-2026
- **Justificativa**: Garante compatibilidade total com compiladores de structured outputs de LLMs de fronteira (P11).
- **Alternativas**: JSON Schema Draft-07 com meta-campos (rejeitado por P11).

### Decisão 7: Suíte de Testes Comportamentais em Subprocessos Isolados (`pytest` + `tmp_path`)
- **Escolhido**: `pytest` executando subprocessos reais em `tmp_path` sob as 4 modalidades da Matriz P05 (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`).
- **Verificado em**: https://docs.pytest.org/en/stable/ em 08-11-2026
- **Justificativa**: Testa a execução real de caixa-preta sem poluir `~/.vitalia` nem criar `~/.vitalia-spec-kit` nesta máquina.
- **Alternativas**: Testes estáticos `is_file()` (rejeitado por P05).

---

## Matriz de Migração e Preservação Comportamental (`AC-PLAN-03`)

Mapeamento exaustivo de todos os componentes migrados/adaptados a partir da referência funcional (`~/.vitalia` e commit `23bb91b`) para `source/` e raiz do repositório:

| Componente Alvo em `source/` / Raiz | Comportamento Existente a Preservar (Camada 1 — Invariante de Negócio) | Acoplamento Legado / Defeito a Remover (Camada 2) | Contrato do Consumidor & Estratégia de Teste (`[TEST:MIGRATION]` / `[TEST:BUGFIX]`) |
|---|---|---|---|
| `kit-bootstrap.sh` & `requirements.txt` | Criação automatizada da árvore do kit instalado, `.venv` isolado, instalação de pacotes (`PyYAML`, `Jinja2`, `jsonschema`, `pytest`), injeção idempotente de `PATH`/`VITALIA_KIT_DIR` em `.bashrc`/`.zshrc` e geração do shim `~/.local/bin/vitalia-install-project`. | **Defeito (`RCA-02`):** Não pré-validava `python3 -m venv` antes de criar pastas; omitia `templates/`, `integrations/antigravity/SKILL.md.template`, `AGENTS.md`, `analyze.toml`, `research.toml` e as 14 lentes `gp_*.yaml`; usava `~/.vitalia` fixo como default. | Padrão `~/.vitalia-spec-kit` (parametrizável via `--target-dir` / `VITALIA_KIT_DIR`). Teste executa `kit-bootstrap.sh` em `tmp_path` e simula falha de `venv` para provar aborto limpo. |
| `source/bin/install-project` & `source/bin/lib/{logger,env_manager,agent_preserver,skill_generator}.sh` | Ativação de projeto hospedeiro, backup de customizações pré-existentes, persistência de `.env` (`VITALIA_KIT_DIR`, `SESSION_REPO`, `DATA_REPO`), atualização de `.gitignore` e geração de `.agents/AGENTS.md` + 16 `.agents/skills/vitalia-*/SKILL.md`. | **Defeito (`RCA-04a`):** `redis_detector.sh`, perguntas de modo Redis-first/CLI legado e criação de `.agents/skills/.trash/` e `.agents/skills/.vitalia-manifest` dentro de `.agents/skills/`. | **Pureza 100% em `.agents/skills/`:** manifesto salvo em `.vitalia/.vitalia-manifest` e backups em `.vitalia/backups/`. Teste executa `install-project` duas vezes sobre projeto com customizações e valida `0` itens ocultos em `.agents/skills/`. |
| `source/bin/lib/git_storage_manager.sh` | Verificação de repositório remoto (`git ls-remote`) e clonagem rasa (`git clone --depth=1`) quando URL remota possui commits, com fallback `git init -b main` quando vazio ou sem URL, mantendo `.git/info/exclude` / `.gitignore` isolados. | **Defeito (`RCA-04b`):** Na tentativa anterior da Spec 002, o `git clone --depth=1` foi amputado e substituído por `git init` fixo que ignorava o histórico remoto. | Teste cria repositório Git bare local com commit real, executa `git_storage_manager.sh` com a URL do bare repo e comprova que o commit remoto foi clonado, além de testar o fallback `git init` sem URL. |
| `source/src/kit_env_bootstrap.py` & `source/src/hooks/scan_environment.py` | Resolução dinâmica do diretório do kit e do `.venv` isolado; diagnóstico estruturado de saúde do ambiente antes dos workflows. | **Defeito (`Pivô 1`):** Fallback hardcoded para `~/.vitalia`, sondagem TCP das portas `6379` (Redis) e `5432` (PostgreSQL) e exigência de `.venv/` na raiz do projeto hospedeiro, gerando `status: "DEGRADED"`. | Precedência `os.environ["VITALIA_KIT_DIR"]` $\rightarrow$ `.env` do projeto $\rightarrow$ `~/.vitalia-spec-kit`. `scan_environment.py` retorna `HEALTHY`/`OK` sem Redis e sem `.venv` no projeto hospedeiro. |
| `source/src/vitalia_hook_runner.py` & `source/src/hooks/guardian_context.py` | Leitura de `.toml`, execução de hooks `before`/`after`, resolução de `model_profile` (`flash` $\rightarrow$ `gemini-3.6-flash`, `pro` $\rightarrow$ `gemini-3.1-pro-preview`), compilação do `guardian_json`, ingestão de handoffs pendentes e emissão do Stub JSON no `stdout`. | **Defeito (`Pivôs 1, 2 e 3`):** Escrita de envelopes em `~/.vitalia/tmp/`, publicação em Redis (`import redis`), injeção de `tmp_cleanup_matrix` e manutenção de adaptadores/lógica de poda em `guardian_context.py`. | Gravação exclusiva em `<project_root>/.vitalia/memory/data_storage/context/<machine_id>/<workflow>_<ts>_<hash>.json`. **Zero poda em 100% dos workflows:** `guardian_context.py` injeta sempre `18/18` princípios (`P00`–`P17`), 100% de `yaml_sources` e 100% de `decisions.jsonl`/`learnings.jsonl`. |
| `source/src/vitalia_context_engine.py`, `source/src/core/{context_engine,shard_manager,utils}.py`, `source/src/rendering/{dashboard_renderer,view_renderer,grounding_renderer,constitution_renderer}.py` & `source/templates/dashboard_template.md` | Ações `--action init|end|consolidate`, persistência de `data/{decisions,learnings,session_history}.jsonl`, escrita de `shards/<machine_id>.yaml`, timestamps `DD-MM-YYYY HH:MM:SS(GMT-04:00)` e renderização completa do `README.md` rico (badges, Mermaid com aspas duplas, tabela HTML de máquinas, sessão ativa em destaque e `<details>` expansíveis) + `SESSION_STATE.md`, `DECISIONS.md`, `LEARNINGS.md`, `SESSION_HISTORY.md`. | **Defeito (`RCA-05` + Bug `shards[0]`):** `ShardManager.load_all_shards()` ordenava `sorted(self.shards_dir.glob("*.yaml"))` por nome de arquivo (`17a6f667` de `03-11` antes de `eb10269b` de `07-11`), acoplamento opcional com Redis em `context_engine.py`, cabeçalhos `v0.5.0`/`v0.6.0` e lista antiga de domínios (`llm_models`) em `grounding_renderer.py`/`dashboard_template.md`. | `ShardManager.load_all_shards()` ordena por `parse_sync_time(shard.get("last_sync", ""))` decrescente (`shards[0]` = `eb10269b`). `grounding_renderer.py` e `dashboard_template.md` atualizados para `Vitalia SPEC Kit v0.0.1` e os 10 domínios canônicos. |
| `source/src/vitalia_handoff.py` & `source/src/schemas/vitalia-handoff-v1.0.0.json` | Subcomandos `create`, `pending`, `consume`, validação OpenAPI 3.0, escrita atômica (`os.replace`) e descoberta da raiz do projeto via `resolve_project_root()`. | Caminhos de fallback apontando para `~/.vitalia` e cabeçalho P04 antigo (`Vitalia SDD v0.6.0`). | Integração com `kit_env_bootstrap` (`VITALIA_KIT_DIR` / `~/.vitalia-spec-kit`) e cabeçalho P04 `Vitalia SPEC Kit v0.0.1`. |
| `source/extensions/*.toml` (16 workflows) & `source/profiles/gp_*.yaml` (14 lentes) | Prompts estruturados, FMEA Mental em 4 questões, *Inverted CoT*, Matriz P05, Engenharia Reversa em 3 Camadas, Grounding via Sub-Agente com rede e pausa HITL soberana. | `preferred = "redis"` em `session-*.toml`, menção a `sdd_judge` em `spec-tasks.toml`, poda `total_budget: 350` em `gp_session-start.yaml` e ausência de `gp_session-end.yaml` e `gp_session-consolidate.yaml`. | Todos os 16 `.toml` com `preferred = "filesystem"`, `version = "0.0.1"`, `hardware_profile = "frontier"`, `{{VITALIA_KIT_DIR}}` e todas as 14 lentes `gp_*.yaml` com `no_prune: true` e `total_budget: 0`. |
| `source/profiles/{constitution,grounding_domains,dynamic_questioning,brainstorming_intents,agents_catalog,routing_table}.yaml` & `source/AGENTS.md` | Governança P00–P17 (com Matriz P05), 10 domínios de grounding com validade temporal, 9 domínios de questionamento socrático, 7 domínios de intenções de brainstorming, catálogo de agentes/rotas e contrato `AGENTS.md`. | Regra `P04` em `constitution.yaml` mencionava `Vitalia SDD v0.6.0`; `source/profiles/` ainda estava na versão pré-calibração do commit `23bb91b`. | Sincronização completa em `source/profiles/` e `source/AGENTS.md` com cabeçalho e regra `P04` padronizados em `Vitalia SPEC Kit v0.0.1`. |

---

## Test Depth Agreement (TDA — Matriz Constitucional P05 — `AC-PLAN-04`)

Acordo vinculante de profundidade e falsificação de testes (sendo **bloqueada (`BLOCKING`)** qualquer tarefa de teste baseada apenas em `assert path.is_file()` ou regex estática sem execução comportamental):

| ID TDA | Componente / Escopo | Modalidade P05 | Profundidade Mínima Exigida & Método de Execução | Cenário de Falsificação Obrigatório (O que faz o teste falhar) |
|---|---|---|---|---|
| **TDA-01** | `kit-bootstrap.sh` (fluxo normal parametrizado) | `[TEST:NEW]` | Execução real via `subprocess.run` com `--target-dir <tmp_path>/kit --non-interactive` e `HOME=<tmp_path>/home`, seguida da invocação do `.venv/bin/python3` criado para importar `yaml`, `jinja2`, `jsonschema` e execução do shim `vitalia-install-project --help`. | Falha se o `.venv` não for funcional, se faltar qualquer um dos 16 `.toml`, 14 `gp_*.yaml`, `templates/dashboard_template.md`, `SKILL.md.template`, `AGENTS.md`, ou se o shim não resolver `VITALIA_KIT_DIR`. |
| **TDA-02** | `kit-bootstrap.sh` (pré-checagem `python3 -m venv` — `RCA-02`) | `[TEST:BUGFIX]` | Execução via `subprocess.run` injetando no `PATH` um wrapper de `python3` que simula falha em `-m venv` (`No module named venv`). | Falha se o script retornar `returncode == 0`, se deixar o diretório `<target_dir>` parcialmente criado ou se não exibir mensagem diagnóstica sobre `python3-venv`. |
| **TDA-03** | `install-project` & `agent_preserver.sh` (pureza de `.agents/skills/` — `RCA-04a`) | `[TEST:BUGFIX]` | Execução dupla de `install-project` em `<tmp_path>/project` contendo skills pré-existentes do usuário, inspecionando todas as entradas de `.agents/skills/`. | Falha se `.agents/skills/` contiver `.trash/`, `.vitalia-manifest`, qualquer arquivo oculto ou menos de 16 diretórios `vitalia-*/SKILL.md`. |
| **TDA-04** | `git_storage_manager.sh` (clone remoto vs init local — `RCA-04b`) | `[TEST:MIGRATION]` | Execução real contra (A) um repositório Git bare criado em `tmp_path` contendo um commit prévio e (B) um diretório sem URL remota. | Falha se no Caso A o commit do repositório bare não estiver presente no `git log` de `.vitalia/memory/session/` (provando que `git clone --depth=1` foi executado) ou se no Caso B o `git init` local falhar. |
| **TDA-05** | `kit_env_bootstrap.py` & `scan_environment.py` (saúde sem Redis/Docker) | `[TEST:BUGFIX]` & `[TEST:MIGRATION]` | Execução de `scan_environment.py` via subprocesso sobre projeto ativado em `tmp_path` sem Redis na porta 6379 e sem `.venv/` na raiz do projeto. | Falha se `status` for `"DEGRADED"`, se houver probe TCP em 6379/5432 ou se `kit_env_bootstrap` resolver `~/.vitalia` em vez de `VITALIA_KIT_DIR` / `~/.vitalia-spec-kit`. |
| **TDA-06** | `vitalia_hook_runner.py` & `guardian_context.py` (Context Lifting isolado + 100% dos 16 workflows sem poda) | `[TEST:MIGRATION]` & `[TEST:BUGFIX]` | Execução real de `vitalia_hook_runner.py` iterando sobre **todos os 16 arquivos `.toml`** em projeto isolado (`tmp_path`), lendo o envelope JSON gerado em `.vitalia/memory/data_storage/context/<machine_id>/`. | Falha se qualquer um dos 16 workflows retornar `returncode != 0`, emitir erro de Redis ou warning de `gp_*.yaml` ausente, gravar em `tmp/`, incluir `tmp_cleanup_matrix`, ter `token_budget != 0` ou contiver menos de 18 princípios (`P00`–`P17`) em `guardian_json.sources.constitution.principles`. |
| **TDA-07** | `vitalia_context_engine.py`, `shard_manager.py` & `dashboard_renderer.py` (ordenação `last_sync` + dashboard rico — `RCA-05`) | `[TEST:BUGFIX]` & `[TEST:MIGRATION]` | Execução real de `--action init`, `--action end` e `--action consolidate` em `tmp_path` populado com os shards `17a6f667.yaml` (`03-11-2026 05:47:37(GMT-04:00)`) e `eb10269b.yaml` (`07-11-2026 21:38:04(GMT-04:00)`). | Falha se `shards[0]` destacar `17a6f667` em vez de `eb10269b` em `SESSION_STATE.md` ou `README.md`, se houver timestamp ISO 8601 bruto, ou se `README.md` omitir o grafo Mermaid com aspas duplas, a tabela HTML de máquinas ou os 10 domínios de grounding. |
| **TDA-08** | `vitalia_handoff.py` & Contratos OpenAPI 3.0 (`schemas/*.json`, `profiles/*.yaml`, `--help` P10) | `[TEST:MIGRATION]` & `[TEST:NEW]` | Ciclo real `create` $\rightarrow$ `pending` $\rightarrow$ `consume` em subdiretório do projeto + validação `jsonschema` de todos os schemas/catálogos + execução de `--help` em todos os scripts Python/Bash. | Falha se qualquer schema contiver `$schema`, `title` raiz ou `additionalProperties: false`, se o handoff vazar para fora do projeto ou se qualquer CLI falhar em `--help`. |

---

## Project Structure

### Documentation (this feature)
```text
specs/002-universal-bootstrap-runtime/
├── research-brainstorming.md               # Síntese socrática + transcrição integral da Âncora (1.124 linhas)
├── regencia-architect-plano-turno.md       # Plano de regência técnica do Architect + auditoria P00–P17
├── spec.md                                 # Especificação funcional e comportamental aprovada
├── checklists/
│   └── requirements.md                     # Checklist de qualidade da spec (15/15)
├── Relatório de Inspeção - specify.md      # Veredito PASS do SDD-Judge (--mode=specify)
├── research.md                             # Decisões técnicas verificadas (HTTP 200) + Engenharia Reversa 3 Camadas
├── data-model.md                           # Modelo de dados das 4 camadas
├── quickstart.md                           # Guia executável de validação E2E (WSL2/zsh)
├── contracts/
│   ├── context-lifting-envelope.json       # Contrato OpenAPI 3.0 do envelope de Context Lifting
│   ├── guardian-profile.json               # Contrato OpenAPI 3.0 das 14 lentes gp_*.yaml sem poda
│   ├── grounding-domains.json              # Contrato OpenAPI 3.0 dos 10 domínios de grounding temporal
│   ├── vitalia-handoff-v1.0.0.json         # Contrato OpenAPI 3.0 do envelope de handoff
│   └── cli-contracts.md                    # Contratos públicos de CLI (Bash e Python)
├── plan.md                                 # Este plano técnico
└── Relatório de Inspeção - plan.md         # Relatório da auditoria /vitalia-judge --mode=plan
```

### Source Code (Repositório Raiz — Camada 1)
```text
vitalia-spec-kit/
├── kit-bootstrap.sh                        # Instalador universal (Camada 1 -> Camada 2, pré-checagem venv)
├── requirements.txt                        # PyYAML, Jinja2, jsonschema, pytest
├── docs/
│   └── adr/
│       └── ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md
├── source/
│   ├── AGENTS.md                           # Contrato global da IA (Primacy & Recency v0.0.1)
│   ├── bin/
│   │   ├── install-project                 # Orquestrador de ativação de projeto hospedeiro
│   │   └── lib/
│   │       ├── logger.sh                   # Logging estruturado POSIX sem colisão de stderr
│   │       ├── env_manager.sh              # Gestão idempotente de .env (VITALIA_KIT_DIR, SESSION_REPO, DATA_REPO)
│   │       ├── git_storage_manager.sh      # git ls-remote -> git clone --depth=1 ou git init local
│   │       ├── agent_preserver.sh          # Backup em .vitalia/backups/ (pureza 100% em .agents/skills/)
│   │       └── skill_generator.sh          # Compilador de .toml -> .agents/skills/vitalia-*/SKILL.md
│   ├── extensions/                         # 16 Workflows Canônicos (100% filesystem e 100% sem poda)
│   │   ├── analyze.toml
│   │   ├── architect.toml
│   │   ├── brainstorming.toml
│   │   ├── clarify.toml
│   │   ├── converge.toml
│   │   ├── judge.toml
│   │   ├── research.toml
│   │   ├── route.toml
│   │   ├── session-consolidate.toml
│   │   ├── session-end.toml
│   │   ├── session-start.toml
│   │   ├── spec-implement.toml
│   │   ├── spec-plan.toml
│   │   ├── spec-specify.toml
│   │   ├── spec-tasks.toml
│   │   └── task-verifier.toml
│   ├── integrations/
│   │   └── antigravity/
│   │       └── SKILL.md.template           # Template de skill da Antigravity IDE
│   ├── profiles/                           # 6 Catálogos + 14 Lentes gp_*.yaml (100% no_prune: true, total_budget: 0)
│   │   ├── agents_catalog.yaml
│   │   ├── brainstorming_intents.yaml
│   │   ├── constitution.yaml
│   │   ├── dynamic_questioning.yaml
│   │   ├── grounding_domains.yaml
│   │   ├── routing_table.yaml
│   │   ├── gp_analyze.yaml
│   │   ├── gp_architect.yaml
│   │   ├── gp_brainstorming.yaml
│   │   ├── gp_research.yaml
│   │   ├── gp_sdd-judge.yaml
│   │   ├── gp_session-consolidate.yaml
│   │   ├── gp_session-end.yaml
│   │   ├── gp_session-start.yaml
│   │   ├── gp_spec-implement.yaml
│   │   ├── gp_spec-plan.yaml
│   │   ├── gp_spec-specify.yaml
│   │   ├── gp_spec-tasks.yaml
│   │   ├── gp_task-verifier.yaml
│   │   └── gp_vitalia-route.yaml
│   ├── templates/
│   │   └── dashboard_template.md           # Template Jinja2 rico do README.md de sessão (v0.0.1)
│   └── src/
│       ├── kit_env_bootstrap.py            # Descoberta de VITALIA_KIT_DIR e re-execução no .venv isolado
│       ├── vitalia_hook_runner.py          # Executor de hooks e Context Lifting em data_storage/context/
│       ├── vitalia_context_engine.py       # Entrypoint CLI do motor 3-Tier (init, end, consolidate)
│       ├── vitalia_handoff.py              # CLI de handoff determinístico inter-agente
│       ├── core/
│       │   ├── __init__.py
│       │   ├── context_engine.py           # Orquestrador 3-Tier em filesystem puro
│       │   ├── shard_manager.py            # Gestão de shards ordenada por last_sync decrescente
│       │   └── utils.py                    # get_timestamp() GMT-04:00, get_machine_id(), format_visible_header()
│       ├── hooks/
│       │   ├── __init__.py
│       │   ├── guardian_context.py         # Compilador Guardian 100% sem poda + checagem valid_until
│       │   ├── domain_detector.py          # Detector determinístico de domínios de grounding
│       │   └── scan_environment.py         # Inspeção de saúde sem Redis/Postgres/Docker
│       ├── rendering/
│       │   ├── __init__.py
│       │   ├── dashboard_renderer.py       # Renderizador Jinja2 do README.md multi-máquina
│       │   ├── view_renderer.py            # Renderizador de SESSION_STATE, DECISIONS, LEARNINGS, HISTORY
│       │   ├── grounding_renderer.py       # Renderizador dos 10 domínios de grounding
│       │   └── constitution_renderer.py    # Renderizador de princípios constitucionais
│       └── schemas/
│           ├── agents_catalog.schema.json
│           ├── brainstorming_intents.schema.json
│           ├── constitution.schema.json
│           ├── context-lifting-envelope.schema.json
│           ├── dynamic_questioning.schema.json
│           ├── grounding_domains.schema.json
│           ├── guardian_profile.schema.json
│           ├── routing_table.schema.json
│           └── vitalia-handoff-v1.0.0.json
└── tests/
    ├── test_bootstrap_and_install.py       # TDA-01, TDA-02, TDA-03, TDA-04
    ├── test_runtime_and_guardian.py        # TDA-05, TDA-06 (16 workflows sem poda + Context Lifting)
    ├── test_context_engine_3tier.py        # TDA-07 (ordenação last_sync + dashboard rico)
    └── test_contracts_and_handoff.py       # TDA-08 (OpenAPI 3.0, handoff, --help P10)
```

---

## Phase Overview

### Phase 1: Setup & Contratos Base (OpenAPI 3.0, `requirements.txt`, `source/AGENTS.md`)
- Atualizar `requirements.txt`, `source/AGENTS.md` (P04 `Vitalia SPEC Kit v0.0.1`) e os schemas OpenAPI 3.0 limpos em `source/src/schemas/`.

### Phase 2: Foundational — Catálogos YAML, 14 Lentes `gp_*.yaml` Sem Poda e 16 Workflows `.toml`
- Sincronizar os 6 catálogos em `source/profiles/` (`constitution.yaml` com `P04` atualizado para `Vitalia SPEC Kit v0.0.1` e `P05` Matriz de 4 Modalidades, `grounding_domains.yaml` com 10 domínios, `dynamic_questioning.yaml` com 9 domínios, `brainstorming_intents.yaml` com 7 domínios, `agents_catalog.yaml` e `routing_table.yaml`).
- Consolidar todas as 14 lentes `source/profiles/gp_*.yaml` (incluindo `gp_session-start.yaml`, `gp_session-end.yaml` e `gp_session-consolidate.yaml`) com `no_prune: true`, `total_budget: 0`, `schema_version: "0.0.1"` e `hardware_profile: "frontier"`.
- Consolidar os 16 workflows canônicos em `source/extensions/*.toml` com `preferred = "filesystem"`, `version = "0.0.1"`, `hardware_profile = "frontier"`, `{{VITALIA_KIT_DIR}}` e remoção dos `.toml` legados fora de escopo.

### Phase 3: User Story 1 & 2 (`US-001`, `US-002`) — Bootstrap Universal e Ativador de Projeto (`kit-bootstrap.sh`, `install-project`, `source/bin/lib/*`)
- Escrever os testes `[TEST:NEW]`, `[TEST:BUGFIX]` e `[TEST:MIGRATION]` em `tests/test_bootstrap_and_install.py` (confirmando Red Phase).
- Implementar `kit-bootstrap.sh` (pré-checagem `python3 -m venv`, default `~/.vitalia-spec-kit`, cópia integral de `source/`), `source/bin/install-project` e `source/bin/lib/{logger,env_manager,git_storage_manager,agent_preserver,skill_generator}.sh` (preservando `git clone --depth=1` e garantindo pureza 100% em `.agents/skills/`).

### Phase 4: User Story 3 (`US-003`) — Descoberta de Ambiente, Hook Runner e Guardian 100% Sem Poda
- Escrever os testes `[TEST:BUGFIX]` e `[TEST:MIGRATION]` em `tests/test_runtime_and_guardian.py` (confirmando Red Phase).
- Implementar `source/src/kit_env_bootstrap.py`, `source/src/hooks/scan_environment.py`, `source/src/hooks/domain_detector.py`, `source/src/hooks/guardian_context.py` (100% sem poda em todos os workflows + inspeção de `valid_until`) e `source/src/vitalia_hook_runner.py` (gravando exclusivamente em `<project_root>/.vitalia/memory/data_storage/context/<machine_id>/` sem Redis e sem `tmp_cleanup_matrix`).

### Phase 5: User Story 4 (`US-004`) — Motor de Sessão 3-Tier Rico e Ordenação Cronológica de Shards
- Escrever os testes `[TEST:BUGFIX]` e `[TEST:MIGRATION]` em `tests/test_context_engine_3tier.py` (confirmando Red Phase para `shards[0]` com `17a6f667` vs `eb10269b`).
- Portar e higienizar `source/src/vitalia_context_engine.py`, `source/src/core/{context_engine,shard_manager,utils}.py`, `source/src/rendering/{dashboard_renderer,view_renderer,grounding_renderer,constitution_renderer}.py` e `source/templates/dashboard_template.md`, ordenando shards por `parse_sync_time(last_sync)` decrescente.

### Phase 6: User Story 5 (`US-005`) — Handoff Determinístico, Contratos OpenAPI 3.0 e Polimento P04/P10
- Escrever e validar `tests/test_contracts_and_handoff.py` (`TDA-08`), higienizar `source/src/vitalia_handoff.py`, auditar cabeçalhos P04 (`Vitalia SPEC Kit v0.0.1`) e `--help` em 100% dos scripts de `source/` e remover arquivos obsoletos residuais de `source/src/` (como `sdd_judge.py` ou `telemetry_worker.py` se existirem).

