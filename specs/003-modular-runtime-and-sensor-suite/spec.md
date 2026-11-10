<!-- spec.md | Vitalia SDD v0.6.0 | 10-11-2026 14:30(GMT-04:00) -->
> **spec.md | Vitalia SDD v0.6.0 | 10-11-2026 14:30(GMT-04:00)**

# Especificação de Funcionalidade: 003-modular-runtime-and-sensor-suite

**Data de Emissão:** 10-11-2026 14:30 (GMT-04:00)  
**Status Constitucional:** EM AUDITORIA ADVERSARIAL (SUB-AGENTE SDD-JUDGE)  
**Preset SDD:** `software`  
**Autor/Agente:** Vitalia AI Spec Lead & Architect  
**Diretório Alvo:** `specs/003-modular-runtime-and-sensor-suite/`

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

### 1.1 Contexto e Justificativa
O **Vitalia SPEC Kit** é uma plataforma agêntica e determinística voltada para desenvolvimento guiado por especificações (Spec-Driven Development — SDD), projetada para operar em modelos de linguagem de fronteira (ex: família Gemini 3.x, Claude 3.x) integrados à IDE Google Antigravity e ambientes POSIX (Linux/WSL2).

Historicamente, o kit acumulou débitos conceituais e operacionais derivados de arquiteturas monolíticas legadas:
1. **Acoplamento a Serviços Externos Pesados:** Dependência operacional de servidores Redis locais e probes de porta de rede que causavam degradação e ruído no stderr.
2. **Poluição de Atenção e Sequestro de Contexto:** Injeção de matrizes de limpeza de arquivos temporários (`tmp_cleanup_matrix`) com mais de 100 linhas de metadados operacionais e prompts interativos (`[a/d/n/t]`) diretamente dentro do payload de contexto do agente (`guardian_json`), induzindo alucinações e degradação de raciocínio.
3. **Caminhos Físicos Hardcoded e Frágeis:** Ocorrências residuais de caminhos locais (`source/`, `~/.vitalia`), falhas de resolução quando caminhos configurados não existiam fisicamente em disco, e anomalias de nomenclatura redundante em geradores de skills (`vitalia-vitalia-*`).
4. **Violação de Purity do Contrato da IDE Antigravity:** Dispersão de backups, manifestos e arquivos temporários dentro da raiz de `.vitalia/` ou no diretório `.agents/skills/`, violando o contrato de descoberta progressiva (*Progressive Disclosure*) da IDE.
5. **Falta de Verificação Comportamental Contínua:** Ausência de uma suíte de sensores em tempo de execução capaz de auditar asserções de Design-by-Contract (DbC), pureza de diretórios, integridade de memória e ausência de vazamento de segredos em cada turno do pipeline.

### 1.2 Objetivo
Esta funcionalidade formaliza a **Arquitetura de Runtime Modular e Suíte de Sensores (VRSS - Vitalia Runtime Sensor Suite)** do Vitalia SPEC Kit, purificando integralmente o ciclo de execução, padronizando os 16 workflows canônicos em contratos OpenAPI 3.0 limpos, implementando a Arquitetura Sanduíche com Inverted CoT no SDD-Judge nativo, garantindo isolamento total de filesystem puro (sem Redis local) e estabelecendo a suíte de 5 sensores de runtime para blindagem constitucional contínua.

---

## 2. Requisitos Funcionais (Functional Requirements - FR)

### FR-001: Runtime Modular com §11 Context Lifting e Filesystem Puro
- O sistema **MUST** executar todas as rotinas de orquestração, auditoria e preservação de memória exclusivamente sobre o sistema de arquivos local (`filesystem`), sem depender de nenhum daemon externo ou serviço de cache local (ex: Redis, Memcached).
- O sistema **MUST** prover injeção dinâmica de contexto via §11 Context Lifting no arquivo transitório `.vitalia/memory/data_storage/context/<session_id>/<workflow>_<timestamp>_<hash>.json`, contendo a constituição integral sem poda de artigos.
- O sistema **MUST** registrar e carregar variáveis de ambiente e diretórios operacionais de forma dinâmica via resolução centralizada e defensiva (`kit_env_bootstrap`).

### FR-002: Suíte de Sensores em Runtime - VRSS (Vitalia Runtime Sensor Suite)
O sistema **MUST** implementar e orquestrar 5 sensores modulares independentes acionáveis via CLI e ganchos de pipeline:
1. **Sensor de Pureza (`sensor_purity.py`):** Valida se o diretório `.agents/skills/` contém estritamente subpastas imediatas contendo um único arquivo `SKILL.md` com frontmatter YAML válido (`name` e `description`), atestando ausência absoluta de arquivos órfãos, links simbólicos quebrados ou pastas ocultas (`.trash`, `.backup`).
2. **Sensor de Contratos DbC (`sensor_contract_dbc.py`):** Valida em tempo real se os arquivos JSON gerados em `data_storage/context/` cumprem rigorosamente as precondições e pós-condições estipuladas no contrato TOML do workflow correspondente e os schemas OpenAPI 3.0 aplicáveis.
3. **Sensor de Integridade de Memória (`sensor_memory_ledger.py`):** Valida a integridade do ledger 3-Tier em `.vitalia/memory/`, certificando que os shards estão ordenados de forma estritamente decrescente por `last_sync` (`shards[0]` é a estação ativa mais recente) e sem colisões de hash.
4. **Sensor de Prevenção de Vazamento e Tokens (`sensor_tokens_leak.py`):** Varre os payloads de contexto e artefatos gerados para assegurar conformidade com P06 (zero segredos/chaves de API) e P07 (sanitização de dados sensíveis), alertando se tokens desnecessários excederem os limites do perfil de hardware.
5. **Sensor de Higiene de Caminhos (`sensor_path_hygiene.py`):** Verifica se nenhum caminho físico absoluto local da máquina de desenvolvimento (tais como `source/`, `/home/andre/.vitalia`, `/tmp/vitalia`) está inserido no código-fonte, prompts, schemas ou artefatos gerados.

### FR-003: Contratos Formais Design-by-Contract (DbC) para os 16 Workflows Canônicos
- O sistema **MUST** padronizar as definições dos 16 workflows centrais do ciclo SDD (`session-start`, `spec-specify`, `judge`, `spec-plan`, `spec-tasks`, `task-verifier`, `spec-implement`, `analyze`, `converge`, `clarify`, `research`, `session-end`, `session-consolidate`, `brainstorming`, `route`, `architect`) em arquivos `.toml` declarativos em `extensions/`.
- Cada extensão TOML **MUST** explicitar:
  - `meta`: versão, perfis de modelo e hardware (`frontier`), domain gates;
  - `tools`: listas de ferramentas requeridas (`required`) e opcionais (`optional`);
  - `context`: caminhos exatos de leitura (`reads`) e escrita (`writes`);
  - `variables`: mapeamento estrito de parâmetros de entrada e saída;
  - `transport`: meio de transporte (`filesystem`) e serialização;
  - `guardian`: profile do guardião e prompt de missão estruturado.

### FR-004: Inverted Chain-of-Thought e Sanduíche Constitucional no SDD-Judge Nativo
- O SDD-Judge **MUST** ser executado nativamente como Sub-Agente na IDE Antigravity, erradicando qualquer dependência de CLI legada de julgamento (`sdd_judge.py` no terminal).
- O SDD-Judge **MUST** aplicar a técnica de **Inverted Chain-of-Thought (Inverted CoT)**: analisar exaustivamente as evidências, princípios constitucionais e asserções antes de emitir a decisão final (`PASS`, `WARN` ou `BLOCK`).
- Toda saída de auditoria do juiz **MUST** ser persistida fisicamente no arquivo `specs/{FEATURE}/Relatório de Inspeção - {mode}.md`, contendo a tabela de conformidade de artigos, justificativas objetivas e recomendações de remediação.

### FR-005: Socratic Gate com Interrupção HITL Soberana e Seleção de Decisão
- Em pontos de inflexão, ambiguidades críticas de escopo ou transições de fase, os workflows **MUST** interromper o fluxo autônomo e renderizar o componente **Socratic Gate** no rodapé da interação.
- O Socratic Gate **MUST** apresentar no máximo 3 perguntas focadas, oferecendo opções estruturadas em tabela (`Option A`, `Option B`, `Custom`) detalhando as implicações de cada escolha.
- O agente **MUST NOT** realizar inferências não autorizadas ou prosseguir arbitrariamente sem a confirmação e seleção explícita do usuário (HITL Soberano).

### FR-006: Dinamicidade Constitucional sem Números Mágicos
- O sistema de governança constitucional **MUST** carregar dinamicamente os princípios (`P00` a `P17`) a partir da fonte declarada em `guardian_json.sources.constitution.principles`.
- É terminantemente proibido o uso de números mágicos hardcoded (como contadores estáticos de regras, listas fixas de IDs em loops de validação ou dicionários estáticos de severidades) no código de verificação ou nos testes.

### FR-007: Centralização e Conformidade Estrita de Schemas em OpenAPI 3.0 Limpo
- Todos os contratos de dados e schemas JSON do kit **MUST** residir centralizados no diretório `source/src/schemas/`.
- Todos os schemas JSON **MUST** adotar estritamente o subset OpenAPI 3.0 Limpo, sendo terminantemente proibida a inclusão de meta-campos incompatíveis com compiladores REST e ferramentas de LLM (tais como `$schema`, `title`, e `additionalProperties: false`).
- Os artefatos de dados e contextos gerados em tempo de execução **MUST** conter dados planos em conformidade com seus respectivos schemas.

### FR-008: Utilitário Autônomo de Faxina e Manutenção de Contexto (`vitalia_tmp_cleanup.py`)
- O sistema **MUST** disponibilizar um utilitário CLI independente (`vitalia_tmp_cleanup.py`) para manutenção, expurgo e arquivamento de contextos expirados e arquivos de log.
- O utilitário **MUST** operar de forma autônoma fora do pipeline de execução dos agentes, provendo interface didática com `--help`, relatórios de economia de espaço em disco e modo interativo seguro de confirmação.

### FR-009: Roteiro e Automação de Instalação e Testes em Ambiente Limpo (WSL2/Linux)
- O sistema **MUST** prover um script instalador idempotente (`install.sh`) capaz de configurar o ambiente isolado do kit (virtualenv, dependências mínimas, permissões de binários e symlinks) em qualquer distribuição Linux ou ambiente WSL2.
- O sistema **MUST** incluir suíte de testes de instalação validando a inicialização em diretório limpo (`$HOME/.vitalia-test-kit`), atestando isolamento absoluto de dependências do projeto hospedeiro.

### FR-010: Persistência de Backups e Manifestos em `data_storage` (Camada 4)
- Todos os backups automáticos de skills gerados durante atualizações ou instalações **MUST** ser gravados estritamente no diretório `<project_root>/.vitalia/memory/data_storage/backups/skills/`.
- O arquivo de manifesto de integridade e hashes SHA-256 (`.vitalia-manifest`) **MUST** ser persistido estritamente em `<project_root>/.vitalia/memory/data_storage/manifests/.vitalia-manifest`.
- A raiz de `.vitalia/` e o diretório `.agents/skills/` **MUST NOT** conter arquivos ocultos ou manifestos soltos.

### FR-011: Purga Incondicional da Matriz Temporária de Atenção no Runtime
- O gerador de contexto de runtime (`vitalia_hook_runner.py`) **MUST NOT** injetar a matriz de arquivos temporários (`tmp_cleanup_matrix`) no payload `guardian_json`.
- O payload de contexto entregue aos agentes de workflow **MUST** conter exclusivamente a constituição, os perfis de grounding ativos, as diretivas do workflow e os metadados de execução da sessão.

### FR-012: Invariante Estrita de Pureza de Caminhos e Erradicação de Hardcodes
- Nenhum caminho físico absoluto do ambiente de desenvolvimento (incluindo `source/`, `/home/andre/.vitalia`, `~/.vitalia` ou referências a diretórios de máquinas específicas) pode constar hardcoded em scripts Python, scripts Bash, arquivos TOML, schemas JSON ou prompts.
- No código do kit, a referência `.vitalia/` **MUST** denotar invariavelmente o diretório local do projeto assistido (`<project_root>/.vitalia/`).
- Toda resolução de caminhos do kit **MUST** derivar dinamicamente da função `kit_env_bootstrap.resolve_kit_dir()`.

### FR-013: Resolução Defensiva do Diretório do Kit com Validação Física de Existência
- A função `resolve_kit_dir()` em `kit_env_bootstrap.py` **MUST** validar fisicamente no sistema de arquivos se o diretório apontado pela variável de ambiente `VITALIA_KIT_DIR` ou pelo arquivo `.env` existe (`candidate.exists()`).
- Caso o caminho configurado não exista fisicamente em disco, o sistema **MUST** realizar fallback defensivo para a raiz de execução do script ativo (`script_kit_root`), impedindo interrupção com `FileNotFoundError`.

### FR-014: Nomenclatura Idempotente e Pura na Geração de Skills
- O script `skill_generator.sh` **MUST** normalizar o nome de cada extensão antes de criar a pasta de skill, removendo qualquer prefixo `vitalia-` pré-existente (`${ext_name#vitalia-}`).
- O diretório gerado em `.agents/skills/` **MUST** adotar estritamente o formato único `vitalia-<workflow>`, garantindo 100% de idempotência contra execuções repetidas.

### FR-015: Delimitação Bounded do MVP aos 16 Workflows Canônicos
- O escopo de entrega do MVP da Spec 003 compreende **estrita e exclusivamente os 16 workflows canônicos centrais**.
- Extensões complementares ou verticais auxiliares (`pair.toml`, `debug.toml`, `review.toml`, `medical-gate.toml`) permanecem catalogadas e desacopladas, sendo expressamente reservadas para especificações incrementais subsequentes.

---

## 3. Requisitos Não-Funcionais (Restrições e Diretrizes)

### NFR-001: Purity & Progressive Disclosure na IDE Antigravity
O kit deve cumprir o princípio de revelação progressiva da IDE. No estado de repouso (turn zero), o diretório `.agents/skills/` deve expor exclusivamente metadados essenciais no frontmatter YAML do `SKILL.md`. Zero arquivos órfãos, backups ou metadados de depuração podem ser expostos na árvore de skills.

### NFR-002: Eficiência e Limpeza de Contexto (Context Hygiene)
O payload JSON de contexto entregue a cada turno de workflow não deve exceder os limites de tokens úteis com metadados dispensáveis. A eliminação de matrizes de limpeza de arquivos temporários deve reduzir o ruído cognitivo em pelo menos 100 linhas por invocação.

### NFR-003: Determinismo e Idempotência
Todas as operações de bootstrapping, geração de skills, checagem de sensores e criação de backups devem ser 100% idempotentes. Executar o processo N vezes consecutivas deve produzir o mesmo estado exato sem duplicidades ou efeitos colaterais.

### NFR-004: Conformidade Constitucional e Formatação P04
Todos os arquivos criados ou modificados devem exibir na linha 1 o cabeçalho de timestamp em fuso horário imutável GMT-04:00 (`DD-MM-YYYY HH:MM:SS(GMT-04:00)`), acompanhado de repetição em formato visível na linha 2 para documentos markdown.

### NFR-005: Isolamento de Runtime (Zero Network & Zero Local Daemons)
O kit deve operar em ambientes com ou sem acesso à rede externa durante a execução de ferramentas de sandbox padrão, sem qualquer tentativa de conexão a portas locais de bancos ou caches (Redis 6379 banido).

---

## 4. Histórias de Usuário (User Stories)

### US1: Engenheiro Executa Workflows com Confiabilidade e Contexto Limpo
**Como um** Engenheiro de Software ou Pesquisador utilizando a IDE Antigravity,  
**Eu quero** acionar os comandos de workflow (`/vitalia-*`) e receber prompts focados e livres de ruídos temporários e logs de portas,  
**Para que** o agente mantenha foco cognitivo total na tarefa técnica sem alucinações ou perda de atenção.

### US2: Arquiteto Governa o Sistema com Sensores Contínuos (VRSS)
**Como um** Tech Lead ou Arquiteto de Software,  
**Eu quero** executar a suíte de sensores de runtime (`sensor_purity`, `sensor_contract_dbc`, etc.),  
**Para que** violações de contratos de diretório, vazamento de segredos ou corrupções de memória sejam detectadas imediatamente no ciclo de desenvolvimento.

### US3: Operador Instala o Kit em Máquina Nova sem Falhas
**Como um** Desenvolvedor configurando uma nova estação de trabalho Linux/WSL2,  
**Eu quero** executar o instalador `install.sh` de forma autônoma e segura,  
**Para que** o ambiente do kit seja configurado com resolução defensiva de diretórios e nomenclatura padronizada de skills sem intervenções manuais.

---

## 5. Critérios de Aceite (Acceptance Criteria - Given / When / Then)

### Cenário 1: Invocação de Workflow sem Poluição de Atenção (FR-001, FR-011)
- **Dado que** o usuário aciona qualquer um dos 16 workflows canônicos (ex: `/vitalia-spec-specify`),
- **Quando** o hook runner (`vitalia_hook_runner.py`) compilar o contexto transitório em `data_storage/context/`,
- **Então** o payload `guardian_json` não deve conter a chave `tmp_cleanup_matrix`, e nenhuma tentativa de conexão com a porta 6379 do Redis deve ocorrer no log de execução.

### Cenário 2: Validação de Pureza da Árvore de Skills pelo VRSS (FR-002, NFR-001)
- **Dado que** o sensor `sensor_purity.py` é executado sobre a pasta `.agents/skills/`,
- **Quando** a árvore for analisada,
- **Então** ele deve atestar que cada subdiretório contém exatamente um `SKILL.md` com YAML frontmatter válido, e reportar erro bloqueante caso encontre arquivos soltos, pastas `.trash` ou manifestos residuais.

### Cenário 3: Localização de Backups e Manifestos na Camada 4 (FR-010)
- **Dado que** o script `skill_generator.sh` ou `agent_preserver.sh` realiza uma atualização de skills,
- **Quando** a operação for concluída,
- **Então** os arquivos de backup devem residir estritamente em `.vitalia/memory/data_storage/backups/skills/` e o `.vitalia-manifest` deve ser gravado em `.vitalia/memory/data_storage/manifests/`, mantendo a raiz de `.vitalia/` perfeitamente limpa.

### Cenário 4: Resolução Defensiva do Diretório do Kit (FR-012, FR-013)
- **Dado que** a variável de ambiente `VITALIA_KIT_DIR` ou o `.env` aponte para um caminho inexistente em disco (ex: `/caminho/inexistente`),
- **Quando** `kit_env_bootstrap.resolve_kit_dir()` for executado por qualquer utilitário do kit,
- **Então** o sistema deve detectar que o candidato não existe fisicamente e retornar a raiz do kit executável ativo (`script_kit_root`) sem emitir `FileNotFoundError`.

### Cenário 5: Idempotência na Nomenclatura de Skills (FR-014)
- **Dado que** o instalador processa arquivos de extensão que já contenham o prefixo `vitalia-` (ex: `vitalia-route.toml`),
- **Quando** `skill_generator.sh` gerar a pasta de destino em `.agents/skills/`,
- **Então** o diretório resultante deve ser exatamente `vitalia-route`, sem duplicações anômalas como `vitalia-vitalia-route`.

### Cenário 6: Auditoria Adversarial Inverted CoT no SDD-Judge (FR-004)
- **Dado que** um artefato SDD é submetido à auditoria pelo Sub-Agente SDD-Judge,
- **Quando** o juiz avaliar as evidências contra os princípios constitucionais dinâmicos,
- **Então** ele deve primeiro detalhar a análise e raciocínio de cada artigo antes de proferir a decisão final, e salvar o relatório em `specs/{FEATURE}/Relatório de Inspeção - {mode}.md`.

### Cenário 7: Interrupção Socrática com Opções Estruturadas (FR-005)
- **Dado que** um workflow detecta uma divergência crítica de arquitetura ou requisito,
- **Quando** a resposta for retornada ao usuário,
- **Então** ela deve conter um Socratic Gate no rodapé com no máximo 3 opções tabuladas (`Option A`, `Option B`, `Custom`) e parar a execução aguardando decisão humana soberana.

---

## 6. Critérios de Sucesso Mensuráveis (Success Criteria - SC)

- **SC-001 (Zero Leak & Zero Residue):** 100% dos backups e manifestos são gravados na Camada 4 (`data_storage/`), garantindo 0 arquivos residuais ou ocultos na raiz de `.vitalia/` e em `.agents/skills/`.
- **SC-002 (Context Attention Recovery):** Redução comprovada de 100% das linhas de metadados da `tmp_cleanup_matrix` dentro de `guardian_json`, diminuindo a carga cognitiva e eliminando prompts alucinatórios de expurgo durante o raciocínio do modelo.
- **SC-003 (Sensor Suite Coverage):** A suíte de sensores VRSS executa 5 verificações automatizadas de integridade com taxa de sucesso de 100% em cenários nominais e detecção de 100% de anomalias injetadas em testes de falsificação.
- **SC-004 (Clean Path Invariant):** 0 ocorrências de caminhos absolutos hardcoded locais (`source/`, `/home/andre/.vitalia`, `~/.vitalia`) em todos os scripts Python, Bash, TOML e schemas do produto.
- **SC-005 (Defensive Bootstrap Reliability):** 100% de taxa de recuperação com fallback defensivo para `script_kit_root` quando `VITALIA_KIT_DIR` apontar para caminhos inexistentes, com 0 quebras por `FileNotFoundError`.
- **SC-006 (Skill Generation Idempotency):** 100% das skills em `.agents/skills/` geradas com o prefixo canônico único `vitalia-<workflow>`, sem duplicações após múltiplas execuções consecutivas.
- **SC-007 (Canonical Workflow Integrity):** 100% dos 16 workflows canônicos possuem contratos TOML válidos com schemas em conformidade estrita com OpenAPI 3.0 Limpo.
- **SC-008 (TDD Falsification Compliance):** 100% das novas lógicas e correções de defeitos cobertas pela Matriz de Testes P05 nas modalidades `[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]` e `[TEST:MIGRATION]`.

---

## 7. Suposições Verificadas (Grounding P03)

- **"OpenAPI 3.0.3 Specification":** Verificado em https://spec.openapis.org/oas/v3.0.3.html em 07-11-2026. A especificação restringe schemas compatíveis com LLM tooling a subsets limpos, banindo meta-campos de rascunhos mais recentes do JSON Schema como `$schema` e `title` redundantes.
- **"Google Antigravity Customization Architecture & Progressive Disclosure":** Verificado na documentação embutida em `/home/andre/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md` em 10-11-2026. A IDE escaneia no turn zero unicamente subdiretórios em `.agents/skills/` contendo arquivos `SKILL.md` com YAML frontmatter (`name` e `description`). Arquivos ocultos, symlinks quebrados ou pastas adicionais provocam advertências de parsing e ruído de indexação.
- **"OWASP Top 10 for Large Language Model Applications (2025)":** Verificado em https://owasp.org/www-project-top-10-for-large-language-model-applications em 07-11-2026. Confirma os riscos LLM01:2025 (Prompt Injection) e LLM06:2025 (Excessive Agency), exigindo mínimo privilégio, descarte de outputs não validados e contenção estrita de runtime.
- **"Python Pathlib & Filesystem Operations (Python 3.10+)":** Verificado na documentação oficial da biblioteca padrão Python (https://docs.python.org/3/library/pathlib.html). Confirma a robustez e idempotência dos métodos `Path.resolve()`, `Path.exists()` e `Path.mkdir(parents=True, exist_ok=True)` para substituição definitiva de manipulações frágeis de strings de paths.

---

## 8. Comportamentos Existentes a Preservar & Defeitos a Reproduzir

### Comportamentos a Preservar
1. **Preservação do Mecanismo §11 Context Lifting:** O isolamento e injeção do arquivo transitório `data_storage/context/.../workflow_timestamp_hash.json` continua sendo o meio primário de entrega de contexto do hook runner para a IDE.
2. **Preservação da Constituição Integral sem Poda:** A injeção integral de `profiles/constitution.yaml` em runtime continua obrigatória, assegurando raciocínio não-mutilado em modelos com ampla janela de contexto.
3. **Preservação do Formato 3-Tier de Memória:** O ledger em `.vitalia/memory/` com `SESSION_HISTORY.md`, `session_ledger.json` e sharding descentralizado permanece como a base de rastreabilidade temporal.

### Defeitos a Reproduzir nos Testes de Falsificação (`[TEST:BUGFIX]` / `[TEST:MIGRATION]`)
1. **Defeito 1 (Injeção de `tmp_cleanup_matrix`):** O teste de regressão deve comprovar que a injeção da matriz poluía o `guardian_json` com mais de 100 linhas e que, após a alteração, a chave inexiste no JSON de contexto.
2. **Defeito 2 (Crash por Diretório Inexistente em `kit_env_bootstrap`):** O teste deve configurar `VITALIA_KIT_DIR=/path/que/nao/existe` e comprovar que o código antigo lançava `FileNotFoundError`, enquanto o código corrigido faz fallback seguro para a raiz do kit executável.
3. **Defeito 3 (Duplicação de Prefixo em `skill_generator.sh`):** O teste deve processar uma extensão nomeada `vitalia-route.toml` e demonstrar que a versão antiga gerava `.agents/skills/vitalia-vitalia-route`, enquanto a versão corrigida gera `.agents/skills/vitalia-route`.
4. **Defeito 4 (Poluição de Backups na Raiz de `.vitalia`):** O teste deve evidenciar que versões antigas gravavam backups soltos e validar que a nova versão grava estritamente em `.vitalia/memory/data_storage/backups/skills/`.

---

## 9. Fora do Escopo (Out of Scope)

1. **Implementação dos Workflows Auxiliares:** Workflows de suporte (`pair.toml`, `debug.toml`, `review.toml`, `medical-gate.toml`) permanecem catalogados para specs posteriores; não fazem parte do entregável do MVP da Spec 003.
2. **Containers e Daemons de Aplicações de Terceiros:** Não é escopo da Spec 003 configurar serviços de banco de dados ou mensageria de projetos assistidos (ex: Postgres, pgvector, Evolution API de aplicações gerenciadas). O kit SDD opera exclusivamente sobre filesystem puro.
3. **Refatoração Visual da IDE Antigravity:** A interface gráfica da IDE não é modificada; o kit se adapta com pureza aos pontos de extensão nativos providos pela ferramenta.

---

## 10. Socratic Gate (Hard Stop Constitucional)

> [!IMPORTANT]
> **GATE SOCRÁTICO DE VALIDAÇÃO DE ESCOPO (HITL SOBERANO)**  
> A especificação acima abrange os 15 requisitos funcionais (`FR-001` a `FR-015`), os 8 critérios de sucesso (`SC-001` a `SC-008`), o corpus dos 8 documentos conceituais de `specs/003-modular-runtime-and-sensor-suite/` e as diretivas da Constituição SDD v0.6.0.
> 
> Antes de avançarmos para o planejamento técnico (`/vitalia-spec-plan`), confirme a aprovação desta especificação formal ou indique ajustes necessários.

