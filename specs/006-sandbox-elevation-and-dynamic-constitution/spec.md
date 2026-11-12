<!-- spec.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:35(GMT-04:00) -->
> **spec.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:35(GMT-04:00)**

# Especificação Funcional — Spec 006: Elevação Proativa de Sandbox, Governança Agnóstica e Minimalista de Agentes, Purga de Variáveis Redundantes, Padrão Afirmativo e Saneamento Dinâmico

- **Data:** 11-11-2026
- **Versão:** 0.0.1
- **Autor/Agente:** Vitalia SPEC Kit Architect & Requirements Engineer
- **Feature:** `specs/006-sandbox-elevation-and-dynamic-constitution`
- **Status:** DRAFT (Submetido à Auditoria `/vitalia-judge --mode=specify` e Aprovação HITL)
- **Fontes Canônicas Obrigatórias:**
  - [`specs/006-sandbox-elevation-and-dynamic-constitution/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/006-sandbox-elevation-and-dynamic-constitution/research-brainstorming.md)
  - [`docs/adr/ADR-0005-proactive-sandbox-elevation-and-agnostic-governance.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0005-proactive-sandbox-elevation-and-agnostic-governance.md)
  - [`specs/006-sandbox-elevation-and-dynamic-constitution/regencia-architect-plano-turno.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/006-sandbox-elevation-and-dynamic-constitution/regencia-architect-plano-turno.md)

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

### 1.1 Problema de Negócio e Engenharia
Durante a validação prática do ciclo SDD e a inicialização de sessões de trabalho, foram identificados seis pontos de atrito cognitivo e operacional que comprometem a fluidez do kit:

1. **Colisão Inicial de Sandbox da IDE (Código 127):** O sandbox padrão da IDE Antigravity restringe o isolamento de montagem ao diretório do workspace (`project_root`). Comandos disparados inicialmente pelo agente em `BypassSandbox: false` falham com `Exit code 127 (No such file or directory)` ao tentar referenciar o interpretador do kit em `~/.vitalia-spec-kit/.venv/bin/python3`. A regra do sistema estabelece que o sandbox pode ser contornado *"unless mentioned otherwise"*.
2. **Contaminação Conceitual de Topologia e Acoplamento no `AGENTS.md`:** O `AGENTS.md` apresentava uma "Topologia de 4 Camadas", citando a pasta `source/` que só existe no repositório de desenvolvimento e não existe no kit instalado no cliente. Além disso, regras específicas de software (como TDD e Falsificação) poluíam a governança geral de agentes, que deve atender a múltiplos especialistas (médicos, acadêmicos, design).
3. **Âncoras Semânticas Negativas (Efeito Elefante Rosa):** Citar ferramentas inexistentes (como `sdd_judge.py`) ou proibir ações específicas (`kit-bootstrap.sh`) atua como gatilho cognitivo, induzindo modelos de linguagem a tentar executar os itens citados durante cenários de falha.
4. **Redundância e Acoplamento da Variável `VITALIA_KIT_DIR` no `.env`:** O instalador injetava caminhos absolutos locais do usuário no `.env` do projeto cliente, criando dependências desnecessárias quando o próprio módulo `kit_env_bootstrap.resolve_kit_dir()` já resolve a localização física intrínseca do kit.
5. **Números Mágicos Estáticos (Violação do FR-006):** Presença de faixas fixas (`P00–P17`, `16 workflows`, `14 lentes`, `6 catálogos`) em 26 pontos de código e prompts, engessando a extensibilidade do sistema.
6. **Violações ao Padrão Afirmativo ("Say what to do instead of what not to do"):** Proibições negativas na constituição e perfis criam ambiguidade comportamental e aumentam a taxa de alucinação dos modelos.

### 1.2 Declaração de Impacto e Princípios Constitucionais (P00, P01, P02, P03, P04, P05, P11, P16)
- **Bem-Estar Humano Primeiro (P00):** Elimina a frustração do usuário com erros 127 repetidos em primeiro turno e comandos truncados.
- **Inviolabilidade do Pipeline SDD (P01):** Condução formal specify ➔ plan ➔ tasks ➔ implement ➔ converge com auditoria constitucional.
- **Validação Centrada no Usuário (P02):** Interface CLI e skills orientadas a zero-friction no terminal.
- **Protocolo de Grounding Externo (P03):** Confirmação mandatória de links ativos (HTTP 200) e leitura integral prévia.
- **Integridade Temporal GMT-04:00 (P04):** Cabeçalho e fuso Cuiabá em todos os artefatos.
- **Matriz de Falsificação Comportamental (P05):** Estratégia de testes nas 4 modalidades ([TEST:NEW], [TEST:BUGFIX], [TEST:REFACTOR], [TEST:MIGRATION]).
- **Agnosticismo de Hardware e Ambiente (P11):** Auto-localização intrínseca sem caminhos desnecessários no `.env`.
- **Integridade de Artefatos e Mermaid (P16):** Labels entre aspas duplas e inserções cronológicas corretas.

---

## 2. Requisitos Funcionais

### FR-001: Elevação Proativa de Sandbox na Invocação de Workflows
O sistema **MUST** assegurar que qualquer comando de workflow disparado por skill na IDE Antigravity execute inicialmente sem bloqueios de sandbox:
- **FR-001.1 (Template de Skill):** O arquivo `source/integrations/antigravity/SKILL.md.template` **MUST** prescrever no Passo 1 a execução com elevação de sandbox mandatória e inicial (`BypassSandbox: true`), acionando a exceção formal das diretrizes da IDE ("unless mentioned otherwise").
- **FR-001.2 (Sincronização de Skills Existentes):** O gerador `source/bin/lib/skill_generator.sh` e todas as skills compiladas em `.agents/skills/*/SKILL.md` **MUST** incorporar a redação imperativa de elevação no Passo 1, eliminando a ocorrência do código 127 no primeiro turno de qualquer workflow.

### FR-002: Governança do `AGENTS.md` Minimalista (~35 linhas) e Agnóstico de Domínio
O sistema **MUST** fornecer um manifesto de agentes enxuto, neutro e desacoplado de regras de implementação de código:
- **FR-002.1 (Agnosticismo e Tamanho Enxuto):** `source/AGENTS.md` e `.agents/AGENTS.md` **MUST** ser reformulados em aproximadamente 35 linhas, focando na orquestração de especialistas e Context Lifting (§11).
- **FR-002.2 (Expurgo de Jargões de Software):** Regras especializadas de desenvolvimento (como TDD, Red-Green-Refactor e Matriz de Falsificação) **MUST** residir exclusivamente na Constituição (`constitution.yaml`), sendo expurgadas do `AGENTS.md`.
- **FR-002.3 (Neutralização de Âncoras Semânticas Negativas):** O texto do `AGENTS.md` **MUST** omitir qualquer menção a ferramentas inexistentes (como `sdd_judge.py`) ou proibições a comandos (como `kit-bootstrap.sh`).
- **FR-002.4 (Topologia Real de 3 Camadas no Cliente):** O `AGENTS.md` **MUST** descrever estritamente as 3 Camadas Reais presentes no cliente instalado:
  - Camada 1: Projeto do Usuário (`<project_root>/`);
  - Camada 2: Kit Vitalia Instalado (`<kit_dir>/`, padrão `~/.vitalia-spec-kit/`);
  - Camada 3: Memória Persistente do Projeto (`<project_root>/.vitalia/`).
  A pasta `source/` **MUST** ser referida exclusivamente como ambiente do repositório de desenvolvimento.
- **FR-002.5 (Idempotência e Prevenção de Duplicação em `agent_preserver.sh`):** O módulo `source/bin/lib/agent_preserver.sh` e o instalador `install-project` **MUST** garantir idempotência estrita ao atualizar `.agents/AGENTS.md`. Caso o arquivo de destino já contenha marcadores `<!-- VITALIA:KIT:START -->` e `<!-- VITALIA:KIT:END -->` duplicados, o algoritmo **MUST** deduplicar e sanitizar o arquivo de modo a manter uma única e exclusiva instância do bloco gerenciado pelo kit, preservando regras customizadas do usuário sem qualquer repetição.

### FR-003: Purga da Injeção de `VITALIA_KIT_DIR` do `.env` do Cliente
O sistema **MUST** manter o `.env` do projeto cliente limpo de variáveis desnecessárias do kit:
- **FR-003.1 (Purga no Instalador):** O script `source/bin/lib/env_manager.sh` **MUST** cessar a injeção da variável `VITALIA_KIT_DIR` no arquivo `.env` do projeto cliente durante `install-project`.
- **FR-003.2 (Auto-Localização Intrínseca):** O módulo `source/src/kit_env_bootstrap.py` **MUST** resolver o diretório do kit com segurança a partir de sua localização física em disco (`Path(__file__).resolve().parent.parent`) sem depender da variável `VITALIA_KIT_DIR` no `.env`.

### FR-004: Saneamento Dinâmico de Números Mágicos (FR-006 em 26 Pontos)
O sistema **MUST** erradicar contadores e faixas estáticas no código, prompts e testes:
- **FR-004.1 (Mapeamento e Substituição nos 26 Pontos):** Todas as referências fixas a contagens (`P00–P17`, `P00 a P20`, `16 workflows`, `14 lentes`, `6 catálogos`) mapeadas nos 26 pontos específicos do sistema **MUST** ser substituídas por resoluções dinâmicas baseadas no tamanho das estruturas em memória (`len(principles)`, `len(extensions)`, `len(profiles)`) ou por redações semânticas abertas (*"integralidade dos princípios constitucionais ativos"*).

### FR-005: Adoção Integral do Padrão Afirmativo ("Say what to do instead of what not to do")
O sistema **MUST** expressar suas regras através de orientações afirmativas e comportamentos esperados:
- **FR-005.1 (Reformulação da Constituição e Perfis):** Todas as ocorrências de proibições e formulações negativas em `source/profiles/constitution.yaml`, `source/profiles/gp_*.yaml` e `source/extensions/*.toml` **MUST** ser convertidas para prescrições afirmativas da forma desejada.
- **FR-005.2 (Padronização do Princípio P03):** O Princípio P03 **MUST** ser redigido unicamente como: *"Toda citação de versão, documentação, endpoint ou alegação científica exige confirmação de link ativo (HTTP 200) seguida de leitura integral da fonte."*

### FR-006: Protocolo Estrito de Grounding e Barreira Síncrona (P03)
O sistema **MUST** garantir integridade e auditoria de fontes externas:
- **FR-006.1 (Barreira Síncrona de Orquestração):** Em workflows que exigem validação de versões, documentação ou fatos científicos, o agente orquestrador **MUST** aguardar a conclusão formal do sub-agente de pesquisa antes de emitir conclusões.
- **FR-006.2 (Rastro de Pesquisa Auditável):** Todo artefato produzido que contenha dados externos **MUST** incluir seção com links validados via HTTP 200 e confirmação de leitura integral da fonte.

---

## 3. Critérios de Sucesso e Cenários BDD (Given/When/Then)

### SC-001: Execução Inicial de Skill sem Colisão de Sandbox (Código 127)
- **Given** que um usuário invoca um comando de workflow (ex: `/vitalia-session-start`) na IDE Antigravity,
- **When** o agente lê o Passo 1 do `SKILL.md` gerado,
- **Then** o comando é executado inicialmente com `BypassSandbox: true` e a execução do `vitalia_hook_runner.py` conclui com sucesso (código 0) sem gerar o erro 127.

### SC-002: Pureza, Agnosticismo e Deduplicação do `AGENTS.md`
- **Given** os arquivos `source/AGENTS.md` e `.agents/AGENTS.md`,
- **When** realizada a inspeção estrutural e de marcadores,
- **Then** o arquivo contém aproximadamente 35 linhas, declara as 3 Camadas Reais, não menciona `sdd_judge.py`, não proíbe `kit-bootstrap.sh`, delega regras de software à Constituição e possui exatamente 1 único bloco entre `<!-- VITALIA:KIT:START -->` e `<!-- VITALIA:KIT:END -->` (zero duplicações).

### SC-003: Instalação Limpa sem Poluição do `.env` do Cliente
- **Given** a execução de `install-project` em um projeto cliente limpo,
- **When** o processo de instalação é concluído,
- **Then** o arquivo `.env` do cliente NÃO contém a variável `VITALIA_KIT_DIR`, e o kit continua operando com sucesso através de `kit_env_bootstrap.resolve_kit_dir()`.

### SC-004: Extensibilidade Dinâmica sem Números Mágicos (FR-006)
- **Given** os 26 pontos saneados no sistema,
- **When** um novo princípio constitucional for adicionado a `constitution.yaml`,
- **Then** nenhum teste quebra por asserção estática de contagem (ex: `assert len == 18` ou regex procurando `P00–P17`), pois todas as validações utilizam contagens dinâmicas.

### SC-005: Conformidade Afirmativa e Barreira Síncrona de Grounding
- **Given** o acionamento de pesquisa para validação de endpoints ou alegações científicas,
- **When** o sub-agente realiza as requisições,
- **Then** apenas fontes com confirmação HTTP 200 e leitura integral constam no rastro final, e o orquestrador não emite conclusões prematuras antes da conclusão do sub-agente.

---

## 4. Suposições Verificadas & Rastro de Pesquisa

- **"Anthropic & OpenAI Prompt Engineering Guidelines":** verificado em `https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct` e `https://platform.openai.com/docs/guides/prompt-engineering` em 11-11-2026 (HTTP 200). Diretriz canônica: *"Describe the shape you want, not the hole"* e *"Say what to do instead of what not to do"*.
- **"Stanford Prompt Design Patterns":** verificado em `https://arxiv.org/abs/2307.03172` (HTTP 200).
- **"Linux Foundation AGENTS.md Standard":** verificado em `https://agents.md` em 11-11-2026 (HTTP 200).

