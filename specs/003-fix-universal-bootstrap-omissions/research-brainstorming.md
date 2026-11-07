<!-- research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:15:00(GMT-04:00) -->
> **research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:15:00(GMT-04:00)**

# SDD Briefing Canônico — Spec 003: Fix Universal Bootstrap Omissions (v0.0.1)

---

## 1. Sumário Executivo e Propósito da Spec Corretiva

Este documento estabelece as diretrizes canônicas, a análise de causa-raiz e os contratos técnicos detalhados para a **Spec 003: Fix Universal Bootstrap Omissions** no repositório **Vitalia SPEC Kit (v0.0.1)**.

Diferente de uma spec de novas capacidades, a Spec 003 é formalmente classificada como uma **Spec Corretiva de Remediação Arquitetural (`fix-*`)**. Seu propósito exclusivo é sanar as omissões estruturais, quebras de caminho, regressões visuais e falsos positivos deixados pela entrega anterior (Spec 002), transformando o instalador global (`kit-bootstrap.sh`), o ativador de projetos (`install-project`) e o motor de consolidação de contexto (`vitalia_context_engine.py`) em ferramentas 100% autônomas, auditáveis, ricas e funcionais em qualquer máquina limpa (*fresh install*).

Fica estabelecido o princípio fundamental: **eliminar o espelhamento em lote cego** de componentes. Cada componente de cada pasta é analisado individualmente, purgado de débitos legados (Redis, Celery, Ollama, VRAM), enriquecido com governança temporal exaustiva e calibrado para o ecossistema v0.0.1.

---

## 2. Root Cause Analysis (RCA) — Post-Mortem da Spec 002

Em consonância com a maturidade de engenharia e os princípios de governança do projeto, foram isoladas cinco causas-raiz para as falhas e omissões observadas após o fechamento da Spec 002:

### RCA-01: Falso Positivo em Testes Unitários de Bootstrap
- **O que ocorreu:** Os testes `test_bootstrap.py` e `test_bootstrap_idempotency.py` validaram apenas a criação do diretório global `~/.vitalia-spec-kit/`, a existência do Python no virtualenv isolado e a criação de arquivos de shim.
- **A falha:** Nenhum teste acionou o `install-project` a partir desse kit global gerado para checar a ativação em um workspace hospedeiro real. Todos os testes unitários passaram com 100% de sucesso enquanto a entrega no destino estava inoperante.
- **Regra Corretiva:** É obrigatório introduzir teste de fumaça de ponta a ponta (*End-to-End* — E2E) simulando a execução completa de `kit-bootstrap.sh` seguida de `install-project` em um diretório temporário (`tmp_path`), inspecionando a geração física de skills em `.agents/skills/` e a integridade de `AGENTS.md`. **O teste roda em sandbox; nada é instalado na máquina host atual.**

### RCA-02: Omissão por Espelhamento Manual em Lote
- **O que ocorreu:** O script `kit-bootstrap.sh` copiou manualmente de `source/` para o kit global apenas `bin/`, `extensions/`, `profiles/` e `src/` via comandos `cp -r`.
- **A falha:** Omitiu a pasta `integrations/` (contendo `SKILL.md.template`), o arquivo `AGENTS.md`, os templates de dashboard e a extensão `analyze.toml`. Quando o `install-project` rodava, avaliava `[ -f "${TEMPLATE}" ]` como falso e abortava silenciosamente a criação de todas as skills da IDE Antigravity.
- **Regra Corretiva:** Abandonar cópias em lote cegas. O `kit-bootstrap.sh` deve realizar uma instalação explícita, componente por componente, validando contratos e integridade de cada artefato instalado.

### RCA-03: Convivência Suja com Resquícios do Kit Legado (`~/.vitalia`)
- **O que ocorreu:** Múltiplos arquivos em `source/` mantinham referências duras ou fallbacks automáticos para `~/.vitalia` (o caminho antigo pré-0.0.1 que continha scripts com dependência de Redis 6379 e Postgres 5432).
- **A falha:** Na máquina de desenvolvimento, as skills legadas continuavam chamando o hook runner de `~/.vitalia`, disparando sondas degradadas de ambiente.
- **Regra Corretiva:** Purga total de qualquer menção a `~/.vitalia`. Todo o código resolve o kit via variável de ambiente `VITALIA_KIT_DIR`, leitura do `.env` do projeto ou fallback padrão para `~/.vitalia-spec-kit`.

### RCA-04: Confusão de Paradigma CLI vs. Workflows Nativos de IDE
- **O que ocorreu:** Tentativas de criar scripts executáveis no terminal (como binários `vitalia-spec-analyze`) para workflows que são nativos da IDE.
- **A falha:** Violação da Regra 6 do `AGENTS.md`. Workflows de análise e auditoria no Vitalia Kit v0.0.1 não são CLIs de terminal, mas **Slash Commands / Sub-Agentes da IDE** com Sanduíche Constitucional e HITL soberano.
- **Regra Corretiva:** `spec-analyze` é estritamente um workflow de IDE (`analyze.toml` gerando `.agents/skills/vitalia-analyze/SKILL.md`), acionado via `/vitalia-analyze`.

### RCA-05: Regressão e Empobrecimento no Dashboard de Memória (`session-consolidate`)
- **O que ocorreu:** No kit legado, a ação `session-consolidate` utilizava o template canônico `~/.vitalia/config/templates/dashboard_template.md` e o renderizador `~/.vitalia/src/rendering/dashboard_renderer.py`. Na Spec 002, ao criar `source/src/vitalia_context_engine.py` para operar em filesystem puro, a ação `consolidate` foi reescrita inline de forma simplista e rudimentar (gerando apenas uma tabela de texto simples e duas linhas de semáforo).
- **A falha:** O dashboard consolidado em `.vitalia/memory/session/README.md` perdeu completamente toda a sua riqueza visual e informativa:
  - Badges de estado (Status Ativo, Semáforo, Modo Filesystem, Sincronização GMT-04:00, Grounding Ativo).
  - Diagrama visual de topologia em Mermaid (`flowchart TD`) mostrando a conexão das estações/shards.
  - Tabela estilizada de máquinas com status visual.
  - Seção de destaque da sessão ativa com a tarefa atual e o Próximo Passo Prioritário (P0).
  - Seções expansíveis (`<details>`) para: Histórico Completo de Sessões (`session_history.jsonl`), Decisões Arquiteturais Consolidadas (`decisions.jsonl`) e Guard Rails de Grounding e Domínios (`grounding_domains.yaml`).
  - O template `dashboard_template.md` sequer foi portado para `source/` nem instalado no kit global.
- **Regra Corretiva:** Portar o template canônico higienizado para `source/templates/dashboard_template.md` (removendo referências a Redis e acoplamentos legados) e integrar o renderizador visual rico dentro do `LocalContextEngine` em `source/src/vitalia_context_engine.py`, resolvendo o template via `kit_env_bootstrap.resolve_kit_dir()`.

---

## 3. Análise Individual Exaustiva de Componentes e Contratos

### 3.1. Pasta `source/profiles/`

A pasta `profiles/` contém a inteligência estática e as regras oraculares do kit. Cada arquivo deve ser individualmente purgado e modelado:

| Componente | Função & Contrato | Débito Identificado | Ação Corretiva na Spec 003 |
| :--- | :--- | :--- | :--- |
| `gp_sdd-judge.yaml` | Perfil fatiado para VRAM 6GB | Obsoleto no v0.0.1 (Context Lifting §11 sem podas) | **Exclusão física definitiva.** Zero perfis `gp_*` no repositório e no kit instalado. |
| `dynamic_questioning.yaml` | Perguntas socráticas do Brainstorming | 100% focado em PII/PHI; condicionais hardcoded de Redis, Celery, Ollama e GPU local | Purgar menções a Redis/Celery/Ollama. Expandir para abranger arquitetura de software, design de APIs, persistência de dados, UI moderna e DevOps. Adicionar **Dimensão Temporal e Rastreabilidade de Fontes** em todos os domínios. |
| `grounding_domains.yaml` | Dicionário de domínios para verificação externa P03 | Focado em PII/PHI; domínio `hardware_specs` exige `nvidia-smi` e VRAM | Purgar `hardware_specs`. Expandir para 10 domínios exaustivos cobrindo todo o ecossistema tecnológico. Adicionar **Dimensão Temporal (`valid_until`), Status (`ACTIVE`/`STALE`) e Rastreamento de Fontes (`last_update_source`, `update_history`)**. |
| `brainstorming_intents.yaml` | Mapeamento de intenções do usuário | Restrito a saúde e workshop acadêmico | Expandir para 7 domínios abrangendo estratégias de produto, arquitetura de software, engenharia web/frontend, infraestrutura/devops, segurança/compliance, educação e saúde clínica. |
| `constitution.yaml` | Princípios P00–P18 | Estável, mas requer cláusula de validade temporal no P03 | Adicionar ao P03 a política de frescura temporal e revalidação de domínios expirados. |
| `agents_catalog.yaml` | Catálogo de agentes do ecossistema | Mapeamento de sub-agentes | Manter em conformidade OpenAPI 3.0 limpa. |
| `routing_table.yaml` | Roteamento determinístico de comandos | Rotas da IDE | Manter em sincronia com os slash commands nativos. |

---

### 3.2. Catálogo Canônico Exaustivo: `grounding_domains.yaml`

Para eliminar qualquer espaço para alucinação ou omissão na implementação, o catálogo formal conterá **10 domínios canônicos**, cada um modelado com sua governança temporal completa e rastreabilidade de fontes (P03):

```yaml
# grounding_domains.yaml | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:15:00(GMT-04:00)
schema_type: "grounding_domains"
schema_version: "0.0.1"
last_catalog_review: "06-11-2026 22:15:00(GMT-04:00)"
default_validity_days: 90

domains:
  - id: "provedores_de_ia"
    name: "Modelos e APIs de IA de Fronteira"
    description: "Nomes de modelos vigentes, janelas de contexto, depreciações, pricing de tokens e endpoints de inferência (Google Gemini, Anthropic Claude, OpenAI)."
    scope: "global"
    trigger: "blocking"
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-02-2027 22:15:00(GMT-04:00)"
    validity_window_days: 90
    status: "ACTIVE"
    last_update_source:
      url: "https://ai.google.dev/gemini-api/docs/models/gemini"
      source_type: "official_vendor_docs"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Validação da família Gemini 2.5 (Flash e Pro) como padrão ativo de fronteira. Purga de Ollama local."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://ai.google.dev/gemini-api/docs/models/gemini"
        verified_by: "session_20261106_2215"
        summary: "Atualização para modelos de fronteira v0.0.1; purga de Ollama local."
    authoritative_sources:
      - "https://ai.google.dev/gemini-api/docs/models/gemini"
      - "https://docs.anthropic.com/en/docs/about-claude/models"
      - "https://platform.openai.com/docs/models"

  - id: "python_packages"
    name: "Ecossistema e Pacotes Python"
    description: "Versões de dependências, compatibilidade com Python >=3.10, changelogs, breaking changes e avisos de segurança no PyPI."
    scope: "global"
    trigger: "blocking"
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-02-2027 22:15:00(GMT-04:00)"
    validity_window_days: 90
    status: "ACTIVE"
    last_update_source:
      url: "https://pypi.org"
      source_type: "package_repository"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Validação de dependências essenciais: pyyaml, jinja2, pytest, jsonschema."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://pypi.org"
        verified_by: "session_20261106_2215"
        summary: "Revisão e pinagem mínima para ambiente virtual isolado (.venv)."
    authoritative_sources:
      - "https://pypi.org"
      - "https://github.com/advisories"

  - id: "web_technologies"
    name: "Tecnologias Web, Frontend e Estilização"
    description: "Padrões de HTML5 semântico, Vanilla CSS moderno (tokens, CSS Grid, Flexbox, glassmorphism), bundlers (Vite), SEO e boas práticas de acessibilidade."
    scope: "global"
    trigger: "warning"
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-05-2027 22:15:00(GMT-04:00)"
    validity_window_days: 180
    status: "ACTIVE"
    last_update_source:
      url: "https://developer.mozilla.org/en-US/docs/Web/CSS"
      source_type: "standards_documentation"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Definição de Vanilla CSS moderno e Vite como padrão de excelência visual sem dependência forçada de Tailwind."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://developer.mozilla.org/en-US/docs/Web/CSS"
        verified_by: "session_20261106_2215"
        summary: "Inclusão formal de padrões web modernos no kit."
    authoritative_sources:
      - "https://developer.mozilla.org"
      - "https://vitejs.dev"
      - "https://web.dev"

  - id: "external_apis"
    name: "APIs Externas e Protocolos de Integração"
    description: "Contratos de endpoints RESTful, GraphQL, gRPC, fluxos de autenticação (OAuth 2.0 / OIDC), rate limiting e webhooks."
    scope: "global"
    trigger: "blocking"
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-02-2027 22:15:00(GMT-04:00)"
    validity_window_days: 90
    status: "ACTIVE"
    last_update_source:
      url: "https://www.rfc-editor.org/rfc/rfc6749"
      source_type: "standards_rfc"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Padronização de contratos OpenAPI 3.0 e fluxos OAuth2/JWT."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://www.rfc-editor.org/rfc/rfc6749"
        verified_by: "session_20261106_2215"
        summary: "Definição de contratos de API sem amarras com brokers legados."
    authoritative_sources:
      - "https://spec.openapis.org/oas/latest.html"
      - "https://www.rfc-editor.org"

  - id: "security_practices"
    name: "Segurança de Aplicação e Vulnerabilidades (CVE)"
    description: "Vulnerabilidades conhecidas, CVEs, diretrizes OWASP Top 10 e OWASP Top 10 for LLM Applications 2025."
    scope: "global"
    trigger: "blocking"
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-01-2027 22:15:00(GMT-04:00)"
    validity_window_days: 60
    status: "ACTIVE"
    last_update_source:
      url: "https://owasp.org/www-project-top-10-for-large-language-model-applications"
      source_type: "security_standard"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Alinhamento com OWASP Top 10 LLM 2025: injeção de prompt, vazamento de dados sensíveis e design inseguro."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://owasp.org/www-project-top-10-for-large-language-model-applications"
        verified_by: "session_20261106_2215"
        summary: "Inclusão de verificações de segurança em nível de oráculo Guardian."
    authoritative_sources:
      - "https://owasp.org"
      - "https://nvd.nist.gov"
      - "https://cve.mitre.org"

  - id: "regulations_compliance"
    name: "Regulações, Privacidade e Compliance Legal"
    description: "LGPD (Lei 13.709/2018), GDPR, HIPAA Security Rule e EU AI Act. Regras para tratamento de dados pessoais (PII) e de saúde (PHI)."
    scope: "global"
    trigger: "blocking"
    constitution_principles: ["P07", "P09", "P17"]
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-11-2027 22:15:00(GMT-04:00)"
    validity_window_days: 365
    status: "ACTIVE"
    last_update_source:
      url: "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm"
      source_type: "legislation"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Revisão dos artigos 11 e 14 da LGPD sobre consentimento e dados sensíveis de saúde."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm"
        verified_by: "session_20261106_2215"
        summary: "Calibração dos princípios P07 e P09 na constituição."
    authoritative_sources:
      - "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm"
      - "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
      - "https://www.hhs.gov/hipaa"
      - "https://artificialintelligenceact.eu"

  - id: "cloud_services"
    name: "Serviços Cloud, Infraestrutura e Custos"
    description: "Modelos de precificação de nuvem (AWS, GCP, Cloudflare), arquiteturas serverless, limites de quotas, SLAs e storage distribuído."
    scope: "global"
    trigger: "warning"
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-02-2027 22:15:00(GMT-04:00)"
    validity_window_days: 90
    status: "ACTIVE"
    last_update_source:
      url: "https://cloud.google.com/pricing"
      source_type: "cloud_pricing"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Validação de modelos de computação sob demanda e precificação de buckets/CDN."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://cloud.google.com/pricing"
        verified_by: "session_20261106_2215"
        summary: "Atualização de parâmetros de custos para decisões arquiteturais."
    authoritative_sources:
      - "https://aws.amazon.com/pricing"
      - "https://cloud.google.com/pricing"
      - "https://www.cloudflare.com/plans"

  - id: "scientific_claims"
    name: "Afirmações Científicas e Revisão de Literatura"
    description: "Citações científicas, evidências empíricas, dosagens, biomarcadores e revisões sistemáticas (PRISMA)."
    scope: "global"
    trigger: "blocking"
    constitution_principles: ["P03", "P09"]
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-05-2027 22:15:00(GMT-04:00)"
    validity_window_days: 180
    status: "ACTIVE"
    last_update_source:
      url: "https://pubmed.ncbi.nlm.nih.gov"
      source_type: "scientific_indexer"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Rigor estrito em citações com links verificáveis (HTTP 200) e identificador DOI."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://pubmed.ncbi.nlm.nih.gov"
        verified_by: "session_20261106_2215"
        summary: "Blindagem de alegações médicas sob o princípio P03."
    authoritative_sources:
      - "https://pubmed.ncbi.nlm.nih.gov"
      - "https://europepmc.org"
      - "https://www.cochranelibrary.com"

  - id: "clinical_safety"
    name: "Segurança Clínica e Protocolos de Saúde Humana"
    description: "Ranges de biomarcadores, contraindicações médicas, suporte à decisão clínica e salvaguarda HITL obrigatória."
    scope: "global"
    trigger: "blocking"
    constitution_principles: ["P00", "P09", "P14"]
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-11-2027 22:15:00(GMT-04:00)"
    validity_window_days: 365
    status: "ACTIVE"
    last_update_source:
      url: "https://www.who.int/publications"
      source_type: "global_health_authority"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Exigência de validação por profissional habilitado para recomendações clínicas diretas."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://www.who.int/publications"
        verified_by: "session_20261106_2215"
        summary: "Inviolabilidade do princípio P00 (Human Wellbeing First) e P09."
    authoritative_sources:
      - "https://www.who.int"
      - "https://www.ms.gov.br"

  - id: "software_architecture"
    name: "Engenharia de Software e Padrões Arquiteturais"
    description: "Padrões de design estrutural baseados em componentes atômicos e coesos utilizando SRP (Single Responsibility Principle), Clean Architecture, contratos OpenAPI 3.0 / JSON Schema puros, baixo acoplamento e alta testabilidade."
    scope: "global"
    trigger: "warning"
    last_verified_at: "06-11-2026 22:15:00(GMT-04:00)"
    valid_until: "06-11-2027 22:15:00(GMT-04:00)"
    validity_window_days: 365
    status: "ACTIVE"
    last_update_source:
      url: "https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html"
      source_type: "engineering_authority"
      verified_by: "session_20261106_2215"
      machine_id: "42c8e746"
      summary_of_changes: "Adoção de componentes desacoplados escritos utilizando SRP (Single Responsibility Principle) e contratos formais como padrão canônico do kit."
    update_history:
      - verified_at: "06-11-2026 22:15:00(GMT-04:00)"
        url: "https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html"
        verified_by: "session_20261106_2215"
        summary: "Formalização do padrão de componentes atômicos orientados a SRP no kit v0.0.1."
    authoritative_sources:
      - "https://blog.cleancoder.com"
      - "https://martinfowler.com"
      - "https://refactoring.guru"
```

---

### 3.3. Registry Canônico Exaustivo: `dynamic_questioning.yaml`

O arquivo `dynamic_questioning.yaml` define o questionamento socrático durante o `/vitalia-brainstorming`. Ele é estruturado em **9 domínios canônicos** cobrindo todas as frentes de engenharia de software moderno, livre de condicionais de Redis/Celery/Ollama/VRAM:

1. **`protecao_de_dados_e_privacidade` (P0 CRITICAL):**
   - *Decisão 1:* Soberania e Localização de Dados (Infraestrutura própria / BYOK vs Cloud / SaaS).
   - *Decisão 2:* Modelo de Consentimento (Opt-in com trilha de auditoria imutável).
2. **`autenticacao_e_identidade` (P0 CRITICAL):**
   - *Decisão 1:* Gestão de Identidade (Sistema Próprio / Custom com hashing seguro vs IDaaS).
   - *Decisão 2:* Controle de Acesso (RBAC simples vs ABAC contextual multi-tenant).
3. **`seguranca_de_api_e_comunicacao` (P0 CRITICAL):**
   - *Decisão 1:* Autenticação e Autorização de Endpoints (JWT com expiração curta + refresh token vs API Keys).
   - *Decisão 2:* Sanitização e Validação de Input (Validação estrita em fronteira via JSON Schema / Pydantic).
4. **`arquitetura_de_aplicacao` (HIGH-LEVERAGE):**
   - *Decisão 1:* Modularidade e Coesão (Componentes desacoplados orientados a SRP com responsabilidade única e contratos estritos vs acoplamento difuso).
   - *Decisão 2:* Comunicação Inter-Componentes (Chamadas em memória via contratos tipados e isolamento de dependências).
5. **`comunicacao_e_sincronizacao` (HIGH-LEVERAGE):**
   - *Decisão 1:* Estratégia de Atualização de Estado (Polling inteligente para MVP vs SSE vs WebSockets).
   - *Decisão 2:* Gestão de Estado Distribuído (Filesystem com controle de semáforo vs Hub Git).
6. **`processamento_assincrono` (HIGH-LEVERAGE):**
   - *Decisão 1:* Desacoplamento de Tarefas Longas (Execução síncrona com timeout vs Workers nativos em background).
7. **`arquitetura_de_dados_e_persistencia` (HIGH-LEVERAGE):**
   - *Decisão 1:* Modelo de Consistência (SQL/ACID com integridade referencial vs NoSQL documental).
   - *Decisão 2:* Migrações e Versionamento de Esquema (Scripts versionados e rastreáveis no Git).
8. **`machine_learning_e_ia_de_fronteira` (HIGH-LEVERAGE):**
   - *Decisão 1:* Provedor e Privacidade de Inferência (Modelos de fronteira com anonimização prévia vs políticas de Zero Data Retention).
   - *Decisão 2:* Orquestração de Contexto (Context Lifting sem podas arbitrárias via oráculo Guardian).
9. **`observabilidade_e_auditoria` (MEDIUM):**
   - *Decisão 1:* Estratégia de Logging (Structured logging JSON com sanitização de PII/PHI).
   - *Decisão 2:* Trilha de Decisões e Aprendizados (Ledger de sessão persistido em `.jsonl`).

Todos os domínios do `dynamic_questioning.yaml` conterão os metadados de governança temporal: `last_reviewed_at`, `valid_until`, `validity_window_days`, `status` e `last_update_source`.

---

### 3.4. Catálogo de Intenções: `brainstorming_intents.yaml`

O arquivo `brainstorming_intents.yaml` é expandido para **7 domínios semânticos**:
1. `estrategia_produto` (Roadmap, proposta de valor, MVP e métricas).
2. `arquitetura_software` (Topologia, isolamento de dependências, ADRs e Clean Architecture).
3. `engenharia_web_frontend` (UI/UX rica, CSS Vanilla, Vite, design systems e SEO).
4. `infraestrutura_devops` (CI/CD, containers, automação, isolamento de runtime e shims).
5. `seguranca_compliance` (OWASP, LGPD/HIPAA, auditoria de código, hardening e Zero Data Leak).
6. `educacao_workshop` (Material didático, cursos, palestras e tutoriais).
7. `saude_clinica` (Sistemas médicos, prontuários, biomarcadores e salvaguarda HITL — Princípio P09).

---

### 3.5. Pasta `source/extensions/`

| Componente | Ação Corretiva na Spec 003 |
| :--- | :--- |
| **Todos os 11 .toml existentes** | Remover a chave obsoleta `guardian_profile = "gp_*"`. Ajustar transport para `filesystem` puro. |
| **`analyze.toml` (Novo)** | Criar extensão v0.0.1 para o workflow `/vitalia-analyze`: <br/>- Modo `after_tasks`: consistência conceitual entre `spec.md`, `plan.md` e `tasks.md`. <br/>- Modo `after_implement`: auditoria de código real via Git Diff em 3 camadas (*Previsto no Plano*, *Adaptação Correlata*, *Órfão Real / Drift*). Verificação estática mandatória de aridade/imports em call-sites modificados. <br/>- Emissão dual de relatório (chat da IDE e arquivo `specs/<feature>/Relatório de Análise e Consistência - <fase>.md`). <br/>- **Pausa mandatória para consentimento humano (HITL Soberano)**. |

---

### 3.6. Pasta `source/bin/` e `source/bin/lib/`

| Componente | Ação Corretiva na Spec 003 |
| :--- | :--- |
| `lib/redis_detector.sh` | **Exclusão definitiva.** |
| `lib/logger.sh` | Adicionar acumulador em memória `_VITALIA_LOG_BUFFER` e função `write_install_log`. |
| `lib/agent_preserver.sh` | Atualizar linha 221 para `${VITALIA_KIT_DIR:-${HOME}/.vitalia-spec-kit}`, eliminando `~/.vitalia`. |
| `lib/env_manager.sh` | Garantir que `VITALIA_KIT_DIR` seja preservado e gravado no `.env` do projeto. |
| `install-project` | - Remover opção e prompts de Gemini CLI (foco exclusivo em Antigravity IDE). <br/>- Backup condicional de `.agents` em `data_storage` se `DATA_REPO` configurado; se não, alerta explícito. <br/>- Configurar `extensions.yml` para acionar a extensão `analyze` em `after_tasks` e `after_implement`. <br/>- Gravar log de instalação no destino condicional. |
| **`vitalia-spec-analyze`** | **NÃO criar script executável de terminal.** O analyze opera como workflow nativo de IDE (`/vitalia-analyze`). |

---

### 3.7. Pasta `source/src/` e Motor de Contexto

| Componente | Ação Corretiva na Spec 003 |
| :--- | :--- |
| `kit_env_bootstrap.py` | Implementar resolução em 3 níveis (`os.environ` $\rightarrow$ `.env` do projeto $\rightarrow$ fallback `$HOME/.vitalia-spec-kit`). Remover busca em `~/.vitalia`. |
| `vitalia_hook_runner.py` | Fallback para `$HOME/.vitalia-spec-kit`. Precedência de PATH com `.venv/bin`. |
| `hooks/guardian_context.py` | Purgar fallback `~/.vitalia` e busca de `gp_*`. Implementar verificação de expiração temporal (`valid_until`) dos domínios. |
| `vitalia_handoff.py` | Atualizar verificações de Zero Data Leak para o caminho customizado do kit. |
| `vitalia_context_engine.py` | **Restauração da Fidelidade do Dashboard Rico:** <br/>- Substituir a montagem inline minimalista por renderizador completo que carrega `dashboard_template.md`. <br/>- Injetar badges dinâmicos, diagrama Mermaid da topologia, tabela rica de shards, destaque da sessão ativa, e seções colapsáveis `<details>` com histórico (`session_history.jsonl`), decisões consolidadas (`decisions.jsonl`) e status dos guard rails de grounding (`grounding_domains.yaml`). <br/>- Resolver caminho do template via `kit_env_bootstrap.resolve_kit_dir()`. |

---

### 3.8. Pasta `source/templates/` (Template Canônico do Dashboard)

Criação de `source/templates/dashboard_template.md` contendo a estrutura visual rica higienizada:

```markdown
<!-- README.md | Atualizado em: {timestamp} -->

# 🧠 Painel de Contexto — {project_name}

{badge_status}
{badge_semaforo}
{badge_modo}
{badge_sync}
{badge_grounding}

> **Vitalia SPEC Kit v0.0.1 — Ledger de Memória Persistente e Orquestração Local.**  
> Este repositório armazena o histórico distribuído, aprendizados consolidados e o controle de concorrência das sessões de trabalho do framework Vitalia.

---

## 📡 Topologia de Shards & Sincronização

<div align="center">

```mermaid
flowchart TD
{mermaid_content}
```

</div>

---

## 🖥️ Máquinas e Status Atual

<table>
  <thead>
    <tr>
      <th align="left">Máquina / ID</th>
      <th align="left">Tarefa Atual</th>
      <th align="center">Ambiente</th>
      <th align="center">Status</th>
      <th align="left">Último Sync</th>
      <th align="left">Próximo Passo (P0)</th>
    </tr>
  </thead>
  <tbody>
{shards_table}
  </tbody>
</table>

---

## 🎯 Sessão Ativa em Destaque

{sessao_ativa}

---

## 📚 Histórico, Decisões & Guard Rails

<details>
<summary><strong>🔍 Clique para expandir o Histórico Completo de Sessões</strong></summary>

<br/>

{historico_sessoes}
</details>

<details>
<summary><strong>⚖️ Clique para expandir as Decisões Arquiteturais Consolidadas</strong></summary>

<br/>

| Máquina (ID) | Decisão Arquitetural | Impacto / Racional |
| :--- | :--- | :--- |
{decisoes_arquiteturais}
</details>

<details>
<summary><strong>🛡️ Clique para expandir os Guard Rails de Grounding e Domínios</strong></summary>

<br/>

| Arquivo de Regras | Status | Domínios Monitorados | Pendentes de Curadoria HITL |
| :--- | :---: | :--- | :---: |
| `grounding_domains.yaml` (Global) | {global_status} | `provedores_de_ia`, `python_packages`, `web_technologies`, `external_apis`, `security_practices`, `regulations_compliance`, `cloud_services`, `scientific_claims`, `clinical_safety`, `software_architecture` | — |
| {local_link} (Projeto) | {local_status} | Domínios locais específicos do workspace | {pending_badge} |

</details>

---

<sub>Painel gerado automaticamente pelo motor de contexto do Vitalia Kit (<code>vitalia_context_engine.py --action consolidate</code>).</sub>
```

---

### 3.9. Pasta `source/integrations/` & `source/AGENTS.md`

| Componente | Ação Corretiva na Spec 003 |
| :--- | :--- |
| `antigravity/SKILL.md.template` | Linha 1 iniciando estritamente com `---` (frontmatter YAML puro). Invocação apontando para `{{VITALIA_KIT_DIR}}/.venv/bin/python3`. |
| `source/AGENTS.md` | Atualizar tendo como base o [`AGENTS.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.agents/AGENTS.md) deste projeto (anti-Lost in the Middle, numeração de specs 3 dígitos zero-padded, isolamento de runtime e HITL soberano). |

---

## 4. O Novo `kit-bootstrap.sh` (Instalação Filtrada, Não Espelhada em Lote)

O `kit-bootstrap.sh` abandona cópias em lote cegas e executa uma **instalação atômica, validada e componente por componente**:
1. **Passo 1 — Destino Global Interativo:** Solicita o caminho sugerindo `~/.vitalia-spec-kit` e expande `~`.
2. **Passo 2 — Criação de Diretórios:** Cria `${VITALIA_DIR}/{bin,bin/lib,extensions,profiles,src,src/hooks,integrations/antigravity,templates}`.
3. **Passo 3 — Virtualenv Isolado:** Cria `.venv` e instala dependências mínimas de `requirements.txt`.
4. **Passo 4 — Instalação Componente a Componente (Filtrada):**
   - Copia apenas os binários autorizados (`install-project`, `lib/agent_preserver.sh`, `lib/env_manager.sh`, `lib/git_storage_manager.sh`, `lib/logger.sh`). **Zero cópia de `redis_detector.sh`**.
   - Copia os 12 `.toml` validados + `analyze.toml`.
   - Copia os perfis canônicos expandidos com dimensão temporal (`constitution.yaml`, `routing_table.yaml`, `agents_catalog.yaml`, `brainstorming_intents.yaml`, `dynamic_questioning.yaml`, `grounding_domains.yaml`). **Zero cópia de `gp_*.yaml`**.
   - Copia o motor Python em `src/` (incluindo `vitalia_context_engine.py` com o renderizador rico e `hooks/`).
   - Copia `templates/dashboard_template.md` para `${VITALIA_DIR}/templates/dashboard_template.md`.
   - Copia `integrations/antigravity/SKILL.md.template`.
   - Copia `source/AGENTS.md` para `${VITALIA_DIR}/AGENTS.md`.
5. **Passo 5 — Shim em `~/.local/bin/`:** Cria `vitalia-install-project` apontando para o interpretador e caminhos configurados.

---

## 5. Estratégia de Smoke Test E2E (Sem Instalar no Host Atual)

O teste automatizado em `tests/test_bootstrap_e2e_project.py` roda em sandbox temporário (`tmp_path`) sem tocar na máquina hospedeira real:
- Executa `kit-bootstrap.sh` apontando `HOME` para `tmp_path/home_sandbox`.
- Executa `vitalia-install-project` dentro de `tmp_path/mock_project`.
- Executa `vitalia_context_engine.py --action consolidate` dentro do projeto mock.
- **Valida:**
  - Criação de `.vitalia/` e `.env` com `VITALIA_KIT_DIR`.
  - Geração de `.agents/skills/vitalia-*/SKILL.md` com YAML frontmatter válido na Linha 1 (incluindo `vitalia-analyze`).
  - Gravação do log de instalação no buffer e arquivo.
  - Ausência de arquivos `gp_*` e `redis_detector.sh` no kit instalado.
  - Geração de `.vitalia/memory/session/README.md` fiel e rico (contendo badges, diagrama Mermaid, tabela estilizada e seções `<details>` colapsáveis de Histórico e Decisões).
  - A máquina hospedeira real permanece 100% intocada.

---

## 6. Rastro de Pesquisa e Grounding (P03)

| # | Fonte Canônica | URL Verificada | Data | Princípio Incorporado |
|---|---|---|---|---|
| **E1** | **PyPA Virtualenv Isolation** | [`https://docs.python.org/3/library/venv.html`](https://docs.python.org/3/library/venv.html) | 06-11-2026 | Isolamento estrito de runtime por ambiente sem contaminação global do host. |
| **E2** | **IEEE 1044 / NASA Root Cause Analysis** | [`https://standards.ieee.org/`](https://standards.ieee.org/) | 06-11-2026 | Classificação e rastreamento formal de anomalias em ciclo de vida de software. |
| **E3** | **Git Porcelains & Diff Inspection** | [`https://git-scm.com/docs/git-diff`](https://git-scm.com/docs/git-diff) | 06-11-2026 | Extração determinística de deltas semânticos e identificação de call-sites modificados. |
| **E4** | **W3C PROV-O (Provenance Ontology)** | [`https://www.w3.org/TR/prov-o/`](https://www.w3.org/TR/prov-o/) | 06-11-2026 | Modelo ontológico para rastreamento de proveniência temporal de dados e entidades. |
| **E5** | **Mermaid.js Flowchart Architecture** | [`https://mermaid.js.org/syntax/flowchart.html`](https://mermaid.js.org/syntax/flowchart.html) | 06-11-2026 | Padrão canônico de renderização de topologia visual de nós e conexões de rede em markdown. |
| **E6** | **OWASP Top 10 for LLM Applications 2025** | [`https://owasp.org/www-project-top-10-for-large-language-model-applications`](https://owasp.org/www-project-top-10-for-large-language-model-applications) | 06-11-2026 | Diretrizes de segurança para sistemas e pipelines orquestrados por agentes de IA. |

---
*Este documento estabelece o briefing de concepção aprovado para guiar a Spec 003 no repositório vitalia-spec-kit.*
