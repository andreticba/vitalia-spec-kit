<!-- plan.md | Vitalia SDD v0.6.0 | 10-11-2026 14:55(GMT-04:00) -->
> **plan.md | Vitalia SDD v0.6.0 | 10-11-2026 14:55(GMT-04:00)**

# Implementation Plan: 003-modular-runtime-and-sensor-suite

**Branch**: `003-modular-runtime-and-sensor-suite` | **Data**: 10-11-2026 14:55 (GMT-04:00)  
**Spec**: [`specs/003-modular-runtime-and-sensor-suite/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/spec.md)  
**Status Constitucional**: EM AUDITORIA ADVERSARIAL (SUB-AGENTE SDD-JUDGE)  
**Autor**: Vitalia AI Spec Lead & Solution Architect  

---

## 1. Summary

A funcionalidade **003-modular-runtime-and-sensor-suite** estabelece a nova base de arquitetura de tempo de execução modular, resiliente e auditável do Vitalia SPEC Kit. O plano compreende a purga definitiva de dependências de daemons externos (Redis), a erradicação de ruídos cognitivos do runtime (`tmp_cleanup_matrix`), a padronização dos 16 workflows canônicos sob Design-by-Contract (DbC) e schemas OpenAPI 3.0 Limpos, a implantação da suíte de 5 sensores em runtime (VRSS), a persistência rigorosa de backups e manifestos na Camada 4 (`data_storage/`), e a blindagem de caminhos e scripts de instalação com validação defensiva e idempotência estrita.

---

## 2. Technical Context

- **Linguagem & Interpretador**: Python 3.10+ (suportando Python 3.11, 3.12, 3.13, 3.14).
- **Dependências Primárias**: Standard Library Python (`pathlib`, `json`, `os`, `re`, `ast`, `shutil`, `sys`), `pyyaml`, `tomllib` (ou parser fallback nativo).
- **Armazenamento e Estado**: Filesystem puro baseado em I/O atômico (`.vitalia/memory/data_storage/`). Zero bancos locais e zero Redis.
- **Framework de Testes**: `pytest` com asserções comportamentais da Matriz P05.
- **Plataforma Alvo**: Linux nativo, WSL2 (Ubuntu/Debian) e IDE Google Antigravity.
- **Tipo de Projeto**: Kit de ferramentas de governança de IA, CLI e extensões de IDE.
- **Metas de Performance**: Despacho de hooks < 150ms, tempo de execução dos 5 sensores < 250ms, zero chamadas de rede locais na porta 6379, redução de 100% de linhas de `tmp_cleanup_matrix` em `guardian_json`.
- **Restrições**: Sem daemons em background, sem escrita fora de `<project_root>/.vitalia/`, sem caminhos absolutos hardcoded no repositório.

---

## 3. Constitution Check

| Princípio | Cláusula | Severidade | Avaliação de Conformidade Técnica no Plano | Status |
| :--- | :--- | :--- | :--- | :--- |
| **P00** | Human Wellbeing First | BLOCKING | Elimina poluição cognitiva do prompt de modelos LLM, reduzindo estresse e alucinações. | **APROVADO** |
| **P01** | SDD Pipeline Inviolability | BLOCKING | Segue estritamente `specify` ➔ `plan` ➔ `tasks` ➔ `implement` ➔ `converge`. | **APROVADO** |
| **P02** | User-Centric Validation | WARNING | Impacto operacional documentado e mensurável (SC-001 a SC-008). | **APROVADO** |
| **P03** | External Verification Protocol | WARNING | Decisões técnicas fundamentadas com documentação oficial em `research.md`. | **APROVADO** |
| **P04** | Timestamp & GMT-04:00 Integrity | WARNING | Cabeçalhos padronizados na linha 1 e 2 em todos os arquivos Markdown. | **APROVADO** |
| **P05** | Test-First & Falsification Matrix | BLOCKING | Test Depth Agreement (TDA) define modalidades e cenários de falsificação. Veto a testes rasos. | **APROVADO** |
| **P06** | Secrets Never in Git | BLOCKING | `sensor_tokens_leak.py` varre ativamente segredos em código e dados de contexto. | **APROVADO** |
| **P07** | Privacy by Design & Data Vault | BLOCKING | Centralização de dados sensíveis na Camada 4 (`data_storage/`) com Zero Data Leak. | **APROVADO** |
| **P08** | Smart Routing & Min Privilege | INFO | Contratos TOML delimitam ferramentas estritas (`required`/`optional`). | **APROVADO** |
| **P10** | Didactics-First & Automation | WARNING | Todos os scripts e sensores implementam `--help` e comentários elucidativos. | **APROVADO** |
| **P11** | Hardware-Agnostic & OpenAPI 3.0 | BLOCKING | 100% dos schemas em OpenAPI 3.0 limpo; paths dinâmicos sem nós de máquina hardcoded. | **APROVADO** |
| **P12** | Prompt Injection & Output Valid | BLOCKING | Context Lifting com validação de schemas OpenAPI 3.0 antes da entrega aos agentes. | **APROVADO** |
| **P15** | Observability & Structured Logs | WARNING | VRSS reporta métricas e anomalias de execução de forma estruturada. | **APROVADO** |
| **P16** | Artifact Integrity & Mermaid | WARNING | Diagramas e artefatos consistentes com rótulos entre aspas duplas. | **APROVADO** |

---

## 4. Technical Decisions

Todas as decisões técnicas detalhadas encontram-se fundamentadas em [`specs/003-modular-runtime-and-sensor-suite/research.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/research.md):
- **Decisão 1**: Runtime em Filesystem Puro & Purga Total do Redis.
- **Decisão 2**: VRSS - 5 Sensores Independentes de Runtime (`purity`, `contract_dbc`, `memory_ledger`, `tokens_leak`, `path_hygiene`).
- **Decisão 3**: Contratos Declarativos TOML dos 16 Workflows Canônicos em `source/extensions/`.
- **Decisão 4**: Persistência de Backups e Manifestos na Camada 4 (`data_storage/backups/skills/` e `data_storage/manifests/`).
- **Decisão 5**: Erradicação da Matriz Temporária do Runtime e Isolamento do CLI `vitalia_tmp_cleanup.py`.
- **Decisão 6**: Resolução Defensiva do Diretório do Kit (`resolve_kit_dir` com checagem de existência física).
- **Decisão 7**: Nomenclatura Idempotente no Gerador de Skills (`${ext_name#vitalia-}`).
- **Decisão 8**: Centralização de Schemas em OpenAPI 3.0 Limpo (`source/src/schemas/`).

---

## 5. Matriz de Migração e Preservação Comportamental

| Componente | Comportamento Existente a Preservar (Invariante de Negócio) | Acoplamento / Defeito a Remover | Contrato do Consumidor & Estratégia de Teste (`[TEST:MIGRATION]`) |
| :--- | :--- | :--- | :--- |
| `kit_env_bootstrap.py` | Carregamento de variáveis de ambiente do `.env` e descoberta do diretório do kit. | Probes na porta 6379 (Redis), telemetria via redis e retorno cego de caminhos inexistentes. | `test_kit_env_bootstrap_migration`: Comprova que `.env` é lido, portas de rede não são sondadas, e caminhos inexistentes acionam fallback defensivo para `script_kit_root`. |
| `vitalia_hook_runner.py` | Injeção de contexto transitório §11 Context Lifting, execução de hooks before/after e constituição integral. | Injeção da `tmp_cleanup_matrix` com menus interativos no payload `guardian_json`. | `test_hook_runner_clean_context`: Executa o hook runner e atesta que o arquivo de contexto é gerado com sucesso, sem conter a chave `tmp_cleanup_matrix`. |
| `skill_generator.sh` | Geração e atualização contínua de skills em `.agents/skills/` com base nas extensões TOML. | Concatenação redundante gerando diretórios duplicados `vitalia-vitalia-*`. | `test_skill_generator_idempotency`: Invoca a geração de skills a partir de `vitalia-route.toml` e valida que a pasta criada é estritamente `vitalia-route`. |
| `agent_preserver.sh` | Preservação de versões anteriores de skills durante updates e cálculo de hashes SHA-256. | Gravação de backups soltos em `.vitalia/` ou `.agents/skills/` e manifestos na raiz. | `test_persistence_data_storage_layer`: Executa atualização e verifica que backups estão estritamente em `data_storage/backups/skills/` e o manifesto em `data_storage/manifests/`. |
| `scan_environment.py` | Diagnóstico de integridade do ambiente e relatório JSON de saúde. | Alertas falsos de degradação por ausência de daemon Redis local. | `test_scan_environment_healthy`: Executa o script e valida que retorna `HEALTHY` em ambiente local baseado exclusivamente em filesystem. |

---

## 6. Test Depth Agreement (TDA — Matriz Constitucional P05)

É terminantemente proibido o uso de testes puramente sintáticos/estáticos (ex: `assert path.is_file()` ou `assert "string" in path.read_text()`). Todo teste deve validar comportamento executável de caixa-preta, acompanhado de seu Cenário de Falsificação explícito:

1. **`[TEST:BUGFIX]` — Resolução Defensiva de Diretório em `kit_env_bootstrap.py`**:
   - *Cenário de Falsificação*: Configurar `VITALIA_KIT_DIR=/diretorio/inexistente/no/sistema`. O teste falha se a função lançar `FileNotFoundError` ou retornar o caminho inválido sem validar sua existência física. O teste passa apenas quando retornar a raiz do kit executável (`script_kit_root`).
2. **`[TEST:BUGFIX]` — Purga da Matriz Temporária em `vitalia_hook_runner.py`**:
   - *Cenário de Falsificação*: Executar `vitalia_hook_runner.py` para um workflow qualquer. O teste falha se a chave `tmp_cleanup_matrix` estiver presente em `guardian_json` ou se o tamanho do payload exceder os limites úteis. O teste passa quando a chave estiver ausente e o contexto limpo.
3. **`[TEST:BUGFIX]` — Nomenclatura Idempotente em `skill_generator.sh`**:
   - *Cenário de Falsificação*: Passar uma extensão com prefixo `vitalia-` pré-existente. O teste falha se o diretório de destino for nomeado com duplicação (`vitalia-vitalia-*`). O teste passa apenas se o diretório for unificado em `vitalia-<workflow>`.
4. **`[TEST:NEW]` — Suíte VRSS de Sensores (`sensor_purity.py`, `sensor_path_hygiene.py`, etc.)**:
   - *Cenário de Falsificação*: Injetar intencionalmente um arquivo órfão em `.agents/skills/` ou uma string hardcoded `source/` em arquivo de teste. O teste falha se os respectivos sensores retornarem código de saída 0 (sucesso). O teste passa apenas quando os sensores emitirem código de erro e relatório de violação preciso.
5. **`[TEST:MIGRATION]` — Persistência de Backups e Manifestos na Camada 4**:
   - *Cenário de Falsificação*: Executar ciclo de preservação. O teste falha se qualquer arquivo for criado na raiz de `.vitalia/` ou em `.agents/skills/` fora de subpastas com `SKILL.md`. O teste passa apenas quando backups residirem em `data_storage/backups/skills/` e o manifesto em `data_storage/manifests/`.
6. **`[TEST:NEW]` — Conformidade de Schemas OpenAPI 3.0 Limpos**:
   - *Cenário de Falsificação*: Inspecionar todos os schemas em `source/src/schemas/`. O teste falha se qualquer schema contiver meta-campos proibidos (`$schema`, `title` raiz, `additionalProperties: false`). O teste passa quando 100% dos schemas forem OpenAPI 3.0 estritos.

---

## 7. Project Structure

### Documentation (this feature)
```
specs/003-modular-runtime-and-sensor-suite/
├── spec.md                                         # Especificação formal aprovada
├── research-brainstorming.md                       # Síntese socrática e escopo estendido
├── research.md                                     # Decisões técnicas e grounding P03
├── plan.md                                         # Este plano de implementação
├── data-model.md                                   # Modelo de dados da Camada 4
├── quickstart.md                                   # Guia executável de verificação end-to-end
├── checklists/
│   └── requirements.md                             # Checklist de qualidade de requisitos
├── Relatório de Inspeção - specify.md              # Parecer do SDD-Judge sobre spec.md
├── Relatório de Inspeção - plan.md                 # Parecer do SDD-Judge sobre plan.md
└── [8 documentos canônicos de concepção]           # Corpus conceitual original
```

### Source Code
```
source/
├── bin/
│   ├── install.sh                                  # Instalador idempotente
│   ├── skill_generator.sh                          # Gerador com strip de prefixo
│   └── agent_preserver.sh                          # Preservador apontado para Camada 4
├── extensions/                                     # 16 Workflows Canônicos em TOML
│   ├── session-start.toml
│   ├── spec-specify.toml
│   ├── judge.toml
│   ├── spec-plan.toml
│   ├── spec-tasks.toml
│   ├── task-verifier.toml
│   ├── spec-implement.toml
│   ├── analyze.toml
│   ├── converge.toml
│   ├── clarify.toml
│   ├── research.toml
│   ├── session-end.toml
│   ├── session-consolidate.toml
│   ├── brainstorming.toml
│   ├── route.toml
│   └── architect.toml
├── src/
│   ├── kit_env_bootstrap.py                        # Resolução dinâmica e defensiva
│   ├── vitalia_hook_runner.py                      # Hook runner sem tmp_cleanup_matrix
│   ├── vitalia_tmp_cleanup.py                      # Utilitário autônomo CLI de faxina
│   ├── hooks/
│   │   ├── scan_environment.py                     # Scanner sem probes de Redis
│   │   └── guardian_context.py                     # Context lifting constitucional
│   ├── schemas/                                    # Schemas OpenAPI 3.0 Limpos
│   │   ├── context_payload.json
│   │   ├── feature_metadata.json
│   │   ├── session_ledger.json
│   │   └── pipeline_state.json
│   └── sensors/                                    # Suíte VRSS (5 Sensores)
│       ├── sensor_purity.py
│       ├── sensor_contract_dbc.py
│       ├── sensor_memory_ledger.py
│       ├── sensor_tokens_leak.py
│       └── sensor_path_hygiene.py
└── tests/                                          # Suíte de Testes Comportamentais P05
    ├── test_kit_env_bootstrap.py
    ├── test_hook_runner.py
    ├── test_sensors_vrss.py
    ├── test_skill_generator.py
    ├── test_schemas_openapi.py
    └── test_clean_install_wsl2.py
```

---

## 8. Phase Overview

### Phase 1: Setup & Groundwork (Infraestrutura Defensiva & Purga de Redis)
- **Objetivo**: Garantir que o ambiente de execução opere em filesystem puro sem ruídos de rede, e que a resolução de diretórios seja resiliente a caminhos inexistentes.
- **Entregas**:
  - Teste `[TEST:BUGFIX]` e refatoração em `kit_env_bootstrap.py` (validação física `candidate.exists()`).
  - Purga definitiva de menções ao Redis e portas de rede em `kit_env_bootstrap.py` e `scan_environment.py`.
  - Remoção de `tmp_cleanup_matrix` em `vitalia_hook_runner.py` e isolamento do CLI `vitalia_tmp_cleanup.py`.

### Phase 2: Sensor Suite (VRSS) & Pureza Arquitetural
- **Objetivo**: Construir a suíte de 5 sensores em runtime para monitoramento contínuo das invariantes do sistema.
- **Entregas**:
  - Criação de `sensor_purity.py`, `sensor_contract_dbc.py`, `sensor_memory_ledger.py`, `sensor_tokens_leak.py` e `sensor_path_hygiene.py`.
  - Criação de testes `[TEST:NEW]` com injeção deliberada de anomalias para falsificação dos sensores.
  - Redirecionamento da persistência de backups e manifestos em `agent_preserver.sh` e `skill_generator.sh` para a Camada 4 (`data_storage/backups/skills/` e `data_storage/manifests/`).

### Phase 3: Workflows Canônicos DbC & Centralização de Schemas
- **Objetivo**: Padronizar os 16 workflows centrais sob contratos declarativos TOML e schemas OpenAPI 3.0 Limpos.
- **Entregas**:
  - Centralização dos schemas JSON em `source/src/schemas/` e purga de meta-campos incompatíveis.
  - Ajuste e validação dos 16 arquivos TOML em `source/extensions/` com DbC formal.
  - Implementação de strip de prefixo idempotente em `skill_generator.sh`.

### Phase 4: Automação de Instalação, Verificação End-to-End & Polish
- **Objetivo**: Integrar instalador em ambiente limpo e validar todo o ciclo operacional.
- **Entregas**:
  - Atualização do script `install.sh` com permissões e paths defensivos.
  - Roteiro de testes executável em WSL2/Linux (`roteiro_testes_maquina_limpa_wsl2.md`).
  - Execução dos 5 sensores sobre todo o repositório garantindo conformidade total.

---

## 9. Socratic Gate (Hard Stop Constitucional)

> [!IMPORTANT]
> **GATE SOCRÁTICO DE VALIDAÇÃO DE PLANO (HITL SOBERANO)**  
> O plano técnico formaliza a arquitetura modular, a suíte de 5 sensores VRSS, os contratos DbC dos 16 workflows canônicos, a purga do Redis e a persistência na Camada 4 sob a Matriz de Testes P05.
> 
> Antes de prosseguirmos para o desmembramento em tarefas atômicas (`/vitalia-spec-tasks`), confirme a aprovação deste plano técnico.

