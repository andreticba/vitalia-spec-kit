<!-- spec.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 19:55(GMT-04:00) -->
> **spec.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 19:55(GMT-04:00)**

# Especificação Funcional — Spec 002: Universal Bootstrap & Runtime

* **Feature:** `specs/002-universal-bootstrap-runtime`
* **Status:** DRAFT REVISADO (Ajustado após feedback HITL e pronto para re-inspeção)
* **Preset:** `software` (ISO/IEC/IEEE 29148:2018 Compliant)
* **Data da Revisão:** 04-11-2026 19:55(GMT-04:00)
* **Governança:** Vitalia SPEC Kit v0.0.1

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

### 1.1 Contexto
O ecossistema de desenvolvimento assistido por agentes requer autonomia, previsibilidade e portabilidade entre máquinas heterogêneas. A arquitetura prévia acumulava dependências de containers Docker locais de suporte (serviços de cache e banco de dados relacional), limitadores artificiais de contexto desenhados para hardware modesto com 6 GB de VRAM (que mutilavam regras, aprendizados e catálogos), scripts legados descontinuados de auditoria externa e caminhos fixos no sistema de arquivos.

### 1.2 Objetivo
Esta funcionalidade transforma o kit em uma ferramenta de engenharia **100% autônoma, portável e instalável a partir de repositório limpo**, estabelecendo um runtime isolado com ciclo de vida idempotente (instalação e reinstalação/atualização seguras), persistência transacional direta em sistema de arquivos, Context Lifting seguro alocado no armazenamento de contexto do projeto (sem poluir o código-fonte via `.gitignore`), eliminação universal de podas de contexto em todos os blocos do oráculo e aplicação da marca canônica **Vitalia SPEC Kit v0.0.1**.

---

## 2. Suposições Verificadas (Grounding de 2026 — Princípio P03)

Em conformidade com o protocolo de verificação externa, as diretrizes conceituais foram validadas na literatura técnica de 2026:

| # | Tecnologia / Conceito | Fonte Canônica | URL Verificada | Data da Verificação |
|---|---|---|---|---|
| **E1** | **Decoupled Brain, Hands & Session** | Anthropic Engineering (2026) | [`https://www.anthropic.com/engineering/managed-agents`](https://www.anthropic.com/engineering/managed-agents) | 03-11-2026 |
| **E2** | **Positional Slices & Prompt Caching** | Anthropic Platform Docs (2026) | [`https://platform.claude.com/docs/en/managed-agents/overview`](https://platform.claude.com/docs/en/managed-agents/overview) | 03-11-2026 |
| **E3** | **Inverted Chain-of-Thought (Critique-First)** | LMSYS / UC Berkeley (MT-Bench) | [`https://arxiv.org/abs/2306.05685`](https://arxiv.org/abs/2306.05685) | 03-11-2026 |
| **E4** | **Application Runtime Isolation Pattern** | Python Packaging Authority (PyPA) | [`https://github.com/pypa/pipx`](https://github.com/pypa/pipx) | 03-11-2026 |
| **E5** | **Critérios Canônicos de Engenharia de Requisitos** | ISO/IEC/IEEE 29148:2018 | [`https://www.iso.org/standard/72089.html`](https://www.iso.org/standard/72089.html) | 03-11-2026 |

---

## 3. Requisitos Funcionais (Agnósticos de Implementação)

Em conformidade com a ISO 29148, cada requisito é singular, mensurável, testável e agnóstico de tecnologia:

### FR-001: Bootstrap Universal Idempotente (Instalação e Reinstalação) [MUST]
* **Descrição:** O sistema deve fornecer um mecanismo autônomo de inicialização que configure ou reinstale/repare o ambiente de operação do produto de maneira estritamente idempotente. O processo deve detectar instalações existentes ou corrompidas e reconfigurar shims e ambiente virtual isolado sem gerar falhas de conflito de arquivos e sem exigir containers de virtualização.
* **Critério de Testabilidade:** Execução repetida do processo de bootstrap em máquina limpa e subsequentemente sobre diretório pré-existente, resultando em saída bem-sucedida (código 0) e ambiente operacional consistente em ambas as execuções.

### FR-002: Isolamento de Runtime da Ferramenta [MUST]
* **Descrição:** O sistema deve executar seus processos internos dentro de um ambiente de execução dedicado e autocontido, impedindo interferências ou conflitos com bibliotecas instaladas nos projetos dos usuários onde os comandos são invocados.
* **Critério de Testabilidade:** Invocação de comandos do kit a partir de projetos com diferentes conjuntos de dependências locais sem contaminação mútua.

### FR-003: Disponibilização Global de Comandos de Sistema [MUST]
* **Descrição:** O sistema deve registrar shims de execução no diretório de comandos de usuário do sistema operacional, permitindo invocação idempotente dos utilitários a partir de qualquer terminal ou subprocesso da IDE.
* **Critério de Testabilidade:** Execução de comandos utilitários a partir de qualquer diretório de trabalho do usuário no sistema.

### FR-004: Verificação Diagnóstica de Ambiente Desacoplada [MUST]
* **Descrição:** A verificação diagnóstica pré-execução deve avaliar estritamente a presença de arquivos de configuração locais, diretórios de governança e integridade do runtime isolado, sem emitir alertas de degradação por ausência de portas de rede de containers auxiliares.
* **Critério de Testabilidade:** Verificação diagnóstica retornando estado saudável em ambiente que opera exclusivamente sobre sistema de arquivos sem portas de rede abertas.

### FR-005: Context Lifting em Armazenamento Local Isolado do Repositório de Código [MUST]
* **Descrição:** O sistema deve gravar os payloads de Context Lifting estritamente no armazenamento transitório local do projeto (`.vitalia/memory/data_storage/context/`), garantindo que os dados residam no disco do projeto (eliminando vazamento em diretórios temporários globais compartilhados como `/tmp/`), ao mesmo tempo em que a pasta `.vitalia/memory` é mantida estritamente excluída do versionamento de código da aplicação hospedeira através do `.gitignore`.
* **Critério de Testabilidade:** Comprovação de que arquivos de contexto residem em `.vitalia/memory/data_storage/context/`, que não há escrita em `/tmp/` e que os arquivos de contexto são estritamente ignorados pelo controle de versão do projeto hospedeiro (permanecendo ocultos ao comando `git status` padrão e imunes a `git add .` graças às regras no `.gitignore`).

### FR-006: Identificação e Particionamento por Estação [MUST]
* **Descrição:** O sistema deve associar a cada artefato de sessão, log transacional e registro de aprendizado o identificador persistente e unívoco da máquina física que executou a ação, assegurando integridade em sincronizações distribuídas entre múltiplos ambientes.
* **Critério de Testabilidade:** Verificação de presença do identificador de estação em cada registro estruturado de contexto e nos nomes dos arquivos de elevação de contexto.

### FR-007: Ingestão de Contexto Integral Universal (Eliminação Holística de Podas) [MUST]
* **Descrição:** O motor de contexto deve injetar integralmente **todos os blocos de contexto** (Constituição holística, histórico de aprendizados consolidados `context_learnings`, histórico de decisões arquiteturais `context_decisions`, catálogo de agentes e tabelas de roteamento) sem aplicar cortes artificiais de quantidade de itens, filtros restritivos de severidade ou tetos de orçamento de tokens baseados em restrições de VRAM legada.
* **Critério de Testabilidade:** Inspeção do payload do oráculo comprovando a presença de todos os aprendizados e decisões históricas e todos os domínios constitucionais ativos sem truncamento de conteúdo.

### FR-008: Governança de Marca Canônica e Rastreabilidade Temporal [MUST]
* **Descrição:** Todo artefato de documentação ou código gerado ou atualizado pelo sistema deve estampar no cabeçalho a identificação unificada `Vitalia SPEC Kit v0.0.1` e a marcação de tempo no fuso horário imutável `America/Cuiaba (GMT-04:00)`.
* **Critério de Testabilidade:** Validação automática da presença e conformidade da assinatura em todos os arquivos rastreados.

### FR-009: Padronização Contratual das Extensões Canônicas [MUST]
* **Descrição:** O sistema deve estruturar os contratos de configuração dos 12 comandos do ciclo SDD e governança sem declarações obsoletas de perfis de hardware restritivos e sem dependências de módulos descontinuados.
* **Critério de Testabilidade:** Validação sintática e contratual de todos os arquivos de extensão contra o esquema de dados do oráculo.

### FR-010: Regência Técnica do Papel de Tech Lead (Vitalia Architect) [MUST]
* **Descrição:** O sistema deve fornecer um comando formal de regência arquitetural que atue na transição entre o brainstorming e o início do ciclo formal de especificação, confrontando demandas contra a constituição e formalizando decisões estruturantes antes do pipeline de escrita.
* **Critério de Testabilidade:** Handoff formal do brainstorming sendo absorvido pelo papel de arquitetura e culminando na recomendação formal de especificação.

### FR-011: Estratégia de Testes Contextualizada [MUST]
* **Descrição:** O sistema deve classificar formalmente a abordagem de testes de acordo com a natureza da demanda de engenharia: teste de ausência prévio para código novo, teste reprodutor prévio para correção de defeitos e testes de caracterização para refatoração.
* **Critério de Testabilidade:** Existência de classificação formal da modalidade de teste em cada plano técnico emitido pelo fluxo.

### FR-012: Delimitação Estrita de Fronteiras Funcionais (Escopo MVP) [MUST]
* **Descrição:** O escopo do sistema deve ser restrito às capacidades fundamentais de runtime, governança e orquestração dos comandos essenciais, mantendo papéis especializados verticais formalmente demarcados como planejados para ciclos subsequentes.
* **Critério de Testabilidade:** Confirmação de que os comandos fundamentais operam de forma completa sem invocar módulos não-instanciados.

---

## 4. Requisitos Não-Funcionais (Restrições Sistêmicas)

* **RNF-001 (Independência de Virtualização):** O sistema não deve exigir privilégios de superusuário ou daemons de virtualização (Docker/Podman) em tempo de execução.
* **RNF-002 (Integridade de Fuso Horário):** Nenhuma rotina do sistema deve admitir cálculo de horário de verão ou variação de fuso diferente de GMT-04:00 imutável.
* **RNF-003 (Compatibilidade OpenAPI 3.0):** Todos os esquemas de dados trocados entre ferramentas e modelos devem utilizar o padrão OpenAPI 3.0 puro, sem meta-campos Draft-07 (`$schema`, `title` de raiz ou `additionalProperties: false`).
* **RNF-004 (Tempo de Resposta do Context Lifting):** A extração e gravação do contexto de execução para qualquer workflow deve ser concluída em menos de 1.500 milissegundos.

---

## 5. Histórias de Usuário (User Stories)

### US1: Instalação e Reinstalação Segura (Idempotência)
* **Como** desenvolvedor em uma estação de trabalho nova ou existente,
* **Eu quero** executar o comando de bootstrap para instalar, atualizar ou reparar o kit,
* **Para que** o ambiente fique perfeitamente operacional sem erros de conflito de arquivos existentes ou estado corrompido, e sem depender de containers.

### US2: Armazenamento Local e Seguro de Contexto sem Poluir o Código
* **Como** desenvolvedor que trabalha em projetos sensíveis com controle de versão,
* **Eu quero** que os arquivos de contexto da IA sejam gravados no armazenamento local de contexto em `.vitalia/memory/data_storage/context/` protegido por `.gitignore`,
* **Para que** os dados da sessão não vazem para diretórios temporários globais do sistema (`/tmp`) e simultaneamente não apareçam como arquivos pendentes de commit no repositório de código da aplicação.

### US3: Condução Arquitetural Estruturada
* **Como** engenheiro de software,
* **Eu quero** que o Vitalia Architect avalie os consensos de ideação e registre decisões arquiteturais formais,
* **Para que** o desenvolvimento inicie fundamentado em princípios constitucionais e contratos estáveis.

### US4: Auditoria Adversarial Precoce
* **Como** guardião de qualidade,
* **Eu quero** que cada fase documental seja auditada pelo SDD-Judge antes de qualquer implementação,
* **Para que** defeitos conceituais e violações de regras sejam corrigidos com custo zero de retrabalho.

---

## 6. Critérios de Aceite (Acceptance Criteria — Given / When / Then)

### SC-001: Instalação e Reinstalação Idempotente
* **Dado que** o usuário aciona a rotina de bootstrap em uma máquina limpa OU sobre uma instalação pré-existente do kit,
* **Quando** o processo é executado,
* **Então** o runtime isolado é configurado ou atualizado com sucesso, os shims são criados/reparados e os comandos tornam-se imediatamente funcionais sem erros de concorrência de arquivos.

### SC-002: Diagnóstico de Ambiente Não-Bloqueante
* **Dado que** o projeto opera exclusivamente sobre o sistema de arquivos local sem portas de rede abertas,
* **Quando** a rotina diagnóstica de pré-execução é disparada,
* **Então** o status do ambiente é reportado como saudável, sem avisos de ausência de Redis ou Postgres.

### SC-003: Isolamento do Context Lifting em Armazenamento Local Ignorado
* **Dado que** um comando assistido por inteligência artificial é invocado,
* **Quando** o motor de contexto constrói o payload de execução,
* **Então** o arquivo de contexto gerado reside estritamente em `.vitalia/memory/data_storage/context/` contendo o `machine_id` no nome, sem nenhuma escrita em `/tmp/` e permanecendo estritamente ignorado e oculto ao `git status` do repositório de código do projeto.

### SC-004: Injeção Universal de Contexto sem Podas de Tokens
* **Dado que** a inteligência artificial opera em modelo de fronteira na IDE,
* **Quando** o contexto operacional é construído pelo Guardian,
* **Então** TODOS os elementos de contexto (Constituição P00-P18, totalidade de `context_learnings`, totalidade de `context_decisions`, catálogos de agentes e rotas) constam integralmente no arquivo sem podas de volume, limites de itens ou tetos artificiais de tokens.

### SC-005: Rastreabilidade de Marca e Fuso nos Artefatos
* **Dado que** qualquer arquivo de código ou documentação é processado pelo sistema,
* **Quando** o arquivo é persistido,
* **Então** sua primeira linha estampa a identificação `Vitalia SPEC Kit v0.0.1` acompanhada de data e hora com sufixo `(GMT-04:00)`.

### SC-006: Geração e Consolidação do Dashboard de Contexto
* **Dado que** uma sessão de trabalho é consolidada via `/vitalia-session-consolidate`,
* **Quando** a rotina processa os dados de sessão e shards das máquinas,
* **Então** o painel visual `README.md` (com escudos informativos SVG, status de semáforo e diagramas Mermaid em tema nativo) e as visões puras em Markdown são geradas com sucesso dentro do repositório isolado de contexto em `.vitalia/memory/session/`.

---

## 7. Delimitação de Escopo (In Scope vs. Out of Scope)

### 7.1 No Escopo (In Scope)
* Geração do painel consolidado `README.md` da sessão em Markdown formatado (com badges/shields SVG e diagramas Mermaid nativos) dentro do repositório isolado de contexto (`.vitalia/memory/session/`), perfeitamente renderizável pela IDE e por visualizadores Git remotos.
* Utilitário autônomo de bootstrap idempotente em shell script com detecção e reparo de ambiente.
* Governança dos 12 comandos canônicos e contratos TOML do kit.

### 7.2 Fora do Escopo (Out of Scope)
* **Aplicações com Interface Gráfica Externa Standalone:** Não inclui o desenvolvimento de interfaces gráficas dedicadas fora da IDE (aplicações desktop standalone em Qt, Electron ou servidores web com frontends próprios em React/Vue para monitoramento de bootstrap). Toda interação ocorre via terminal e IDE Antigravity.
* **Especialistas Verticais:** Não inclui a ativação operacional nem os fluxos especializados dos 5 agentes verticais (`Django-Stark`, `React-Vinci`, `Infra-Nomad`, `Cortex-Analyst`, `Figma-Maestro`), alocados formalmente para a **Spec 003**.
* **Gerenciadores Globais de Pacotes:** Não inclui publicação do kit em repositórios públicos globais de pacotes (PyPI/npm) neste ciclo de MVP.
* **Modelos LLM com Janela Restrita:** Não inclui suporte a modelos de linguagem legados com janela de contexto inferior a 32.000 tokens.
