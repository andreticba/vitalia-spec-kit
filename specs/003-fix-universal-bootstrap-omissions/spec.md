<!-- spec.md | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:30:00(GMT-04:00) -->
> **spec.md | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:30:00(GMT-04:00)**

# Especificação Formal — Spec 003: Fix Universal Bootstrap Omissions (v0.0.1)

---

## 1. Sumário Executivo & Declaração de Valor

### 1.1. Contexto e Justificativa
A entrega da Spec 002 estabeleceu a fundação do instalador universal e o isolamento de runtime (`.venv`). Contudo, testes automatizados insuficientes e o espelhamento manual em lote (`cp -r`) causaram a omissão de componentes vitais (`integrations/`, `AGENTS.md`, `analyze.toml`, templates de dashboard), caminhos legados quebrados (`~/.vitalia`), regressão severa na fidelidade do painel de contexto (`session-consolidate`), e acoplamentos conceituais com infraestruturas locais descontinuadas (Redis, Celery, Ollama, VRAM fatiada).

A **Spec 003** é uma **especificação formal corretiva e de remediação arquitetural (`fix-*`)** que resolve integralmente essas lacunas. Ela substitui o espelhamento cego por uma esteira de instalação atômica validada componente por componente, restabelece a fidelidade visual e informativa do dashboard de memória, e introduz governança temporal estrita em 10 domínios canônicos de grounding e 9 domínios de questionamento socrático centrados no Princípio da Responsabilidade Única (SRP).

### 1.2. Valor para o Usuário
- **Instalação Autônoma e Parametrizada:** O desenvolvedor define interativamente o diretório de instalação do kit (`VITALIA_KIT_DIR`), e todos os scripts respeitam essa variável via `.env`.
- **Rastreabilidade Forense e Proteção de Dados:** Eventos de instalação acumulados em buffer de memória, gravados condicionalmente em log detalhado, com backup automático da pasta `.agents` se `DATA_REPO` estiver configurado.
- **Painel de Memória Rico e Fiel:** Restauração do dashboard consolidado com badges de status, diagrama de topologia Mermaid `flowchart TD`, tabela executiva de shards e seções expansíveis (`<details>`) para histórico de sessões, decisões arquiteturais e guard rails de grounding.
- **Governança Temporal e Proveniência de Conhecimento:** 10 domínios canônicos em `grounding_domains.yaml` e 9 domínios em `dynamic_questioning.yaml` com prazos de validade (`valid_until`), rastreamento de fontes autoritativas (`last_update_source`) e política de atualização em 4 etapas.
- **Auditoria Contínua de Código (HITL Soberano):** Workflow nativo `/vitalia-analyze` inspeciona a consistência entre especificação, planejamento e código real (Git Diff em 3 camadas e análise estática de call-sites) com pausa mandatória para aprovação humana.

---

## 2. Atores e Papéis

- **Desenvolvedor / Usuário Host:** Engenheiro ou pesquisador executando a instalação do kit em máquina limpa ou ativando o kit em um repositório hospedeiro.
- **Agente / Sub-Agente IDE:** Modelo de IA (Gemini 2.5 Flash/Pro, Claude 3.5, etc.) orquestrado via Antigravity IDE executando workflows SDD.
- **Oráculo Guardian (§11):** Mecanismo de context lifting que injeta a constituição, tabelas de roteamento e regras de ambiente sem podas artificiais de tokens.

---

## 3. Cenários de Usuário & Critérios de Aceite (Given/When/Then)

### US1: Instalação Limpa do Kit Global com Destino Parametrizado
**Como** desenvolvedor configurando uma nova máquina,  
**Quero** executar `kit-bootstrap.sh` e escolher interativamente o diretório de instalação do kit global (sugerindo `~/.vitalia-spec-kit`),  
**Para que** o ambiente isolado seja instalado no caminho desejado sem caminhos hardcoded no sistema operacional.

- **Cenário 1.1 — Definição do diretório aceitando o padrão:**
  - **Given** um ambiente host sem instalação prévia do kit e com Python $\ge 3.10$,
  - **When** o usuário executa `./kit-bootstrap.sh` e pressiona Enter no prompt de destino,
  - **Then** o sistema adota `~/.vitalia-spec-kit/`, cria o virtualenv isolado, instala dependências de `requirements.txt`, copia atomicamente todos os componentes autorizados (incluindo `templates/dashboard_template.md`, `integrations/` e `AGENTS.md`) e gera o shim `~/.local/bin/vitalia-install-project` contendo `export VITALIA_KIT_DIR=".../.vitalia-spec-kit"`.

- **Cenário 1.2 — Definição de caminho customizado:**
  - **Given** o mesmo ambiente host limpo,
  - **When** o usuário digita um caminho personalizado (ex: `~/meu-kit-vitalia`),
  - **Then** o sistema expande o til (`~`), cria os diretórios em `~/meu-kit-vitalia`, instala todos os componentes nesse destino e configura o shim para apontar para `~/meu-kit-vitalia`.

---

### US2: Ativação em Projeto Hospedeiro com Log em Memória e Proteção de Dados
**Como** desenvolvedor ativando o kit em um repositório de projeto,  
**Quero** executar `vitalia-install-project`,  
**Para que** o projeto seja configurado com `.vitalia/`, `.env`, skills da IDE Antigravity, log detalhado de execução e backup seguro de `.agents`.

- **Cenário 2.1 — Ativação com repositório de dados remoto configurado:**
  - **Given** um projeto que já possui a pasta `.agents/` e o usuário informa a URL de `DATA_REPO`,
  - **When** a ativação é concluída,
  - **Then** o sistema cria o backup `.vitalia/memory/data_storage/.agents_<timestamp>.bak/`, grava o log detalhado em `.vitalia/memory/data_storage/install_<timestamp>.log`, persiste `VITALIA_KIT_DIR` no `.env` e configura as skills da IDE em `.agents/skills/`.

- **Cenário 2.2 — Ativação sem repositório de dados remoto:**
  - **Given** um projeto onde o usuário não informa a URL de `DATA_REPO` (Enter para pular),
  - **When** a ativação é executada,
  - **Then** o sistema exibe alerta explícito informando que o backup de `.agents` não será realizado, grava o log de instalação diretamente na raiz do projeto (`./install_<timestamp>.log`) e conclui a configuração com sucesso.

- **Cenário 2.3 — Ausência de prompts do Gemini CLI:**
  - **Given** a execução de `install-project`,
  - **When** o script atinge o passo de integrações,
  - **Then** nenhuma pergunta sobre Gemini CLI é exibida; o script configura diretamente a Antigravity IDE (`.agents/skills/`) e registra `antigravity: true` em `.vitalia/config.yml`.

---

### US3: Governança Temporal de Grounding e Questionamento Orientado a SRP
**Como** arquiteto de software conduzindo um `/vitalia-brainstorming`,  
**Quero** que os domínios de grounding e perguntas socráticas cubram arquiteturas modernas regidas por SRP e possuam datas de validade explícitas,  
**Para que** o sistema não sugere tecnologias obsoletas nem restrinja o escopo a PII/PHI.

- **Cenário 3.1 — Consulta a dados dentro do prazo de validade (`ACTIVE`):**
  - **Given** que o domínio técnico possui `valid_until` superior à data atual,
  - **When** o oráculo carrega o contexto do workflow,
  - **Then** o domínio é marcado com status `ACTIVE` e suas premissas são apresentadas como confiáveis.

- **Cenário 3.2 — Detecção de dado expirado (`STALE`) e busca P03 obrigatória:**
  - **Given** que a data atual ultrapassou o `valid_until` de um domínio técnico,
  - **When** a IA processa o workflow,
  - **Then** o oráculo sinaliza status `STALE`, forçando a realização de busca externa (Grounding P03) nas fontes autorizadas antes de emitir a recomendação.

- **Cenário 3.3 — Avaliação de Arquitetura Orientada a SRP:**
  - **Given** o domínio `software_architecture` em `grounding_domains.yaml` e `dynamic_questioning.yaml`,
  - **When** o agente propõe decisões estruturais,
  - **Then** a recomendação avalia a decomposição em componentes atômicos regidos pelo Princípio da Responsabilidade Única (SRP) com interfaces e contratos estritos.

- **Cenário 3.4 — Proposta de renovação e persistência com HITL:**
  - **Given** que um domínio foi revalidado na sessão,
  - **When** o usuário aciona `/vitalia-session-end`,
  - **Then** o relatório de encerramento exibe a Proposta de Renovação com a URL consultada e o novo prazo sugerido, atualizando a base do kit sob aprovação humana soberana.

---

### US4: Restauração da Fidelidade Visual do Dashboard de Memória
**Como** desenvolvedor executando `/vitalia-session-consolidate`,  
**Quero** que o arquivo `.vitalia/memory/session/README.md` seja gerado com base no template canônico rico,  
**Para que** o painel de contexto preserve badges, topologia Mermaid, tabela executiva de máquinas e seções colapsáveis com histórico e decisões.

- **Cenário 4.1 — Renderização do Painel Completo:**
  - **Given** estações ativas com shards gravados e histórico de sessões em `session_history.jsonl`,
  - **When** a ação `vitalia_context_engine.py --action consolidate` é executada,
  - **Then** o `README.md` é gerado contendo:
    - Badges de Status, Semáforo, Modo Filesystem, Sync GMT-04:00 e Grounding Ativo.
    - Diagrama Mermaid `flowchart TD` das estações conectadas ao repositório remoto.
    - Tabela HTML estilizada das máquinas ativas.
    - Sessão ativa em destaque com a tarefa e Próximo Passo Prioritário (P0).
    - Seções expansíveis (`<details>`) para Histórico de Sessões, Decisões Arquiteturais Consolidadas e Guard Rails de Grounding.

- **Cenário 4.2 — Resolução Dinâmica do Template sem Hardcode:**
  - **Given** a execução da consolidação em qualquer projeto,
  - **When** o renderizador busca o arquivo `dashboard_template.md`,
  - **Then** o caminho é resolvido via `kit_env_bootstrap.resolve_kit_dir() / "templates" / "dashboard_template.md"`, sem referências duras a `~/.vitalia`.

---

### US5: Auditoria de Consistência e Código Real com `/vitalia-analyze`
**Como** tech lead conduzindo o ciclo SDD,  
**Quero** executar `/vitalia-analyze` tanto após as tarefas (`after_tasks`) quanto após a implementação (`after_implement`),  
**Para que** divergências entre o plano e o código real sejam detectadas precocemente com pausa mandatória para decisão humana.

- **Cenário 5.1 — Modo Pré-Implementação (`after_tasks`):**
  - **Given** os artefatos `spec.md`, `plan.md` e `tasks.md` gerados,
  - **When** `/vitalia-analyze` é acionado,
  - **Then** o agente valida cobertura de requisitos, ausência de tarefas órfãs e conformidade constitucional sem inspecionar arquivos de código.

- **Cenário 5.2 — Modo Pós-Implementação (`after_implement`) e Git Diff em 3 Camadas:**
  - **Given** a conclusão do `/vitalia-spec-implement`,
  - **When** `/vitalia-analyze` é invocado,
  - **Then** o agente inspeciona o `git diff` real e classifica todos os arquivos alterados em:
    - 🟢 *Previsto no Plano*
    - 🟡 *Adaptação Correlata* (Imports, Registro Central, Call-sites ajustados)
    - 🔴 *Órfão Real / Drift de Escopo*

- **Cenário 5.3 — Detecção de Breaking Changes em Call-sites:**
  - **Given** um arquivo modificado para consumir nova função da feature,
  - **When** a chamada omite parâmetro obrigatório ou importa símbolo inexistente,
  - **Then** o agente emite finding `CRITICAL: Breaking Change Não Resolvida em <arquivo>:<linha>`.

- **Cenário 5.4 — Emissão Dual de Relatório e Pausa HITL Soberano:**
  - **Given** o encerramento das verificações do `analyze`,
  - **When** o relatório é gerado,
  - **Then** o conteúdo é exibido no chat, gravado em `specs/<feature>/Relatório de Análise e Consistência - <fase>.md` e o workflow entra em pausa mandatória aguardando aprovação soberana do usuário.

---

## 4. Requisitos Funcionais (RFC 2119)

### 4.1. Bootstrap & Runtime Global
- **FR-001 (MUST):** O `kit-bootstrap.sh` **DEVE** solicitar interativamente o diretório de instalação do kit global (default: `~/.vitalia-spec-kit`), normalizando caminhos com `~`.
- **FR-002 (MUST):** O `kit-bootstrap.sh` **DEVE** realizar instalação componente por componente, copiando estritamente os arquivos validados de `bin/`, `bin/lib/`, `extensions/`, `profiles/`, `src/`, `src/hooks/`, `templates/`, `integrations/` e `AGENTS.md`. É **PROIBIDO** o uso de comandos de espelhamento em lote cego (`cp -r source/bin/.`).
- **FR-003 (MUST):** O `kit-bootstrap.sh` **NÃO DEVE** copiar nenhum arquivo `gp_*.yaml` nem o script descontinuado `redis_detector.sh` para o kit instalado.
- **FR-004 (MUST):** O `kit-bootstrap.sh` **DEVE** gerar o shim `~/.local/bin/vitalia-install-project` contendo `export VITALIA_KIT_DIR="<caminho_escolhido>"`.

### 4.2. Resolução Dinâmica e Purga de Legado
- **FR-005 (MUST):** Todo código Python do kit **DEVE** resolver `VITALIA_KIT_DIR` na precedência estrita: (1) variável de ambiente `os.environ`, (2) leitura nativa do `.env` do projeto via `load_dotenv_native()`, (3) fallback padrão `$HOME/.vitalia-spec-kit`.
- **FR-006 (MUST):** É **TERMINANTEMENTE PROIBIDO** qualquer fallback automático ou busca no caminho legado `~/.vitalia`.
- **FR-007 (MUST):** Nenhum script em tempo de execução no kit instalado ou nos projetos hospedeiros **DEVE** assumir a existência do diretório `source/`. O diretório `source/` é exclusivo do repositório de desenvolvimento do kit.

### 4.3. Ativação de Projetos (`install-project`)
- **FR-008 (MUST):** O `install-project` **DEVE** acumular todos os eventos de execução em buffer de memória (`_VITALIA_LOG_BUFFER`).
- **FR-009 (MUST):** O `install-project` **DEVE** gravar o arquivo de log detalhado em `.vitalia/memory/data_storage/install_<timestamp>.log` se `DATA_REPO` estiver definido, ou em `./install_<timestamp>.log` na raiz caso contrário.
- **FR-010 (MUST):** Se `DATA_REPO` for informado e a pasta `.agents` existir, o `install-project` **DEVE** gerar backup em `.vitalia/memory/data_storage/.agents_<timestamp>.bak/`. Se `DATA_REPO` não for informado, **DEVE** emitir alerta explícito informando a não-realização do backup.
- **FR-011 (MUST):** O `install-project` **DEVE** remover todas as opções e referências ao Gemini CLI, gerando exclusivamente as skills da Antigravity IDE em `.agents/skills/`.
- **FR-012 (MUST):** O template `SKILL.md.template` **DEVE** iniciar rigorosamente na Linha 1 com `---` (frontmatter YAML) e apontar comandos para `{{VITALIA_KIT_DIR}}/.venv/bin/python3`.

### 4.4. Perfis, Governança Temporal e Padrão SRP
- **FR-013 (MUST):** O arquivo `grounding_domains.yaml` **DEVE** conter exatamente os 10 domínios canônicos definidos no briefing (`provedores_de_ia`, `python_packages`, `web_technologies`, `external_apis`, `security_practices`, `regulations_compliance`, `cloud_services`, `scientific_claims`, `clinical_safety`, `software_architecture`).
- **FR-014 (MUST):** Todos os 10 domínios de `grounding_domains.yaml` e 9 domínios de `dynamic_questioning.yaml` **DEVEM** conter os campos de validade temporal `last_verified_at`, `valid_until`, `validity_window_days` e `status` (`ACTIVE`/`STALE`/`DEPRECATED`).
- **FR-015 (MUST):** Todos os domínios de `grounding_domains.yaml` e `dynamic_questioning.yaml` **DEVEM** conter os campos de proveniência `last_update_source` (`url`, `source_type`, `verified_by`, `machine_id`, `summary_of_changes`) e histórico `update_history`.
- **FR-016 (MUST):** O domínio `software_architecture` em `grounding_domains.yaml` e o domínio `arquitetura_de_aplicacao` em `dynamic_questioning.yaml` **DEVEM** definir a adoção de componentes atômicos e coesos regidos pelo Princípio da Responsabilidade Única (SRP) e contratos formais explícitos.
- **FR-017 (MUST):** O arquivo `brainstorming_intents.yaml` **DEVE** conter os 7 domínios semânticos expandidos (`estrategia_produto`, `arquitetura_software`, `engenharia_web_frontend`, `infraestrutura_devops`, `seguranca_compliance`, `educacao_workshop`, `saude_clinica`).
- **FR-018 (MUST):** Todos os arquivos `.toml` em `source/extensions/` **DEVEM** ter a chave `guardian_profile = "gp_*"` removida.

### 4.5. Restauração do Dashboard de Memória (`session-consolidate`)
- **FR-019 (MUST):** O repositório **DEVE** conter `source/templates/dashboard_template.md` com a estrutura canônica rica (badges, Mermaid, tabela executiva de máquinas, sessão ativa e seções colapsáveis `<details>`), higienizada de referências a Redis.
- **FR-020 (MUST):** O motor `vitalia_context_engine.py` **DEVE** incorporar renderizador que carrega `dashboard_template.md` (resolvido dinamicamente via `resolve_kit_dir()`), preenchendo os placeholders canônicos com dados de `session_history.jsonl`, `decisions.jsonl` e `grounding_domains.yaml`.

### 4.6. Workflow de Análise e Auditoria de Código
- **FR-021 (MUST):** O workflow `spec-analyze` **DEVE** ser implementado em `source/extensions/analyze.toml`, gerando a skill `.agents/skills/vitalia-analyze/SKILL.md` sem criação de script executável de terminal.
- **FR-022 (MUST):** O `/vitalia-analyze` no modo `after_implement` **DEVE** inspecionar o Git Diff em 3 camadas e validar estaticamente aridade e imports em call-sites modificados, emitindo relatório em chat e arquivo físico local, seguido de pausa mandatória para HITL soberano.

### 4.7. Qualidade e Testabilidade
- **FR-023 (MUST):** A suíte de testes **DEVE** conter teste E2E (`tests/test_bootstrap_e2e_project.py`) que valida a instalação global, a ativação em projeto hospedeiro e a consolidação do dashboard rico em sandbox (`tmp_path`) sem instalar nada na máquina host.

---

## 5. Critérios de Sucesso (Mensuráveis e Agnósticos de Tecnologia)

- **SC-001:** 100% dos arquivos do kit global espelhados contêm caminhos relativos ou parametrizados via `VITALIA_KIT_DIR`, com zero ocorrências de `~/.vitalia` em código funcional.
- **SC-002:** O teste E2E em sandbox limpo conclui com código de retorno 0 em menos de 120 segundos, gerando todos os arquivos de configuração, log, skills e o `README.md` rico sem intervenção manual.
- **SC-003:** O arquivo `.agents/skills/vitalia-analyze/SKILL.md` é gerado com frontmatter YAML 100% válido, reconhecido nativamente pela Antigravity IDE na primeira linha (`---`).
- **SC-004:** Toda execução de `/vitalia-analyze` emite o relatório físico em `specs/<feature>/Relatório de Análise e Consistência - <fase>.md` e pausa obrigatoriamente para decisão humana soberana.
- **SC-005:** 100% dos 10 domínios canônicos de `grounding_domains.yaml` possuem data de validade futura, URL oficial autoritativa declarada e rastro auditável.
- **SC-006:** A execução de `vitalia_context_engine.py --action consolidate` gera `README.md` contendo todos os badges, diagrama Mermaid e seções expansíveis `<details>`, com correspondência estrita ao template.
- **SC-007:** Zero arquivos ou dependências do kit global são gravados no sistema host durante a execução dos testes automatizados.

---

## 6. Suposições Verificadas & Rastro de Pesquisa (P03)

- **PyPA Virtualenv Isolation:** Verificado em [Python venv Docs](https://docs.python.org/3/library/venv.html) em 06-11-2026. Runtime isolado garante blindagem de pacotes.
- **Single Responsibility Principle (SRP):** Verificado em [Clean Coder Blog](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) em 06-11-2026. Componentes com responsabilidade isolada e contratos formais explícitos.
- **Git Porcelains & Diff Parsing:** Verificado em [Git Diff Docs](https://git-scm.com/docs/git-diff) em 06-11-2026. `git diff -U0` fornece deltas semânticos limpos para análise estática de chamadas.
- **Mermaid.js Flowchart Syntax:** Verificado em [Mermaid Flowchart Docs](https://mermaid.js.org/syntax/flowchart.html) em 06-11-2026. Renderização nativa de topologia visual em markdown.
- **W3C Provenance Standard:** Verificado em [W3C PROV-O](https://www.w3.org/TR/prov-o/) em 06-11-2026. Metadados de proveniência temporal (`verified_by`, `source_type`, `summary_of_changes`) atendem ao padrão internacional de rastreabilidade.
