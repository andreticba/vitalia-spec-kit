<!-- analise-contratual-e-auditoria-kit.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 07:28(GMT-04:00) -->
> **analise-contratual-e-auditoria-kit.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 07:28(GMT-04:00)**

# Relatório de Auditoria Contratual, Engenharia de Atenção e Análise Semântica do Vitalia SPEC Kit

**Data:** 10-11-2026 07:28 (GMT-04:00)  
**Status:** DRAFT PARA APROVAÇÃO HITL  
**Alvo:** `source/` (Repositório) vs `~/.vitalia` (Kit Global) vs Contrato da Antigravity IDE  

---

## 1. Mapeamento de Contratos dos Arquivos e Topologia de Execução

### 1.1. Arquitetura em 4 Camadas Isoladas (FR-001)
1. **Camada 1 (Repositório de Código-Fonte):** `source/` no repositório `vitalia-spec-kit`. Versionado via Git raiz. Não executa diretamente runtime de projeto.
2. **Camada 2 (Kit Global na Máquina Hospedeira):** `~/.vitalia-spec-kit/` (ou `~/.vitalia`). Contém o interpretador isolado `.venv`, executáveis em `bin/`, extensões canônicas em `extensions/`, perfis em `profiles/` e biblioteca em `src/`.
3. **Camada 3 (Memória de Sessão Multi-Máquina):** `<project_root>/.vitalia/memory/session/`. Repositório Git dedicado, gerido exclusivamente pelo `vitalia_context_engine.py` (Regra da Cerca Elétrica).
4. **Camada 4 (Memória de Dados e Handoffs):** `<project_root>/.vitalia/memory/data_storage/`. Guarda `handoffs/` e `context/<machine_id>/`. Isolado de `$HOME` e de `VITALIA_KIT_DIR` (Zero Data Leak).

---

## 2. Tabela de Auditoria por Requisito Funcional (Specs 001, 002 e Extensões)

| Requisito / Tarefa | Descrição na Spec | Estado no código do Kit em `source` | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :---: | :--- |
| **FR-001 / T001** (Topologia 4 Camadas) | Isolamento estrito entre `source/`, Kit Global, sessão e data storage. | Implementado em `source/` e validado em `test_bootstrap_and_install.py`. | **CONFORME** | A separação impede contaminação entre código versionado e runtime local. |
| **FR-002 / T013** (Bootstrap Universal) | `kit-bootstrap.sh` com suporte a `--target-dir`, pré-checagem de `python3 -m venv` e injeção semântica. | Implementado na raiz e testado contra falha de `venv`. | **CONFORME** | Emite erro limpo (exit code 1) se `python3-venv` faltar no sistema. |
| **FR-003 / T014-T019** (Pureza de Skills) | `install-project` mantém `.agents/skills/` 100% puro (zero `.trash`, zero `.vitalia-manifest`). | Implementado em `source/bin/lib/skill_generator.sh`. | **ALERTA** | A geração em `skill_generator.sh` usa `update_skill "vitalia-${ext_name}"`. Se o arquivo for `vitalia-route.toml`, gera `vitalia-vitalia-route`. Requer normalização idempotente. |
| **FR-004 / T022** (Descoberta sem Redis) | `scan_environment.py` e `kit_env_bootstrap.py` reportam `OK` sem exigir Redis local. | Implementado em `source/src/hooks/scan_environment.py`. | **CONFORME** | Testado em `test_scan_environment_and_kit_bootstrap_healthy_without_redis`. |
| **FR-005 / T023-T024** (Context Lifting Sem Poda) | §11 Context Lifting: 100% sem poda (`token_budget: 0`, `no_prune: true`), gravando envelope em `context/<machine_id>/`. | Implementado em `source/src/vitalia_hook_runner.py` e `guardian_context.py`. | **CONFORME** | Persistência local atômica sem vazar dados no terminal e sem Redis. |
| **FR-006 / T025-T029** (Motor 3-Tier e Shards) | Ordenação de shards por `last_sync` decrescente, garantindo `shards[0]` como máquina ativa. | Implementado em `source/src/core/shard_manager.py`. | **CONFORME** | Testado em `test_shard_manager_orders_by_last_sync_descending`. |
| **FR-007 / T030-T031** (Handoff Determinístico) | `vitalia_handoff.py` resolve raiz, cria, lista e consome atomicamente em `data_storage/handoffs/`. | Implementado em `source/src/vitalia_handoff.py`. | **CONFORME** | Zero Data Leak garantido: bloqueia `$HOME` e `VITALIA_KIT_DIR`. |
| **FR-008 / T009-T010** (16 Workflows Canônicos) | 16 workflows `.toml` em `source/extensions/` mapeados para 14 lentes `gp_*.yaml` sem poda. | Presentes os 16 `.toml` canônicos em `source/extensions/`. | **DIVERGÊNCIA** | Workflows auxiliares como `pair.toml`, `debug.toml`, `review.toml` etc., existem em `~/.vitalia` mas NÃO foram integrados à pasta `source/extensions/`. |
| **Ingestão session_context.handoff** | Ingestão em `guardian_context.py` populando `session_context.handoff` via `latest_handoff()`. | Presente em `source/src/hooks/guardian_context.py`. | **ALERTA** | O `guardian_context.py` tenta ler `vitalia_handoff.py` primeiro do kit global e depois de `source/src/`. Se `~/.vitalia` estiver desatualizado, pode ocorrer colisão de versão. |
| **Desacoplamento do Brainstorming** | `brainstorming.toml` atua como supervisor socrático e delega via handoff `forward` para `vitalia-route`. | Implementado em `source/extensions/brainstorming.toml`. | **CONFORME** | NUNCA despacha direto para `/vitalia-spec-specify`. Regra explícita de inviolabilidade. |
| **Despachante vitalia-route (Zero Redis)** | `route.toml` consome via filesystem/handoff local sem qualquer citação a Redis Stream. | Implementado em `source/extensions/route.toml`. | **CONFORME** | `preferred = "filesystem"`, `file_path = ".vitalia/pipeline.json"`. Zero Redis. |
| **Trava de Escalação Invertida** | `spec-implement.toml` e `pair.toml` gravam `divergence_<uuid_8>.json` e geram handoff `reverse`. | Presente em `spec-implement.toml`. Ausente em `source/extensions/pair.toml`. | **CRÍTICO** | `pair.toml` está ausente de `source/extensions/` (só existe no kit legado `~/.vitalia/extensions/`). Deve ser portado com urgência. |
| **Contratos OpenAPI 3.0 (P11)** | Schemas sem `$schema`, sem `title` de raiz e sem `additionalProperties: false`. | 9 schemas em `source/src/schemas/` 100% aderentes. | **CONFORME** | Evita erro HTTP 400 em chamadas de API do Google Gemini. |
| **Princípio Didático P10** | 100% dos scripts utilitários CLI implementam `--help` didático com exemplos de uso. | Implementado em todos os scripts Python de `source/src/` e testado. | **CONFORME** | Validado em `test_contracts_and_handoff.py`. |

---

## 3. Análise Semântica, Sequestro de Atenção do LLM e Engenharia de Prompts

### 3.1. Como os Modelos de Fronteira Processam as Seções dos `.toml`
Os arquivos `.toml` definem a execução em dois momentos:
1. **Momento da IDE (Pré-Execução):** O arquivo `.agents/skills/<skill>/SKILL.md` expõe o `description` no catálogo. O modelo lê o frontmatter e decide invocar o comando de hook (`python3 vitalia_hook_runner.py ...`).
2. **Momento da Sessão (Pós-Hook):** O agente lê o arquivo JSON gerado pelo Context Lifting (§11). Esse JSON contém:
   - `prompt`: Instruções de regência da fase (o "Script de Ação").
   - `guardian_json`: O universo constitucional, regras de domínio, aprendizados, histórico e handoffs (as "Leis da Física").

### 3.2. A Dinâmica de Atenção: Primacy, Recency e Lost-in-the-Middle
- **Topo do Prompt (Primacy Effect):** Define quem o LLM é (Identidade, Persona, Papel). É onde a autoridade socrática deve ser cravada.
- **Miolo do Prompt (Middle):** Dados contextuais injetados. Se o modelo tiver que "procurar" regras mandatórias aqui, ele falha devido à atenuação da curva em U. Portanto, `guardian_json` contém dados de apoio, não a dinâmica conversacional.
- **Fim do Prompt (Recency Effect):** Protocolo estrito de encerramento (`STOP -> SCAN -> ASK -> WAIT`), formato rígido de saída e freio cognitivo.

### 3.3. Simulação Cognitiva: "Se eu fosse um LLM lendo este prompt..."
- **Cenário A: Alteração Inadvertida na Finalização do Ciclo:**
  - *Se o prompt disser no final: "Gere o código correspondente às decisões":*  
    O LLM sofre viés de recência imediato. Ele ignora solenemente o bloco socrático anterior e escreve código diretamente na conversa, violando o princípio `P01` (SDD Pipeline Inviolability).
  - *Com a estrutura canônica atual:*  
    O final do prompt impõe: `WAIT (Pausa e Avaliação de Estado) — Formule no máximo 3 perguntas e pare imediatamente`. O modelo encerra a resposta sem gerar artefatos prematuros.
- **Cenário B: Falha na Interpolação de `{{args}}` ou variáveis:**
  - Se `{{args}}` não for preenchido, `user_input` chega vazio ao Guardian. O modelo fica cego quanto à intenção do usuário e faz perguntas genéricas de cold-start.
- **Cenário C: Ingestão de Handoff Invertido:**
  - Quando um desenvolvedor ou subagente desvia da arquitetura no `spec-implement`, a Trava de Escalação grava `divergence_<uuid_8>.json` e cria handoff `reverse` para `brainstorming`.
  - O Brainstorming lê `session_context.handoff`, detecta a divergência e, em vez de iniciar um novo fluxo, pergunta especificamente: *"Foi detectada divergência no componente X. Deseja revisar o contrato de arquitetura ou forçar a implementação?"*.

---

## 4. Diagnóstico das Diferenças: `source/` vs `~/.vitalia` (Kit Instalado)

1. **Defasagem Temporal:** `~/.vitalia` possui arquivos de 31-Out e 07-Nov, enquanto `source/` foi 100% blindado na Spec 002 (08-Nov e 09-Nov).
2. **Workflows Faltantes em `source/extensions/`:**
   - Em `~/.vitalia/extensions/`: existem 28 arquivos `.toml` (incluindo `pair.toml`, `debug.toml`, `review.toml`, `medical-gate.toml`).
   - Em `source/extensions/`: existem apenas os 16 canônicos da Spec 002.
   - **Risco:** Comandos como `/vitalia-pair` e `/vitalia-debug` continuam chamando scripts legados em `~/.vitalia`.
3. **Nomenclatura em `skill_generator.sh`:**
   - A função `update_skill` prefixa cegamente `vitalia-`. Se o arquivo se chamar `vitalia-route.toml`, gera `.agents/skills/vitalia-vitalia-route/`.
   - **Correção Necessária:** Implementar normalização idempotente: `skill_target_name="${ext_name#vitalia-}"; skill_target_name="vitalia-${skill_target_name}"`.
4. **Instalação do Kit Atualizado:**
   - O repositório `source/` tem 100% dos testes verdes (11/11 em 58s). Para que a IDE consuma essas melhorias sem bugs residuais, o kit em `~/.vitalia` (ou `~/.vitalia-spec-kit`) precisa ser sincronizado a partir de `source/`.

---

## 5. Plano de Ação Proposto (Roadmap para Aprovação)

### Fase 1: Higienização e Normalização Idempotente em `source/`
1. Atualizar `source/bin/lib/skill_generator.sh` garantindo tratamento idempotente de prefixos (`vitalia-` nunca duplicado).
2. Portar `pair.toml` para `source/extensions/pair.toml` adaptado para o novo padrão:
   - `version = "0.0.1"`
   - `hardware_profile = "frontier"`
   - `{{VITALIA_KIT_DIR}}` dinâmico (sem `~/.vitalia` hardcoded)
   - Trava de Escalação Invertida com gravação em `.vitalia/memory/data_storage/handoffs/divergence_<uuid_8>.json`
   - Handoff `reverse` para `brainstorming`.
3. Portar os demais workflows essenciais (`debug.toml`, `medical-gate.toml`, `review.toml`) sob a mesma governança sem poda.

### Fase 2: Sincronização Cirúrgica do Kit Global (`~/.vitalia`)
1. Fazer backup prévio de `~/.vitalia` para `~/.vitalia.bak.<timestamp>`.
2. Espelhar os arquivos testados de `source/{bin,extensions,profiles,src,integrations,templates}` para `~/.vitalia/`, eliminando divergências de código entre repositório e runtime.
3. Re-executar `install-project` no workspace para atualizar as 16+ skills em `.agents/skills/` com pureza total.

### Fase 3: Preparação da Próxima Spec (Spec 003)
1. Consolidar os novos contratos no catálogo formal.
2. Abrir a especificação da Spec 003 (Módulos de Pair Programming, Sensores de Runtime e Supervisão de Subagentes).

---
*Fim do Relatório Técnico. Salvo em `TEMP/analise-contratual-e-auditoria-kit.md`.*

