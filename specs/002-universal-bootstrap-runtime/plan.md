<!-- plan.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:10(GMT-04:00) -->
> **plan.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:10(GMT-04:00)**

# Plano de Implementação Técnica — Spec 002: Universal Bootstrap & Runtime

* **Branch:** `main` (ou branch dedicada `feature/002-universal-bootstrap-runtime`)
* **Data:** 04-11-2026 20:10(GMT-04:00)
* **Especificação de Referência:** [specs/002-universal-bootstrap-runtime/spec.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/spec.md)
* **Pesquisa Técnica:** [specs/002-universal-bootstrap-runtime/research.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research.md)
* **Contratos OpenAPI 3.0:** [contracts/](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/contracts/)
* **Guia de Validação Rápida:** [quickstart.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/quickstart.md)

---

## 1. Sumário Executivo

Este plano técnico estabelece a arquitetura e a decomposição de engenharia para transformar o repositório **vitalia-spec-kit** em um produto autônomo, distribuível e instalável via `git clone`, desvinculando-o integralmente de containers locais (Redis/Postgres), podas artificiais de VRAM e dependências do caminho legado `~/.vitalia/`.

A abordagem técnica consiste em:
1. Criar um instalador universal idempotente (`kit-bootstrap.sh`) que configura um interpretador isolado em `~/.vitalia-spec-kit/.venv/` com shims em `~/.local/bin/`.
2. Refatorar os utilitários de diagnóstico e orquestração (`scan_environment.py`, `vitalia_hook_runner.py`) para operar 100% sobre o sistema de arquivos local, direcionando o Context Lifting para `.vitalia/memory/data_storage/context/`.
3. Saneamento e padronização contratual dos 12 arquivos `.toml` em `source/extensions/`, eliminando códigos mortos de telemetria e limites de hardware obsoletos.
4. Formalizar a governança da nova marca **`Vitalia SPEC Kit v0.0.1`** e fuso horário imutável `America/Cuiaba (GMT-04:00)`.

---

## 2. Contexto Técnico e Restrições

* **Linguagem & Interpretador Base:** Shell Script (Bash v4+) para bootstrap; Python 3.10+ para runtime dos hooks e utilitários.
* **Ambiente de Runtime:** `~/.vitalia-spec-kit/.venv/` (isolamento de dependências PEP 668).
* **Dependências Primárias:** `pyyaml>=6.0`, `jinja2>=3.1.0`, `click>=8.1.0` (zero bibliotecas pesadas de banco ou containers).
* **Armazenamento de Dados:** Filesystem local puro:
  - Repositório Transitório do Projeto: `.vitalia/memory/data_storage/` (protegido por `.gitignore`).
  - Repositório de Sessão Compartilhado: `.vitalia/memory/session/` (Git distribuído particionado por `machine_id`).
* **Estratégia de Testes (P05):**
  - Módulos novos: TDD Red Phase.
  - Módulos refatorados: Characterization Tests (Golden Master) garantindo equivalência e pureza.
* **Plataforma Alvo:** POSIX (Linux x86_64/arm64 e macOS).
* **Tipo do Projeto:** Developer Tooling & Agentic SDD Runtime Kit.
* **Metas de Performance:** Bootstrap completo em < 60 segundos; Context Lifting em < 1.500 ms.
* **Restrições:** Proibido uso de `sudo`, proibido requisito de daemon Docker, proibida escuta em portas de rede TCP.

---

## 3. Avaliação de Conformidade Constitucional (Constitution Check)

| Princípio | Descrição da Regra | Como o Plano Atende | Status |
|---|---|---|:---:|
| **P00 (PURPOSE)** | Human Wellbeing First | Elimina dependências que causam atrito de instalação e falhas intermitentes de container | ✅ APROVADO |
| **P01 (GOVERNANCE)** | SDD Pipeline Inviolability | Nenhuma linha de código será escrita até que o `tasks.md` seja formalmente aprovado | ✅ APROVADO |
| **P02 (GOVERNANCE)** | User-Centric Validation | User Stories focadas em idempotência, proteção de código e portabilidade | ✅ APROVADO |
| **P03 (GROUNDING)** | External Verification | 6 decisões técnicas fundamentadas com fontes autoritativas em `research.md` | ✅ APROVADO |
| **P04 (INFRASTRUCTURE)** | Timestamp & GMT-04:00 | Padronização mandatória de cabeçalhos duplos `Vitalia SPEC Kit v0.0.1` | ✅ APROVADO |
| **P05 (GOVERNANCE)** | Test-First Development | Estratégia bifurcada formalizada (TDD para bootstrap; Characterization para refatoração) | ✅ APROVADO |
| **P06 (SECRETS)** | Secrets Never in Git | Nenhuma credencial em código; `.env` puramente local e variáveis de ambiente | ✅ APROVADO |
| **P07 (PRIVACY)** | Zero Data Leak / Local Vault | Context Lifting reside no disco do projeto, estritamente ignorado pelo git da aplicação | ✅ APROVADO |
| **P11 (AGNOSTICISM)** | Clean Schemas & Machine ID | Schemas OpenAPI 3.0 puros e derivação de `machine_id` via SHA-256 de hostname | ✅ APROVADO |

---

## 4. Estrutura do Projeto

### 4.1 Documentação (Nesta Feature)
```
specs/002-universal-bootstrap-runtime/
├── spec.md                                      # Especificação funcional ISO 29148
├── research.md                                  # Pesquisa técnica e decisões fundamentadas
├── plan.md                                      # Este plano de implementação técnica
├── quickstart.md                                # Guia executável de validação
├── checklists/
│   └── requirements.md                          # Validação de qualidade de requisitos
├── contracts/
│   ├── context-lifting.schema.json              # Contrato OpenAPI 3.0 para elevação de contexto
│   └── scan-environment.schema.json            # Contrato OpenAPI 3.0 para diagnóstico
└── Relatório de Inspeção - specify.md           # Parecer do SDD-Judge
```

### 4.2 Código Fonte e Arquivos Afetados no Repositório
```
vitalia-spec-kit/
├── kit-bootstrap.sh                             # [NOVO] Instalador universal idempotente
├── requirements.txt                             # [NOVO] Dependências mínimas do runtime
├── source/
│   ├── bin/
│   │   └── install-project                      # Utilitário de setup no projeto do usuário
│   ├── src/
│   │   ├── vitalia_hook_runner.py               # [REFATORAR] Context lifting em disco e purga de Redis
│   │   ├── vitalia_context_engine.py            # [REFATORAR] Consolidação em filesystem puro
│   │   ├── hooks/
│   │   │   └── scan_environment.py             # [REFATORAR] Diagnóstico sem checagem de portas TCP
│   │   └── core/
│   │       └── guardian.py                      # [REFATORAR] Injeção de contexto holístico sem podas
│   ├── profiles/
│   │   ├── constitution.yaml                    # [ATUALIZAR] Versão v0.0.1 e princípios integrados
│   │   ├── routing_table.yaml                   # [ATUALIZAR] Registro do vitalia-architect
│   │   └── brainstorming_intents.yaml           # [ATUALIZAR] target_agent e command
│   └── extensions/
│       ├── architect.toml                       # [NOVO] Extensão oficial do Tech Lead
│       ├── session-start.toml                   # [ATUALIZAR] Purga de Redis e profile frontier
│       ├── spec-specify.toml                    # [ATUALIZAR] Inclusão de research-brainstorming.md
│       ├── judge.toml                           # [ATUALIZAR] Inverted CoT e ausência de CLI legado
│       ├── spec-plan.toml                       # [ATUALIZAR] Validação de contratos OpenAPI 3.0
│       ├── spec-tasks.toml                      # [ATUALIZAR] Estratégia de testes bifurcada
│       ├── spec-implement.toml                  # [ATUALIZAR] Consumo de contexto local
│       ├── converge.toml                        # [ATUALIZAR] Auditoria 4D na IDE
│       ├── session-end.toml                     # [ATUALIZAR] Gravação com machine_id
│       ├── session-consolidate.toml             # [ATUALIZAR] Deduplicação e pure views
│       ├── brainstorming.toml                   # [ATUALIZAR] Handoff forward para route
│       └── route.toml                           # [ATUALIZAR] Despacho para architect
└── .vitalia/
    └── feature.json                             # Apontador da feature ativa
```

---

## 5. Fases de Execução Técnica

### Fase 1: Setup da Topologia e Bootstrap Idempotente
* **Objetivo:** Estabelecer o mecanismo de instalação do produto em qualquer máquina sem dependência prévia.
* **Entregáveis:**
  - Script `kit-bootstrap.sh` na raiz:
    - Criação de `~/.vitalia-spec-kit/`.
    - Inicialização idempotente do ambiente virtual isolado `.venv/` via `python3 -m venv`.
    - Instalação das dependências a partir de `requirements.txt`.
    - Criação de shims idempotentes em `~/.local/bin/`.
  - Arquivo `requirements.txt` com as dependências essenciais fixadas.

### Fase 2: Runtime Isolado e Desacoplamento de Infraestrutura
* **Objetivo:** Refatorar os motores centrais em `source/src/` eliminando toda dependência de containers locais.
* **Entregáveis:**
  - `source/src/hooks/scan_environment.py`: purgar sockets TCP nas portas `6379` e `5432`; avaliar apenas `.env`, `.agents/` e integridade do interpretador isolado.
  - `source/src/vitalia_hook_runner.py`:
    - Direcionar o salvamento do payload de contexto para `.vitalia/memory/data_storage/context/<workflow>_<timestamp>_<machine_id>_<hash>.json`.
    - Purgar completamente a telemetria via Redis Streams e bibliotecas de conexão de rede.
  - `source/src/core/guardian.py`: descontinuar qualquer cálculo de corte ou truncamento de token budget para modelos de fronteira.

### Fase 3: Governança, Perfis e os 12 TOMLs Canônicos
* **Objetivo:** Estabelecer a integridade de regras e contratos do ecossistema.
* **Entregáveis:**
  - Atualização de `source/profiles/constitution.yaml` com o cabeçalho `Vitalia SPEC Kit v0.0.1` e fuso GMT-04:00.
  - Atualização de `source/profiles/routing_table.yaml` e `brainstorming_intents.yaml`.
  - Implementação de `source/extensions/architect.toml` e saneamento das 11 extensões existentes conforme a Seção 4 do briefing canônico.

### Fase 4: Validação End-to-End via Dogfooding
* **Objetivo:** Comprovar a operação integrada do novo kit.
* **Entregáveis:**
  - Execução de testes de caracterização para assegurar que as saídas dos hooks atendem aos esquemas OpenAPI 3.0 definidos em `contracts/`.
  - Teste de idempotência executando `./kit-bootstrap.sh` repetidas vezes.
  - Submissão ao Sub-Agente nativo `/vitalia-judge --mode=plan`.
