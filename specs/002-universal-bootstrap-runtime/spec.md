<!-- spec.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:41(GMT-04:00) -->
> **spec.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:41(GMT-04:00)**

# Especificação de Funcionalidade: Universal Bootstrap, Runtime Autônomo em 4 Camadas & Blindagem SDD

**Data:** 08-11-2026  
**Versão:** 0.0.1  
**Autor/Agente:** Vitalia SPEC Kit Architect & Requirements Engineer  
**Feature:** `specs/002-universal-bootstrap-runtime`  
**Status:** DRAFT (Submetido à Auditoria `/vitalia-judge --mode=specify` e Aprovação HITL)  
**Fontes Canônicas Obrigatórias:**
- [`.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md)
- [`specs/002-universal-bootstrap-runtime/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research-brainstorming.md)
- [`docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md)

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

### 1.1 Problema de Negócio e Engenharia
Desenvolvedores e pesquisadores que instalam o **Vitalia SPEC Kit** em uma máquina limpa (como uma estação Linux ou ambiente **WSL2 com shell zsh**) precisam que o kit funcione de ponta a ponta imediatamente após `git clone`, sem exigir containers locais (Redis, PostgreSQL, Ollama), sem sofrer podas de contexto herdadas de GPUs de 6 GB de VRAM e sem corromper o indexador de comandos da IDE Antigravity.

Nas iterações anteriores (descartadas via rollback ao commit `23bb91b` da Spec 001), cinco falhas críticas (`RCA-01` a `RCA-05`) impediram a operação real em máquina limpa:
1. **Testes Sintáticos Rasos (`RCA-01`):** A suíte de testes verificava apenas existência estática de arquivos, gerando falsos positivos enquanto o produto falhava em execução real.
2. **Omissão de Artefatos e Pré-Validação no Bootstrap (`RCA-02`):** O instalador não pré-validava a disponibilidade de ambiente virtual Python no host e omitia templates, instruções de agente e extensões.
3. **Caminhos Hardcoded (`RCA-03`):** Referências fixas a `~/.vitalia` impediam a escolha do diretório de instalação pelo usuário (padrão `~/.vitalia-spec-kit`).
4. **Violação do Contrato da IDE e Amputação de Clonagem Remota (`RCA-04`):** Arquivos ocultos e pastas de lixeira criados dentro de `.agents/skills/` quebravam a descoberta de slash commands na IDE Antigravity, e a lógica funcional de clonagem remota dos repositórios de sessão/dados foi substituída por inicializações vazias.
5. **Regressão no Motor de Sessão e Ordenação de Shards (`RCA-05`):** O motor de contexto perdeu a formatação temporal canônica `DD-MM-YYYY HH:MM:SS(GMT-04:00)`, a renderização rica do painel multi-máquina e exibia a estação ativa errada por ordenar shards alfabeticamente pelo nome do arquivo em vez do timestamp `last_sync` mais recente.

### 1.2 Declaração de Impacto ao Usuário e Validação Pré-Spec (Princípio P02)
- **Impacto Direto ao Usuário Final (Desenvolvedor/Pesquisador):** Reduz o tempo de ativação do kit em máquina limpa para menos de 2 minutos, elimina 100% dos falsos alertas de infraestrutura (`DEGRADED` por falta de Redis) e garante que todo o ciclo SDD (`/vitalia-session-start` $\rightarrow$ `/vitalia-brainstorming` $\rightarrow$ `/vitalia-route` $\rightarrow$ `/vitalia-architect` $\rightarrow$ `/vitalia-spec-specify` $\rightarrow$ `/vitalia-clarify` $\rightarrow$ `/vitalia-spec-plan` $\rightarrow$ `/vitalia-spec-tasks` $\rightarrow$ `/vitalia-task-verifier` $\rightarrow$ `/vitalia-analyze` $\rightarrow$ `/vitalia-spec-implement` $\rightarrow$ `/vitalia-converge` $\rightarrow$ `/vitalia-judge` $\rightarrow$ `/vitalia-session-end`) opere sob 100% da Constituição sem poda.
- **Multi-Tenancy e Isolamento por Projeto/Máquina:** Cada projeto hospedeiro isola seus envelopes de Context Lifting em `.vitalia/memory/data_storage/context/<machine_id>/` e cada estação grava seu próprio shard `.vitalia/memory/session/shards/<machine_id>.yaml` sem colisão entre máquinas.
- **RBAC e Mínimo Privilégio por Agente (P08):** Cada extensão declara estritamente suas ferramentas obrigatórias e opcionais, operando sob default-deny.
- **LGPD/HIPAA e Zero Data Leak (P07):** Nenhum payload de contexto é gravado em diretórios temporários globais compartilhados (`/tmp` ou `~/.vitalia/tmp/`); todos os artefatos de memória permanecem confinados ao projeto e bloqueados no `.gitignore` raiz.
- **Performance (Anti-N+1 / Latência):** A remoção de tentativas de conexão TCP/socket para Redis e Postgres elimina timeouts de rede a cada invocação de hook.
- **Segurança e Validação de Input (P06, P12):** Entradas de CLI e envelopes de handoff são validados estruturalmente contra schemas compatíveis com OpenAPI 3.0 limpo antes de qualquer mutação de estado.

---

## 2. Requisitos Funcionais

### FR-001: Topologia Estrita de 4 Camadas e Isolamento de Versionamento
O sistema **MUST** impor a separação física e lógica entre 4 camadas independentes:
1. **Camada 1 (Repositório Raiz):** Todo o código-fonte do kit **MUST** residir exclusivamente dentro de `source/` (`bin/`, `extensions/`, `profiles/`, `src/`, `integrations/`, `templates/`, `AGENTS.md`), acompanhado na raiz apenas por `kit-bootstrap.sh`, `requirements.txt`, `specs/`, `docs/`, `tests/` e `.gitignore`.
2. **Camada 2 (Kit Instalado na Máquina):** O instalador **MUST** materializar o conteúdo de `source/` diretamente no diretório escolhido pelo usuário (padrão `~/.vitalia-spec-kit`, persistido em `VITALIA_KIT_DIR`), sem o nível intermediário `source/`, incluindo o ambiente virtual isolado `.venv/`.
3. **Camada 3 (Repositório de Contexto de Sessão):** O diretório `.vitalia/memory/session/` **MUST** operar como repositório Git independente para estado de sessão, shards por máquina e aprendizados/decisões consolidados.
4. **Camada 4 (Repositório de Dados Operacionais):** O diretório `.vitalia/memory/data_storage/` **MUST** operar como repositório Git independente para envelopes de Context Lifting (`context/<machine_id>/`), handoffs (`handoffs/`) e pesquisas (`research/`).

### FR-002: Instalador Universal `kit-bootstrap.sh` com Pré-Validação de Ambiente
O instalador `kit-bootstrap.sh` na raiz do repositório **MUST**:
- Permitir que o usuário escolha interativamente o diretório de instalação (sugerindo `~/.vitalia-spec-kit` como padrão) ou receba o caminho de forma não-interativa via `--target-dir <path>` ou variável `VITALIA_KIT_DIR`, expandindo `~` para `${HOME}`.
- Pré-validar, **antes** de criar diretórios do kit, se o interpretador Python 3 e o módulo de criação de ambientes virtuais (`venv` / `ensurepip`) estão funcionais na máquina hospedeira; caso ausentes ou quebrados, o instalador **MUST** abortar imediatamente com código de saída diferente de zero e exibir instrução diagnóstica clara ao usuário.
- Criar o ambiente virtual isolado em `${VITALIA_KIT_DIR}/.venv`, instalar as dependências de `requirements.txt` e validar a importação real dos pacotes essenciais antes de concluir.
- Instalar 100% dos componentes de `source/` no destino (`bin/`, `bin/lib/` sem detector de Redis, `extensions/` com os 16 workflows, `profiles/` com os 6 catálogos e todas as 14 lentes `gp_*.yaml` cobrindo 100% dos workflows sem poda, `src/` com `core/`, `hooks/`, `rendering/`, `schemas/`, `templates/dashboard_template.md`, `integrations/antigravity/SKILL.md.template` e `AGENTS.md`).
- Gerar o executável `~/.local/bin/vitalia-install-project` exportando `VITALIA_KIT_DIR` dinamicamente para o diretório escolhido.

### FR-003: Ativador de Projeto `install-project` e Bibliotecas Modulares (`source/bin/lib/*`)
O ativador `source/bin/install-project` e suas bibliotecas modulares **MUST**:
- Operar exclusivamente para a IDE Antigravity, sem exibir perguntas sobre modo Redis-first ou clientes CLI legados, e sem incluir `redis_detector.sh`.
- **Invariante de Pureza de `.agents/skills/` (`agent_preserver.sh`):** Garantir que `.agents/skills/` contenha **exclusivamente** subdiretórios de skills (`vitalia-*/SKILL.md` ou skills customizadas do usuário). É **MUST NOT** criar arquivos ocultos (`.vitalia-manifest`) ou diretórios de backup/quarentena (`.trash/`) dentro de `.agents/skills/`; todo manifesto ou backup **MUST** ser armazenado em `.vitalia/`.
- **Preservação de Clonagem Remota e Inicialização Local (`git_storage_manager.sh`):** Quando o usuário ou o `.env` fornecer uma URL remota para `SESSION_REPO` ou `DATA_REPO`, o sistema **MUST** verificar a acessibilidade do repositório remoto e, caso contenha histórico acessível, clonar o repositório existente (`git clone --depth=1`); caso nenhuma URL seja fornecida ou o repositório remoto seja novo/vazio, o sistema **MUST** inicializar o repositório Git localmente (`git init`) com a estrutura base sem falhar.
- **Geração Completa de Skills:** Gerar `.agents/AGENTS.md` e `.agents/skills/vitalia-<workflow>/SKILL.md` para todas as 16 extensões canônicas instaladas, substituindo `{{VITALIA_KIT_DIR}}` pelo caminho real do kit instalado.
- **Persistência de Configuração (`env_manager.sh`):** Gravar e preservar `VITALIA_KIT_DIR`, `SESSION_REPO` e `DATA_REPO` no arquivo `.env` do projeto hospedeiro.

### FR-004: Descoberta de Ambiente e Inspeção de Saúde sem Containers (`kit_env_bootstrap.py` & `scan_environment.py`)
O módulo de resolução de ambiente e o hook de inspeção **MUST**:
- Resolver o diretório do kit instalado em 3 níveis de precedência determinística: (1) variável de ambiente `VITALIA_KIT_DIR`; (2) chave `VITALIA_KIT_DIR` no `.env` do projeto hospedeiro; (3) fallback padrão `~/.vitalia-spec-kit` (nunca `~/.vitalia`).
- Avaliar a saúde do projeto verificando exclusivamente: presença do `.env` do projeto, existência de `.agents/AGENTS.md`, pureza do diretório `.agents/skills/` e integridade do interpretador isolado `${VITALIA_KIT_DIR}/.venv/bin/python3`.
- **MUST NOT** testar portas TCP `6379` (Redis) ou `5432` (PostgreSQL) e **MUST NOT** reportar status `DEGRADED` pela ausência de containers Docker ou ambiente `.venv` na raiz do projeto hospedeiro.

### FR-005: Orquestrador de Hooks e Guardian 100% Sem Poda (`vitalia_hook_runner.py` & `guardian_context.py`)
O executor de hooks e o compilador de contexto Guardian (§11) **MUST**:
- Gravar todos os envelopes JSON de Context Lifting exclusivamente dentro do repositório de dados do projeto hospedeiro em `.vitalia/memory/data_storage/context/<machine_id>/<workflow>_<timestamp>_<hash>.json`, sendo **MUST NOT** gravar em `~/.vitalia/tmp/` ou `/tmp/` e **MUST NOT** injetar matrizes de limpeza `tmp_cleanup_matrix` nem publicar telemetria em Redis.
- **Invariante Incondicional de Contexto Sem Poda (Zero-Pruning Policy):** **Todos os 16 workflows produzidos no kit novo DEVEM trabalhar incondicionalmente sem poda de contexto (`no_prune: true`, `total_budget: 0`)**. O `guardian_context.py` **MUST** eliminar qualquer lógica ou adaptador legado de poda/truncamento por orçamento de tokens, domínios ou severidade, injetando **sempre 100% dos 18 princípios da `constitution.yaml` (`P00` a `P17`)** e **100% das fontes declaradas em `yaml_sources`** em todos os workflows sem exceção.
- Carregar 100% do histórico de `decisions.jsonl` e `learnings.jsonl` do repositório de sessão em todos os workflows, sem limite artificial de 5 itens (`n=5`).
- Injetar diretamente no `guardian_json` os blocos `phase_guardrails` e `phase_profiles` definidos na lente `gp_*.yaml` do workflow.
- Inspecionar os metadados temporais (`valid_until`) de `grounding_domains.yaml`, sinalizando no `guardian_json` caso algum domínio esteja expirado (`STALE`).

### FR-006: Motor de Sessão 3-Tier e Renderização Rica do Dashboard (`vitalia_context_engine.py`, `core/*` & `rendering/*`)
O motor de contexto **MUST** preservar todas as capacidades da arquitetura modular de referência em filesystem puro:
- **Integridade Temporal Canônica (P04):** Gerar todos os timestamps de sessão, shards, decisões, aprendizados e cabeçalhos estritamente no formato `DD-MM-YYYY HH:MM:SS(GMT-04:00)` (fuso `America/Cuiaba`), proibindo formatos ISO 8601 brutos nos artefatos de sessão.
- **Gestão e Ordenação Cronológica de Shards (`shard_manager.py`):** Persistir um arquivo YAML por estação em `.vitalia/memory/session/shards/<machine_id>.yaml` e **ordenar a lista de shards carregados em ordem decrescente do timestamp `last_sync`** (convertido cronologicamente, e não por ordem alfabética de nome de arquivo), garantindo que `shards[0]` — exibido como Estação Ativa em `SESSION_STATE.md` e em destaque no `README.md` — seja sempre a máquina que sincronizou mais recentemente.
- **Ações de Ciclo (`init`, `end`, `consolidate`):**
  - `--action init`: inicializar a árvore `.vitalia/memory/session/{data,shards,state}` de forma idempotente.
  - `--action end`: receber e persistir aprendizados (`--learnings-json`), decisões (`--decisions-json`) e histórico de sessão em `data/{learnings,decisions,session_history}.jsonl` com `machine_id` e data canônica, atualizar o shard YAML da estação atual e disparar a consolidação.
  - `--action consolidate`: renderizar `README.md` a partir de `templates/dashboard_template.md` (v0.0.1) com badges de status, diagrama Mermaid de topologia (com labels entre aspas duplas — P16), tabela HTML de máquinas, sessão ativa em destaque e blocos expansíveis `<details>` (Histórico Completo, Decisões Arquiteturais Consolidadas e Guard Rails de Grounding refletindo os 10 domínios canônicos), além das visões `SESSION_STATE.md`, `LEARNINGS.md`, `DECISIONS.md` e `SESSION_HISTORY.md`.

### FR-007: Handoff Inter-Agente Determinístico no Projeto Local (`vitalia_handoff.py`)
O utilitário de handoff **MUST**:
- Resolver a raiz do projeto hospedeiro via `resolve_project_root()` integrada à resolução dinâmica de `VITALIA_KIT_DIR`, ignorando `$HOME` e o próprio diretório do kit instalado.
- Criar, validar contra `schemas/vitalia-handoff-v1.0.0.json` e consumir atomicamente (via arquivo temporário + `os.replace`) os envelopes `handoff_<source>_to_<target>_<uuid8>.json` estritamente em `<project_root>/.vitalia/memory/data_storage/handoffs/`.

### FR-008: Catálogo Completo dos 16 Workflows Canônicos (`source/extensions/*.toml`) e Lentes de Fase Sem Poda (`source/profiles/gp_*.yaml`)
O produto **MUST** fornecer e validar os 16 workflows canônicos em `source/extensions/` (`session-start`, `spec-specify`, `judge`, `spec-plan`, `spec-tasks`, `task-verifier`, `spec-implement`, `analyze`, `converge`, `clarify`, `research`, `session-end`, `session-consolidate`, `brainstorming`, `route` e `architect`) e todas as 14 lentes correspondentes em `source/profiles/gp_*.yaml` (`gp_session-start`, `gp_session-end`, `gp_session-consolidate`, `gp_brainstorming`, `gp_vitalia-route`, `gp_architect`, `gp_research`, `gp_spec-specify`, `gp_spec-plan`, `gp_spec-tasks`, `gp_task-verifier`, `gp_analyze`, `gp_spec-implement` e `gp_sdd-judge`), cumprindo integralmente os contratos `AC-*` da Âncora:
- Todos os 16 `.toml` **MUST** trabalhar **100% sem poda de contexto**, declarando `version = "0.0.1"`, `hardware_profile = "frontier"`, `preferred = "filesystem"` em `[transport]` (sem chaves `redis` ou `redis_key`), `guardian_profile` apontando para uma lente `gp_*.yaml` existente em `source/profiles/` (zero warnings de arquivo ausente) e referenciando `{{VITALIA_KIT_DIR}}` (zero `~/.vitalia` hardcoded e zero menção ao script CLI legado `sdd_judge.py`).
- Todas as 14 lentes `gp_*.yaml` (cobrindo 100% dos 16 workflows, incluindo `gp_session-start.yaml`, `gp_session-end.yaml` e `gp_session-consolidate.yaml`) **MUST** declarar `no_prune: true`, `total_budget: 0`, `schema_version: "0.0.1"` e `hardware_profile: "frontier"`.
- Os workflows de verificação (`judge.toml`, `task-verifier.toml`, `analyze.toml`, `converge.toml`, `clarify.toml`) **MUST** impor o FMEA Mental em 4 questões (Ambiente Limpo, Anti-Shallow Testing P05, Regressão por Simplificação Indevida e Violação de Contrato do Consumidor), *Inverted Chain-of-Thought*, geração de relatório físico de inspeção e pausa obrigatória para aprovação humana (HITL soberano).

### FR-009: Perfis Constitucionais, Catálogos de Grounding/Questionamento e `source/AGENTS.md`
O diretório `source/profiles/` e o arquivo `source/AGENTS.md` **MUST** conter:
- `constitution.yaml`: 18 princípios (`P00` a `P17`), com `P05` instituindo a **Matriz Bidimensional de 4 Modalidades (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`)**, obrigatoriedade de **Cenário de Falsificação** e veto `BLOCKING` a asserções sintáticas isoladas.
- `grounding_domains.yaml`: os 10 domínios canônicos (`provedores_de_ia`, `python_packages`, `web_technologies`, `external_apis`, `security_practices`, `regulations_compliance`, `cloud_services`, `scientific_claims`, `clinical_safety`, `software_architecture`) com metadados de validade temporal (`last_verified_at`, `valid_until`, `validity_window_days`, `status`, `last_update_source`, `update_history`).
- `dynamic_questioning.yaml`: os 9 domínios socráticos canônicos livres de referências a Redis/Celery/Ollama/VRAM e com metadados temporais.
- `brainstorming_intents.yaml`: os 7 domínios semânticos estruturados (`estrategia_produto`, `arquitetura_software`, `engenharia_web_frontend`, `infraestrutura_devops`, `seguranca_compliance`, `educacao_workshop`, `saude_clinica`).
- `agents_catalog.yaml` e `routing_table.yaml`: sincronizados com os 16 workflows canônicos (incluindo `architect` e `research`) e mantendo os 5 especialistas verticais de domínio com `status: "planned"`.
- `source/AGENTS.md`: estruturado por Primacy e Recency conforme seção 6 da Parte I da Âncora.

---

## 3. Comportamentos Existentes a Preservar & Defeitos a Reproduzir (`AC-SPEC-04`)

Em conformidade com a Engenharia Reversa Funcional em 3 Camadas, esta especificação estabelece a fronteira exata entre o que deve ser preservado do código funcional de referência (`~/.vitalia` e commit `23bb91b`) e os defeitos que devem ser reproduzidos e corrigidos:

| ID | Componente | Comportamento Estável a Preservar (Camada 1) | Defeito / Acoplamento Legado a Reproduzir e Corrigir (Camadas 2 e 3) |
|---|---|---|---|
| **PRES-01 / BUG-01** | `kit-bootstrap.sh` | Criação automatizada de diretórios do kit, `.venv`, instalação de pacotes e geração do shim `~/.local/bin/vitalia-install-project`. | **Defeito (`RCA-02`):** Não pré-valida `python3 -m venv` antes de criar pastas e omitia `templates/`, `SKILL.md.template`, `AGENTS.md`, `analyze.toml`, `research.toml` e `gp_*.yaml`. |
| **PRES-02 / BUG-02** | `agent_preserver.sh` & `install-project` | Backup de agentes/skills pré-existentes do usuário e geração de `SKILL.md` a partir das extensões `.toml`. | **Defeito (`RCA-04a`):** Criava `.agents/skills/.trash/` e `.agents/skills/.vitalia-manifest` dentro de `.agents/skills/`, violando o contrato da Antigravity IDE. |
| **PRES-03 / BUG-03** | `git_storage_manager.sh` | Verificação de repositório remoto (`git ls-remote`) e clonagem rasa (`git clone --depth=1`) quando URL remota é fornecida, com fallback para `git init` local. | **Defeito (`RCA-04b`):** Na tentativa anterior da Spec 002, a clonagem remota foi amputada e trocada por um `git init` fixo que ignorava o histórico remoto. |
| **PRES-04 / BUG-04** | `vitalia_context_engine.py`, `shard_manager.py` & `dashboard_renderer.py` | Geração de `data/*.jsonl`, `shards/<machine_id>.yaml` com timestamps `DD-MM-YYYY HH:MM:SS(GMT-04:00)` e renderização completa do `README.md` rico via `dashboard_template.md`. | **Defeito (`RCA-05` + Bug `shards[0]`):** `shard_manager.py` carregava shards por ordem alfabética de arquivo (`sorted(glob("*.yaml"))`), fazendo `shards[0]` destacar uma máquina antiga (`17a6f667` de 03-11) em vez da mais recente (`eb10269b` de 07-11), além de acoplamento opcional com Redis e template com versão `v0.5.0` e lista antiga de domínios (`llm_models`). |
| **PRES-05 / BUG-05** | `vitalia_hook_runner.py` & `guardian_context.py` | Injeção polimórfica de `guardian_json`, leitura de handoff pendente, substituição de variáveis e emissão do Stub JSON. | **Defeito (`Pivôs 1, 2 e 3`):** Gravava envelopes em `~/.vitalia/tmp/`, tentava publicar telemetria em Redis (`No module named 'redis'`), injetava `tmp_cleanup_matrix`, mantinha lógica legada de poda condicional em `guardian_context.py`, podava a Constituição em `gp_session-start.yaml` (`total_budget: 350`, retornando apenas P01 e P11) e não possuía `gp_session-end.yaml` nem `gp_session-consolidate.yaml` em `profiles/`. |

---

## 4. Requisitos Não-Funcionais e Restrições Arquiteturais

- **RN-001 (Autonomia Zero-Container):** O kit **MUST** executar 100% de seus comandos, hooks e testes sem nenhum serviço externo em execução (zero Redis, zero PostgreSQL, zero Docker).
- **RN-002 (Compatibilidade POSIX / WSL2 / zsh / bash):** Todos os scripts shell (`kit-bootstrap.sh`, `install-project`, `source/bin/lib/*.sh`) **MUST** executar sem deadlocks de prompt interativo, sem colisão de `stderr` em subshells e com expansão segura de caminhos em ambientes Linux e WSL2 acionados a partir de `zsh` ou `bash`.
- **RN-003 (Contratos OpenAPI 3.0 Puros — P11):** Todo arquivo de schema JSON em `source/src/schemas/` ou `specs/002-universal-bootstrap-runtime/contracts/` **MUST** seguir estritamente o subset OpenAPI 3.0 limpo, sendo proibidos os meta-campos `$schema`, `title` na raiz do schema e `additionalProperties: false`.
- **RN-004 (Padronização de Cabeçalhos e Fuso Imutável — P04):** Todo arquivo criado ou modificado **MUST** conter o cabeçalho P04 (`<nome_arquivo> | Vitalia SPEC Kit v0.0.1 | DD-MM-YYYY HH:MM(GMT-04:00)`, duplo em Markdown) com fuso `GMT-04:00` (`America/Cuiaba`), atualizando também o texto de `P04` em `source/profiles/constitution.yaml` e de todos os artefatos de `source/` para `Vitalia SPEC Kit v0.0.1`.
- **RN-005 (Didática e Automação — P10):** 100% dos scripts Python executáveis via CLI em `source/src/` **MUST** responder à flag `--help` com descrição clara e exemplos de uso.

---

## 5. Histórias de Usuário (User Stories)

### US-001 [Prioridade: P1]: Bootstrap Universal e Instalação em Máquina Limpa (WSL2/zsh)
**Como um** Desenvolvedor configurando uma nova estação de trabalho (WSL2/zsh ou Linux),  
**eu quero** clonar o repositório `vitalia-spec-kit`, executar `./kit-bootstrap.sh` (escolhendo ou aceitando `~/.vitalia-spec-kit`) e ativar um projeto novo com `vitalia-install-project`,  
**para que** o kit crie seu próprio `.venv` isolado, instale todos os templates, extensões e lentes sem omissões e disponibilize todos os 16 slash commands nativamente na IDE Antigravity.

### US-002 [Prioridade: P1]: Pureza de `.agents/skills/` e Preservação de Clonagem Git Remota
**Como um** Engenheiro ativando o Vitalia SPEC Kit em um projeto novo ou existente,  
**eu quero** que o `install-project` mantenha `.agents/skills/` livre de arquivos ocultos/lixeiras e clone os repositórios remotos de sessão e dados quando URLs válidas forem informadas (ou inicialize repositórios locais quando vazio),  
**para que** o indexador da IDE reconheça imediatamente todas as skills e o contexto distribuído da equipe seja preservado.

### US-003 [Prioridade: P1]: Context Lifting Isolado e Governança Sem Poda (`no_prune: true`)
**Como um** Arquiteto conduzindo o ciclo SDD na IDE Antigravity,  
**eu quero** que cada comando `/vitalia-*` grave seu envelope de contexto em `.vitalia/memory/data_storage/context/<machine_id>/` e receba os 18 princípios da Constituição (`P00`–`P17`) mais os `phase_guardrails` da fase sem cortes de tokens e sem alertas de Redis,  
**para que** nenhuma regra constitucional seja diluída entre `/vitalia-session-start` e `/vitalia-session-end`.

### US-004 [Prioridade: P1]: Motor de Sessão 3-Tier Fiel com Destaque Cronológico Correto
**Como um** Desenvolvedor alternando entre múltiplas estações de trabalho,  
**eu quero** que o `vitalia_context_engine.py` registre aprendizados, decisões e shards com timestamps `DD-MM-YYYY HH:MM:SS(GMT-04:00)` e ordene as máquinas pelo `last_sync` mais recente ao renderizar `SESSION_STATE.md` e `README.md`,  
**para que** o painel do repositório `vitalia-spec-kit-context` destaque sempre a última estação ativa com fidelidade visual completa.

### US-005 [Prioridade: P2]: Suíte de Testes Comportamentais P05 Anti-Regressão
**Como um** Mantenedor do Vitalia SPEC Kit,  
**eu quero** uma suíte automatizada estruturada nas 4 modalidades da Matriz P05 (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`) com Cenários de Falsificação executados em subprocessos reais,  
**para que** regressões de runtime, omissões de bootstrap ou testes rasos sejam bloqueados antes de qualquer release.

---

## 6. Critérios de Aceite e Cenários Comportamentais (BDD Given/When/Then — `AC-SPEC-02`)

### Cenário 1 (`[TEST:NEW]` / `US-001`): Bootstrap Completo e Execução Isolada em Máquina Limpa
- **Dado** um diretório de instalação limpo parametrizado via `--target-dir` (ou `VITALIA_KIT_DIR`) em um ambiente sem `~/.vitalia` e sem containers Docker/Redis ativos,
- **Quando** o usuário executa `./kit-bootstrap.sh --target-dir <destino>` seguido de `<destino>/bin/install-project <projeto_novo>` em modo não-interativo,
- **Então** o instalador cria o `.venv` isolado capaz de importar `yaml`, `jinja2` e `jsonschema` com código de retorno `0`, instala todas as 16 extensões `.toml`, todas as 14 lentes `gp_*.yaml` sem poda e os templates no `<destino>`, e o `install-project` ativa o `<projeto_novo>` gerando `.agents/AGENTS.md` e as 16 skills funcionais.

### Cenário 2 (`[TEST:BUGFIX]` / `US-001` — `RCA-02`): Falha Segura na Pré-Validação de `python3 -m venv`
- **Dado** um ambiente hospedeiro onde o módulo `venv`/`ensurepip` do Python 3 está indisponível ou falha ao ser invocado,
- **Quando** o usuário executa `./kit-bootstrap.sh --target-dir <destino>`,
- **Então** o script aborta imediatamente com código de saída diferente de zero **antes** de instalar arquivos parciais no destino e exibe mensagem diagnóstica instruindo a instalação do pacote `python3-venv`.

### Cenário 3 (`[TEST:BUGFIX]` / `US-002` — `RCA-04a`): Invariante de Pureza do Contrato `.agents/skills/`
- **Dado** um projeto hospedeiro que já possui skills em `.agents/skills/` e é submetido a múltiplas execuções de `install-project`,
- **Quando** o diretório `.agents/skills/` é inspecionado após a ativação e preservação de agentes,
- **Então** 100% das entradas em `.agents/skills/` são exclusivamente diretórios de skills contendo `SKILL.md`, não existindo nenhum arquivo oculto (como `.vitalia-manifest`) nem diretório `.trash/` dentro de `.agents/skills/`.

### Cenário 4 (`[TEST:MIGRATION]` / `US-002` — `RCA-04b`): Clonagem Remota vs. Inicialização Local em `git_storage_manager.sh`
- **Dado** um repositório Git bare acessível contendo commits prévios de contexto (Caso A) ou um projeto novo sem URL remota informada (Caso B),
- **Quando** `git_storage_manager.sh` / `install-project` configura `.vitalia/memory/session/` e `.vitalia/memory/data_storage/`,
- **Então** no Caso A o repositório local é populado via `git clone --depth=1` preservando o commit remoto existente, e no Caso B é inicializado via `git init` local funcional, ambos retornando código `0`.

### Cenário 5 (`[TEST:MIGRATION]` & `[TEST:BUGFIX]` / `US-003`): Context Lifting em `data_storage/context/` e 100% dos Workflows Sem Poda
- **Dado** um projeto ativado com o novo kit sem Redis instalado,
- **Quando** `vitalia_hook_runner.py` é executado para todos os 16 workflows produzidos no kit novo (de `session-start.toml` a `session-end.toml`),
- **Então** o comando termina com código `0` em todos os 16 workflows sem emitir erro de Redis nem warning de `guardian_profile` ausente no `stderr`, grava o arquivo JSON de contexto dentro de `<projeto>/.vitalia/memory/data_storage/context/<machine_id>/` (nunca em `tmp/`), o `scan_environment.py` reporta status `HEALTHY` (ou `OK`), e o `guardian_json` resultante contém todos os 18 princípios (`P00`–`P17`) integralmente sem poda (`token_budget: 0`, `no_prune: true`) e sem `tmp_cleanup_matrix`.

### Cenário 6 (`[TEST:BUGFIX]` & `[TEST:MIGRATION]` / `US-004` — `RCA-05`): Ordenação Cronológica de Shards e Renderização do Dashboard Rico
- **Dado** um repositório `.vitalia/memory/session/` contendo o shard `17a6f667.yaml` (`last_sync: "03-11-2026 05:47:37(GMT-04:00)"`, estação `ai-control`) e o shard `eb10269b.yaml` (`last_sync: "07-11-2026 21:38:04(GMT-04:00)"`, estação `srv_master`),
- **Quando** `vitalia_context_engine.py --action consolidate` é executado,
- **Então** o motor ordena os shards por `last_sync` decrescente e destaca `srv_master` (`eb10269b`) como Estação Ativa tanto em `SESSION_STATE.md` quanto na seção `🎯 Sessão Ativa em Destaque` do `README.md`, renderizando todas as seções do `dashboard_template.md` v0.0.1 e os 10 domínios de `grounding_domains.yaml`.

---

## 7. Success Criteria (Critérios de Sucesso Mensuráveis e Observáveis em Caixa-Preta)

| ID | Critério de Sucesso Observável | Meta Mensurável |
|---|---|---|
| **SC-001** | Execução ponta a ponta de `kit-bootstrap.sh` $\rightarrow$ `install-project` $\rightarrow$ `vitalia_hook_runner.py` $\rightarrow$ `vitalia_handoff.py` $\rightarrow$ `vitalia_context_engine.py` em diretório limpo sem containers Docker/Redis ativos. | Código de saída `0` em 100% das etapas e zero erros de conexão Redis no `stderr`. |
| **SC-002** | Pureza contratual do diretório `.agents/skills/` após instalação e re-instalação idempotente sobre projeto com customizações. | `0` arquivos ocultos ou pastas `.trash` dentro de `.agents/skills/`; 16 diretórios `vitalia-*/SKILL.md` válidos. |
| **SC-003** | Operação 100% sem poda de contexto (Constituição integral, fontes YAML e histórico `decisions`/`learnings`) em todos os workflows produzidos no kit novo. | `18/18` princípios (`P00`–`P17`) presentes no `guardian_json` e `token_budget: 0` em `100%` dos 16 workflows do kit (`0` workflows com poda e `0` warnings de `gp_*.yaml` ausente). |
| **SC-004** | Isolamento de Context Lifting por projeto e por máquina (P07 Zero Data Leak). | `100%` dos envelopes de workflow gerados em `<project_root>/.vitalia/memory/data_storage/context/<machine_id>/`; `0` arquivos gerados em `tmp/` do kit. |
| **SC-005** | Fidelidade cronológica e visual da consolidação de sessão multi-máquina. | `100%` dos timestamps gerados no padrão `DD-MM-YYYY HH:MM:SS(GMT-04:00)` e estação com `last_sync` mais recente sempre selecionada em `shards[0]`. |
| **SC-006** | Cobertura comportamental da suíte de testes sob a Matriz P05 (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`). | `100%` dos testes executando comportamentos reais (subprocessos, CLI, mutação de estado e contratos) com `0` testes puramente sintáticos isolados. |

---

## 8. Modelos de Dados e Entidades (Dialeto OpenAPI 3.0 Puro — P11)

### 8.1 Envelope de Context Lifting (`.vitalia/memory/data_storage/context/<machine_id>/<workflow>_<ts>_<hash>.json`)
```yaml
type: object
required:
  - description
  - meta
  - transport
  - guardian
  - guardian_json
properties:
  description:
    type: string
  meta:
    type: object
    required:
      - version
      - hardware_profile
    properties:
      version:
        type: string
        enum: ["0.0.1"]
      hardware_profile:
        type: string
        enum: ["frontier"]
  transport:
    type: object
    required:
      - preferred
    properties:
      preferred:
        type: string
        enum: ["filesystem"]
  guardian_json:
    type: object
    required:
      - schema_version
      - workflow
      - timestamp
      - sources
      - phase_guardrails
      - session_context
      - context_decisions
      - context_learnings
    properties:
      schema_version:
        type: string
      workflow:
        type: string
      timestamp:
        type: string
        description: "Formato canônico DD-MM-YYYY HH:MM:SS(GMT-04:00)"
      sources:
        type: object
      phase_guardrails:
        type: object
      phase_profiles:
        type: object
      session_context:
        type: object
      context_decisions:
        type: array
        items:
          type: object
      context_learnings:
        type: array
        items:
          type: object
```

### 8.2 Relatório de Inspeção de Ambiente (`scan_environment.py`)
```yaml
type: object
required:
  - status
  - project_root
  - kit_dir
  - has_env
  - kit_venv_ok
  - skills_pure
  - issues
properties:
  status:
    type: string
    enum: ["HEALTHY", "DEGRADED"]
  project_root:
    type: string
  kit_dir:
    type: string
  has_env:
    type: boolean
  kit_venv_ok:
    type: boolean
  skills_pure:
    type: boolean
  issues:
    type: array
    items:
      type: string
```

---

## 9. Fora do Escopo (Out of Scope)

- **Ativação Executável dos 5 Especialistas Verticais de Domínio:** `Django-Stark`, `React-Vinci`, `Infra-Nomad`, `Cortex-Analyst` e `Figma-Maestro` permanecem registrados apenas como `status: "planned"` em `agents_catalog.yaml` (Pivô 6).
- **Extensões Auxiliares Legadas fora dos 16 Workflows Canônicos:** Os comandos `adr`, `blueprint-plan`, `blueprint-specify`, `continue`, `debug`, `integrative-review`, `medical-gate`, `pair`, `release`, `review`, `science-review` e `skill-evaluation` de `~/.vitalia` não fazem parte do pacote de 16 extensões canônicas de `source/extensions/`.
- **Criação de `~/.vitalia-spec-kit` na Estação Atual de Desenvolvimento:** Durante este turno, toda implementação ocorre em `source/`, `tests/`, `kit-bootstrap.sh` e `requirements.txt` do repositório local (e diretórios temporários isolados `tmp_path` do `pytest`), preservando `~/.vitalia` como toolchain da estação atual até o teste em máquina externa `WSL2/zsh`.

---

## 10. Suposições e Dependências

- **Sistema Operacional Alvo:** Distribuições Linux e Windows Subsystem for Linux (WSL2) com shells `zsh` ou `bash`, possuindo `git`, `python3` ($\ge 3.10$) e o módulo `venv` instalados no sistema operacional.
- **IDE Consumidora:** Antigravity IDE (v2.0+) com leitura automática de `.agents/AGENTS.md` e descoberta de slash commands via `.agents/skills/<name>/SKILL.md`.

---

## 11. Suposições Verificadas e Rastro de Grounding (Princípio P03 — `AC-SPEC-03`)

As suposições tecnológicas e contratuais abaixo foram verificadas empiricamente via Sub-Agente `vitalia-researcher` e inspeção direta com retorno HTTP 200 e leitura integral da documentação:

- **"Antigravity IDE Skills Discovery Contract (`.agents/skills/<name>/SKILL.md`)"**: verificado em `/home/andre/.gemini/antigravity/builtin/skills/agy-customizations/docs/skills.md` e `/home/andre/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md` em `08-11-2026` — confirma que cada skill reside em `.agents/skills/<skill-name>/SKILL.md` com frontmatter YAML (`name`, `description`), exigindo pureza do diretório `.agents/skills/`.
- **"Python Standard Library `venv` — Criação de Ambientes Virtuais Isolados e `ensurepip`"**: verificado em `https://docs.python.org/3/library/venv.html` (HTTP 200) em `08-11-2026` — confirma o comportamento de `python3 -m venv` e a dependência de `ensurepip` em distribuições Debian/Ubuntu/WSL2 (`python3-venv`).
- **"Dashboard Multi-Máquina Oficial (`vitalia-spec-kit-context`)"**: verificado em `https://raw.githubusercontent.com/andreticba/vitalia-spec-kit-context/main/README.md` (HTTP 200) em `08-11-2026` — confirma a estrutura exata renderizada por `dashboard_renderer.py` e `dashboard_template.md`.
- **"Inverted Chain-of-Thought e Mitigação de Viés em Avaliadores LLM-as-a-Judge"**: verificado em `https://arxiv.org/abs/2306.05685` (HTTP 200) em `08-11-2026` — fundamenta a exigência de evidências e crítica antes do veredito no `/vitalia-judge` e `/vitalia-task-verifier`.
- **"Critérios de Qualidade de Requisitos ISO/IEC/IEEE 29148:2018"**: verificado em `https://www.iso.org/standard/72089.html` (HTTP 200) em `08-11-2026` — fundamenta a estruturação não-ambígua, singular e mensurável dos requisitos `FR-001` a `FR-009` e `SC-001` a `SC-006`.
- **"Anthropic Managed Agents Architecture (Decoupling Brain, Hands, and Session)"**: verificado em `https://www.anthropic.com/engineering/managed-agents` e `https://platform.claude.com/docs/en/managed-agents/overview` em `07-11-2026` — fundamenta o isolamento da sessão fora da janela de contexto estática e o Context Lifting sob demanda.

