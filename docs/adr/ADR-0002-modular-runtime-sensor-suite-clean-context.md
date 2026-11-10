<!-- ADR-0002-modular-runtime-sensor-suite-clean-context.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 14:15(GMT-04:00) -->
> **ADR-0002-modular-runtime-sensor-suite-clean-context.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 14:15(GMT-04:00)**

# ADR-0002: Modular Runtime, Suíte de Sensores VRSS, Erradicação de Alucinações por Matriz Temporária e Persistência na Camada 4

- **Status:** Aceito (Regência Técnica do Vitalia Architect / HITL)
- **Data:** 10-11-2026
- **Autor:** Vitalia Architect (`/vitalia-architect`)
- **Feature:** `specs/003-modular-runtime-and-sensor-suite`
- **Fontes Canônicas:**
  - [`specs/003-modular-runtime-and-sensor-suite/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/research-brainstorming.md)
  - [`specs/003-modular-runtime-and-sensor-suite/revisao_contratual_workflows_sdd.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/revisao_contratual_workflows_sdd.md)
  - [`specs/003-modular-runtime-and-sensor-suite/relatorio_schemas_e_cobertura.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/relatorio_schemas_e_cobertura.md)
  - [`specs/003-modular-runtime-and-sensor-suite/plano-adequacao-kit-legado-turno.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/plano-adequacao-kit-legado-turno.md)

---

## 1. Contexto e Problema

Com a estabilização da topologia de 4 camadas na Spec 002, a inspeção empírica detalhada no código e os ensaios de execução com modelos de fronteira revelaram desafios atencionais e contratuais que demandavam padronização estruturante:

1. **Vetor de Alucinação Atencional (`tmp_cleanup_matrix`):** A injeção de mais de 100 linhas de metadados de arquivos temporários e menus interativos de limpeza (`[a/d/n/t]`) dentro de `guardian_json` desviava a atenção do modelo (sequestro atencional por *lost-in-the-middle*), provocando alucinações sobre tarefas de faxina em vez da execução do workflow.
2. **Dispersão de Persistência Local:** Backups e manifestos de integridade vinham sendo alocados na raiz de `.vitalia/` (`.vitalia/backups/` e `.vitalia/.vitalia-manifest`), violando o princípio de bounded context da Camada 4 (`data_storage`).
3. **Resolução Frágil de Variáveis de Ambiente:** `kit_env_bootstrap.py` retornava o valor configurado em `VITALIA_KIT_DIR` sem validar sua existência física prévia em disco, resultando em quebras imediatas (`FileNotFoundError`) caso apontasse para pasta não instalada.
4. **Anomalia de Nomenclatura no Gerador de Skills:** `skill_generator.sh` concatenava o prefixo `vitalia-` cegamente, gerando pastas duplicadas (`.agents/skills/vitalia-vitalia-route/`) quando extensões já continham o prefixo.
5. **Necessidade de Observabilidade em Malha Fechada (VRSS):** Falhas de testes e logs brutos de console poluíam o prompt da LLM sem enriquecimento semântico.

---

## 2. Decisões Arquiteturais Estruturantes

### 2.1. Erradicação da Matriz Temporária do Runtime e Autonomia do Faxineiro
- A injeção de `tmp_cleanup_matrix` é terminantemente banida de `vitalia_hook_runner.py` e de todos os payloads dinâmicos `guardian_json`.
- A manutenção e higiene de arquivos temporários passa a residir exclusivamente no utilitário de manutenção autônomo `vitalia_tmp_cleanup.py`, acionado de forma isolada e fora do pipeline cognitivo de raciocínio da IA.

### 2.2. Unificação da Persistência de Integridade na Camada 4 (`data_storage`)
- Toda persistência auditável de projeto reside estritamente em `.vitalia/memory/data_storage/`:
  - **Backups de Skills:** `<project_root>/.vitalia/memory/data_storage/backups/skills/`
  - **Manifestos de Hash SHA-256:** `<project_root>/.vitalia/memory/data_storage/manifests/.vitalia-manifest`
- A raiz de `.vitalia/` permanece estritamente pura, contendo apenas metadados canônicos locais (`feature.json`, `pipeline.json`).

### 2.3. Resolução Defensiva de Diretórios e Invariante de Pureza de Caminhos
- `resolve_kit_dir()` valida fisicamente se o candidato apontado pela variável de ambiente existe em disco (`if candidate.exists(): return candidate`). Caso o caminho configurado não exista, o sistema executa fallback defensivo e seguro para o diretório raiz do script em execução (`script_kit_root` com `profiles/constitution.yaml`).
- É estritamente proibido hardcodar `source/` ou `~/.vitalia` em scripts ou prompts do kit novo. No código do kit, `.vitalia/` refere-se **sempre** à pasta local do projeto alvo.

### 2.4. Nomenclatura Idempotente de Skills (`skill_generator.sh`)
- `skill_generator.sh` aplica strip de prefixo redundante (`local base_name="${ext_name#vitalia-}"; update_skill "vitalia-${base_name}" ...`), assegurando que 100% das pastas em `.agents/skills/` sigam a convenção única `vitalia-<workflow>/`.

### 2.5. Suíte de Sensores em Tempo Real (Vitalia Runtime Sensor Suite — VRSS)
- Arquitetura de observabilidade estruturada em 5 classes:
  1. *Contrato & DbC Sensor:* Validação contra esquemas OpenAPI 3.0 Limpos.
  2. *Execução Comportamental Sensor:* Sentinel de exit codes e poda de tracebacks do Pytest.
  3. *Estático & Código Sensor:* AST parser pós-escrita e bloqueio de violações sintáticas.
  4. *Cognitivo & Contexto Sensor:* Circuit breaker contra loops e monitoramento de saturação.
  5. *Preservação & Higiene Sensor:* Fiscalização de pureza estrita em `.agents/skills/`.
- Pipeline de feedback estruturado: *Slicing & Redaction* $\longrightarrow$ *Structured Error Envelope (JSON)* $\longrightarrow$ *Context Lifting* $\longrightarrow$ *Inverted CoT*.

### 2.6. Cálculo Determinístico de Ambiguidades (`sdd_ambiguity_scorer.py`)
- Desacoplamento da pontuação matemática de ambiguidades para o script CLI `sdd_ambiguity_scorer.py` e perfil dedicado `source/profiles/ambiguity_scoring.yaml`, preservando o Princípio da Responsabilidade Única (SRP) e eliminando alucinações aritméticas do LLM.

---

## 3. Consequências

- **Positivas:** Redução de mais de 1.500 tokens de ruído por turno; eliminação de distrações cognitivas e alucinações do modelo; conformidade total com o contrato de consumo da Antigravity IDE (Progressive Disclosure puro); observabilidade estruturada em falhas; e integridade determinística de dados na Camada 4.
- **Trade-offs:** Exige que a suíte de testes P05 adicione asserções comportamentais provando o expurgo de `tmp_cleanup_matrix`, a idempotência de nomenclatura de skills e a criação de backups na pasta correta de `data_storage`.

