<!-- ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:43(GMT-04:00) -->
> **ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:43(GMT-04:00)**

# ADR-0001: Topologia Isolada em 4 Camadas, Lentes de Fase Sem Poda (`no_prune: true`) e Matriz Comportamental P05

- **Status:** Aceito (Soberania HITL)
- **Data:** 08-11-2026
- **Autor:** Vitalia Architect (`/vitalia-architect`)
- **Feature:** `specs/002-universal-bootstrap-runtime`
- **Fontes Canônicas:**
  - [`.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md)
  - [`specs/002-universal-bootstrap-runtime/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research-brainstorming.md)

---

## 1. Contexto e Problema

As tentativas anteriores de entrega das Specs 002 e 003 no repositório raiz apresentaram falhas críticas diagnosticadas empiricamente em máquina limpa (`WSL2/zsh`):
1. **Acoplamento com Infraestrutura Legada e Caminhos Fixos:** Presença residual de probes TCP para containers locais (Redis 6379, Postgres 5432), escrita de envelopes de Context Lifting em `~/.vitalia/tmp/` global e referências hardcoded a `~/.vitalia`.
2. **Diluição Constitucional por Poda de Contexto:** Perfis legados `gp_*.yaml` desenhados para GPUs locais de 6 GB VRAM cortavam princípios constitucionais (`total_budget: 350/1000/4000`) e truncavam aprendizados em `n=5`.
3. **Reescrita Cega vs. Espelhamento Sujo:** Na modularização de `install-project` e `vitalia_context_engine.py`, comportamentos funcionais estáveis de `~/.vitalia` foram amputados (`git clone --depth=1` substituído por `git init` vazio; dashboard multi-máquina rico substituído por markdown raso com datas ISO; criação de `.trash/` e `.vitalia-manifest` dentro de `.agents/skills/`, quebrando o indexador da Antigravity IDE).
4. **Falso Positivo por Testes Sintáticos Rasos:** Testes baseados apenas em `assert path.is_file()` aprovaram entregas que falhavam em execução real.

---

## 2. Decisões Arquiteturais Estruturantes

### 2.1. Isolamento Estrito em 4 Camadas Físicas e de Versionamento (P07, P11)
1. **Camada 1 — Repositório Raiz (`source/`):** Todo código-fonte do kit reside estritamente em `source/{bin,extensions,profiles,src,integrations,templates,AGENTS.md}`, acompanhado na raiz por `kit-bootstrap.sh`, `requirements.txt`, `specs/` e `tests/`.
2. **Camada 2 — Kit Instalado na Máquina Hospedeira (`VITALIA_KIT_DIR`, padrão `~/.vitalia-spec-kit`):** Instalado por `kit-bootstrap.sh` diretamente a partir de `source/` (sem o nível intermediário `source/`), abrigando o ambiente virtual isolado `${VITALIA_KIT_DIR}/.venv/bin/python3`.
3. **Camada 3 — Repositório Exclusivo de Contexto de Sessão (`.vitalia/memory/session/`):** Repositório Git separado contendo `shards/<machine_id>.yaml` (ordenados por `last_sync` decrescente em formato `DD-MM-YYYY HH:MM:SS(GMT-04:00)`), `data/{decisions,learnings,session_history}.jsonl` e dashboard `README.md`, mutado exclusivamente via `vitalia_context_engine.py` (Regra da Cerca Elétrica).
4. **Camada 4 — Repositório Exclusivo de Dados Operacionais (`.vitalia/memory/data_storage/`):** Repositório Git separado armazenando Context Lifting (`context/<machine_id>/`), handoffs (`handoffs/`) e pesquisas (`research/`).

### 2.2. Operação 100% Sem Poda em Todos os Workflows (`guardian_context.py` & 14 Lentes `gp_*.yaml` com `no_prune: true`)
- Todos os 16 workflows produzidos no kit novo operam incondicionalmente sem poda de contexto (`no_prune: true`, `total_budget: 0`, `hardware_profile: "frontier"`). O `guardian_context.py` elimina toda lógica legada de truncamento/filtragem por domínios, severidade ou orçamento de tokens, e todas as 14 lentes `gp_*.yaml` (incluindo `gp_session-start.yaml`, `gp_session-end.yaml` e `gp_session-consolidate.yaml`) injetam **100% dos 18 princípios da `constitution.yaml` (`P00`–`P17`)**, 100% das fontes `yaml_sources`, 100% do histórico de decisões e aprendizados (sem corte `n=5`) e adicionam `phase_guardrails` e `phase_profiles` específicos de cada etapa.

### 2.3. Engenharia Reversa em 3 Camadas e Matriz Comportamental P05 (4 Modalidades + Cenário de Falsificação)
- Toda migração a partir da referência funcional em `~/.vitalia` preserva a Camada 1 (Intenção de Negócio Pura), purga a Camada 2 (Redis, Celery, Ollama, `tmp/` global) e respeita a Camada 3 (Contrato do Consumidor: pureza 100% em `.agents/skills/`, pré-validação de `python3 -m venv`, suporte a `WSL2/zsh`).
- Todo teste automatizado é classificado em `[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]` ou `[TEST:MIGRATION]` com **Cenário de Falsificação executável** via `subprocess.run` em `tmp_path`, sendo bloqueadas (`BLOCK`) asserções puramente sintáticas (`assert path.is_file()`).

---

## 3. Consequências

- **Positivas:** Instalação limpa 100% reprodutível em qualquer estação Linux/WSL2 (`git clone` $\rightarrow$ `kit-bootstrap.sh` $\rightarrow$ `install-project`), zero dependência de Docker/Redis para operar o kit, governança constitucional integral em todas as fases e eliminação de falsos positivos na suíte `pytest`.
- **Trade-offs:** Exige que a suíte de testes execute subprocessos reais (`venv`, `git clone` contra repositórios bare locais, `vitalia_hook_runner.py`, `vitalia_context_engine.py`), aumentando o tempo de execução dos testes E2E em troca de fidelidade comportamental real.

