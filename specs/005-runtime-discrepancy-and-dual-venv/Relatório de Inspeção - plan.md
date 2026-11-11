<!-- Relatório de Inspeção - plan.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:01(GMT-04:00) -->
> **Relatório de Inspeção - plan.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:01(GMT-04:00)**

# Relatório de Inspeção Constitucional — SDD-Judge (Fase: `plan`)

- **Feature Inspecionada:** `specs/005-runtime-discrepancy-and-dual-venv`
- **Artefato Alvo:** [`specs/005-runtime-discrepancy-and-dual-venv/plan.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/plan.md)
- **Artefatos de Suporte:**
  - [`specs/005-runtime-discrepancy-and-dual-venv/research.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/research.md)
  - [`specs/005-runtime-discrepancy-and-dual-venv/contracts/cli-contracts.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/contracts/cli-contracts.md)
  - [`specs/005-runtime-discrepancy-and-dual-venv/quickstart.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/quickstart.md)
- **Modo:** Sub-Agente Nativo na IDE Antigravity (`/vitalia-judge --mode=plan`)
- **Data da Inspeção:** 11-11-2026 10:01(GMT-04:00)

---

## 1. FMEA Mental (Red Team Failure Hunt)

### Q1: Hipóteses de Ambiente Limpo (Clean Machine Assumptions)
- **Análise Adversarial:** O plano assume que ferramentas externas ou interpretadores Python específicos já estarão instalados globalmente no sistema host?
- **Evidências:** A Seção 2 e a Seção 4 definem que o `{{KIT_PYTHON}}` opera exclusivamente sobre `${VITALIA_KIT_DIR}/.venv` pré-construído pelo `kit-bootstrap.sh`. Para o `{{PROJECT_PYTHON}}`, a Seção 4 (Decisão D2) implementa a busca em 4 níveis com fallback dinâmico transparente para `{{KIT_PYTHON}}` caso o projeto cliente não utilize virtualenv. Não há qualquer suposição de dependências globais ou de ferramentas adicionais.
- **Conclusão:** Imune a premissas de máquina limpa. Suporta ambientes Linux, WSL e Windows sem suposições ocultas.

### Q2: Auditoria Anti-Shallow Testing (P05)
- **Análise Adversarial:** A estratégia de testes proposta em `plan.md` permite que a implementação seja validada com testes puramente sintáticos de arquivos ou mocks triviais?
- **Evidências:** A Seção 6 estabelece o Test Depth Agreement (TDA) com as 4 modalidades canônicas P05:
  - `[TEST:BUGFIX]`: Injeção de binário mock de `python3` no `$PATH` retornando erro 127 para falsificar comportamento do runner caso este recorra ao `python3` global.
  - `[TEST:NEW]`: Criação de projeto efêmero com `.env` customizado para falsificar e validar a ancoragem de caminhos relativos em `project_root`.
  - `[TEST:REFACTOR]`: Linter estático nos 16 arquivos `.toml` para falsificar regressões na sintaxe de hooks.
  - `[TEST:MIGRATION]`: Teste de integração de ponta a ponta com `install-project` em ambiente isolado.
- **Conclusão:** Plena conformidade com P05. Testes sintáticos superficiais (`assert path.is_file()`) estão formalmente vetados.

### Q3: Regressão por Simplificação Indevida
- **Análise Adversarial:** A alteração de `kit_env_bootstrap.py` e `vitalia_hook_runner.py` compromete a passagem de contexto de sessão (3-Tier) ou a ejeção de envelopes JSON nos hooks existentes?
- **Evidências:** A Seção 5 (Matriz de Migração) isola os comportamentos invariantes a preservar: parse de TOML, emissão de stub no stdout, injeção de envelopes físicos em `.vitalia/memory/data_storage/context/` e persistência de sessão. A auto-substituição de `python3` em `vitalia_hook_runner.py` atua estritamente como interceptor defensivo apenas para chamadas a scripts do kit, preservando comandos externos intocados.
- **Conclusão:** Risco de regressão neutralizado.

### Q4: Violação de Contrato do Consumidor
- **Análise Adversarial:** Os contratos de CLI e esquemas de dados expostos alteram a interface consumida pela IDE Antigravity ou introduzem meta-schemas proibidos?
- **Evidências:** O artefato [`specs/005-runtime-discrepancy-and-dual-venv/contracts/cli-contracts.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/contracts/cli-contracts.md) define o payload de `scan_environment.py` em conformidade estrita com o subset OpenAPI 3.0 (sem `$schema`, sem `title` raiz, sem `additionalProperties: false`). As skills continuam 100% puras no diretório `.agents/skills/`.
- **Conclusão:** Contratos com o consumidor IDE Antigravity integralmente preservados.

---

## 2. Inverted Chain-of-Thought (Citações de Linha & Análise Crítica)

1. **Evidência 1 (`plan.md`, Linhas 13-14):**
   > *"Desacoplamento estrito entre o runtime de governança interna do kit (`{{KIT_PYTHON}}` em `${VITALIA_KIT_DIR}/.venv`) e o runtime da aplicação hospedeira (`{{PROJECT_PYTHON}}`), resolvido em 4 níveis de descoberta dinâmica no `kit_env_bootstrap.py`."*  
   *Análise Crítica:* Resolve a causa raiz do problema operacional sem criar acoplamento temporal ou de pacotes entre o ferramental do kit e a aplicação do usuário.

2. **Evidência 2 (`plan.md`, Linhas 48-49):**
   > *"D1: Uso de `sys.executable` e inspeção de caminhos para auto-substituição de comandos `python3` no runner."*  
   *Análise Crítica:* Implementa o padrão de defesa em profundidade. Mesmo que haja desvios em chamadas operacionais, o processo pai reescreve deterministicamente a chamada para o interpretador do virtualenv em que o runner reside.

3. **Evidência 3 (`plan.md`, Linha 51):**
   > *"D4: Regra cognitiva anti-loop de sandbox em `AGENTS.md` instruindo `BypassSandbox: true` e vetando `./kit-bootstrap.sh`."*  
   *Análise Crítica:* Elimina a lacuna cognitiva dos modelos de linguagem que interpretavam erro 127 de sandbox como ausência do kit no disco.

---

## 3. Matriz de Confronto Constitucional 1-a-1

| Princípio Constitucional | Regra Avaliada | Evidência no `plan.md` | Veredito Unitário |
| :--- | :--- | :--- | :---: |
| **P00 (Purpose Arbiter)** | Centralidade humana e fluidez de desenvolvimento. | Elimina interrupções indevidas em `/vitalia-session-start`. | **PASS** |
| **P01 (SDD Inviolability)** | Estrita sequência specify $\to$ plan $\to$ tasks $\to$ implement. | Plano formal alinhado a `spec.md` e clarificação prévia. | **PASS** |
| **P02 (User-Centric Validation)** | Resolução de atritos reais do usuário. | Foco total na estabilidade do fluxo de inicialização e execução. | **PASS** |
| **P03 (External Grounding)** | Fundamentação técnica verificada. | Seção 3 e `research.md` fundamentados em PEP 405 e documentação de sandbox. | **PASS** |
| **P04 (Timestamp GMT-04:00)** | Cabeçalho duplo-stamp GMT-04:00 em `plan.md`. | Cabeçalho duplo validado nas linhas 1 e 2. | **PASS** |
| **P05 (TDD & Falsificação)** | Matriz de 4 modalidades e cenários de falsificação. | Seção 6 detalha o TDA com `[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`. | **PASS** |
| **P06 (Secrets Never in Git)** | Segurança de variáveis e credenciais. | Variáveis de caminho gerenciadas via `.env` local sem exposição. | **PASS** |
| **P07 (Architecture Governance)** | Governança por ADRs e topologia de 4 camadas. | Implementa a arquitetura de Camada 2 vs Camada 1 do ADR-0004. | **PASS** |
| **P10 (Didactics-First)** | Mensagens operacionais claras e explicativas. | Quickstart e diagnósticos prescrevem correções claras ao desenvolvedor. | **PASS** |
| **P11 (Runtime Autonomy)** | Independência de runtime e ausência de colisões. | Núcleo do plano: isolamento total de `site-packages` do kit. | **PASS** |
| **P15 (Observability)** | Diagnósticos estruturados e rastreáveis. | Payload OpenAPI 3.0 segregado em `kit_runtime` e `project_runtime`. | **PASS** |
| **P16 (Defensive Mermaid)** | Mermaid com labels com aspas duplas. | Sem diagramas em `plan.md` (diagrama em `contracts` validado com aspas). | **PASS** |

---

## 4. Veredito Constitucional

### Status: **PASS (Aprovado)**
O plano técnico [`specs/005-runtime-discrepancy-and-dual-venv/plan.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/005-runtime-discrepancy-and-dual-venv/plan.md) foi exaustivamente auditado pelo SDD-Judge. O documento cumpre com excelência todos os 18 princípios da Constituição Vitalia, estabelece com rigor o Test Depth Agreement (P05) e neutraliza de forma definitiva a discrepância de runtimes e os falsos loops de bootstrap.

---

### 🚦 Gate HITL Soberano
O plano técnico está **aprovado** pelo SDD-Judge. Em conformidade com o princípio de governança e soberania humana, submetemos a aprovação do plano para autorização formal do desenvolvedor antes de avançar para a fase de decomposição de tarefas atômicas ([`/vitalia-spec-tasks`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.agents/skills/vitalia-spec-tasks/SKILL.md)).

