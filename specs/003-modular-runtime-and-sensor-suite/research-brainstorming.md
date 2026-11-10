<!-- research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 13:28(GMT-04:00) -->
> **research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 13:28(GMT-04:00)**

# Síntese de Concepção Socrática & Adicionais de Escopo: Modular Runtime & Sensor Suite (Spec 003)

**Data de Consolidação:** 10-11-2026 13:28 (GMT-04:00)  
**Status Constitucional:** APROVADO PELO OPERADOR (HITL SOBERANO)  
**Workflow de Origem:** `/vitalia-brainstorming` (Nexus Socrático)  
**Destino de Despacho Oficial:** `/vitalia-route`  
**Feature:** `specs/003-modular-runtime-and-sensor-suite`  

---

## 1. Vinculação Mandatória do Corpus Documental da Spec 003

> [!IMPORTANT]
> **DIRETIVA CONSTITUCIONAL DE ESCOPO:**  
> A presente especificação (**Spec 003**) **DEVE COBRIR INTEGRALMENTE** todo o conteúdo, decisões arquiteturais, contratos de interface, suíte de sensores (VRSS), esquemas OpenAPI 3.0 e rotinas de validação detalhadas nos **8 documentos canônicos de concepção transferidos para este diretório**:
>
> 1. [`revisao_contratual_workflows_sdd.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/revisao_contratual_workflows_sdd.md) (~98 KB): Contrato formal e DbC dos 16 workflows centrais, Inverted CoT no SDD-Judge, Socratic Gate, dinamicidade constitucional sem números mágicos e a suíte VRSS de 5 sensores.
> 2. [`revisao_contratual_agentes_especialistas.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/revisao_contratual_agentes_especialistas.md) (~27 KB): As 4 verticais de especialização, os 10 especialistas planejados e o desacoplamento das extensões complementares.
> 3. [`relatorio_contratos_sdd_e_faxineiro.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/relatorio_contratos_sdd_e_faxineiro.md) (~12 KB): Padrões de indústria (OpenSpec, GitHub Spec Kit, Google AIPs, AWS Smithy), Arquitetura Sanduíche para artefatos markdown e especificação do utilitário `vitalia_tmp_cleanup.py`.
> 4. [`relatorio_schemas_e_cobertura.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/relatorio_schemas_e_cobertura.md) (~13 KB): Mapeamento de 100% dos schemas em OpenAPI 3.0 Limpo e roteiro de centralização em `source/src/schemas/`.
> 5. [`roteiro_testes_maquina_limpa_wsl2.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/roteiro_testes_maquina_limpa_wsl2.md) (~8 KB): Roteiro de testes executável em WSL2/zsh em diretório isolado `$HOME/.vitalia-test-kit`.
> 6. [`inventario.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/inventario.md) (~8.7 KB): Índice executivo e síntese das decisões assentadas.
> 7. [`analise-contratual-e-auditoria-kit.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/analise-contratual-e-auditoria-kit.md) (~11.6 KB): Tabela de auditoria por requisito funcional, engenharia de prompts e análise de atenção de modelos de fronteira.
> 8. [`plano-adequacao-kit-legado-turno.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/plano-adequacao-kit-legado-turno.md) (~3.3 KB): Diagnóstico cirúrgico e evidências empíricas da purga de Redis e expurgo da matriz temporária.

Este documento de brainstorming **NÃO substitui nem resume de forma simplificada** o corpus acima; seu propósito estrito é **identificar as lacunas que permaneciam em aberto nesses arquivos e registrar os pontos adicionais obrigatórios pactuados na discussão atual**.

---

## 2. Adicionais de Escopo da Spec 003 (Lacunas Identificadas e Resolvidas)

A análise aprofundada dos documentos acima confrontada com o código real e as exigências operacionais da sessão revelou **6 lacunas críticas** que passam a integrar obrigatoriamente o escopo da Spec 003:

### Adicional 1: Regra Constitucional de Persistência de Backups e Manifestos em `data_storage` (Camada 4)
- **Lacuna nos Documentos Anteriores:** Os scripts `agent_preserver.sh` e `skill_generator.sh` previam salvar backups em `.vitalia/backups/skills/` e manifestos em `.vitalia/.vitalia-manifest`.
- **Decisão Vinculante Assentada:**  
  Toda persistência local, rastros e backups de integridade pertencem estritamente à **Camada 4 (`.vitalia/memory/data_storage/`)**, preservando a pureza absoluta da raiz de `.vitalia/`:
  - **Backups de Skills:** `<project_root>/.vitalia/memory/data_storage/backups/skills/`
  - **Manifestos de Hash SHA-256:** `<project_root>/.vitalia/memory/data_storage/manifests/.vitalia-manifest`
- **Impacto na Spec:** Modificar os contratos de `agent_preserver.sh` e `skill_generator.sh` e adicionar asserções na suíte de testes P05.

### Adicional 2: Erradicação Incondicional da `tmp_cleanup_matrix` do Context Lifting e Runtime
- **Lacuna nos Documentos Anteriores:** O relatório do faxineiro especificou o `vitalia_tmp_cleanup.py` como utilitário interativo, mas não revogou explicitamente a injeção da `tmp_cleanup_matrix` dentro de `guardian_json` pelo `vitalia_hook_runner.py`.
- **Decisão Vinculante Assentada:**  
  A injeção de `tmp_cleanup_matrix` em tempo de execução de workflows é **terminantemente proibida**. Mais de 100 linhas de metadados temporários e menus `[a/d/n/t]` dentro do payload de contexto causam sequestro de atenção e alto risco de alucinação em modelos de fronteira. A limpeza temporária passa a ser uma ferramenta CLI de manutenção autônoma (`vitalia_tmp_cleanup.py`), desvinculada dos prompts dos agentes.
- **Impacto na Spec:** Remoção completa da geração de matrizes de expurgo em `vitalia_hook_runner.py`.

### Adicional 3: Invariante Estrita de Pureza de Caminhos (`source/` e `~/.vitalia` Banidos do Código)
- **Lacuna nos Documentos Anteriores:** Havia referências dispersas e fallbacks hardcoded apontando para `~/.vitalia` ou caminhos relativos de `source/`.
- **Decisão Vinculante Assentada:**  
  - No código do kit, `.vitalia/` **sempre** se refere à pasta local do projeto alvo (`<project_root>/.vitalia/`).
  - Na máquina do usuário alvo, a pasta `source/` **não existe** (o kit é instalado na pasta customizável escolhida pelo usuário, com padrão `~/.vitalia-spec-kit/`).
  - Nem `source/` nem `~/.vitalia` podem constar hardcoded em nenhum script, prompt ou schema do produto.
  - Toda resolução do kit deve derivar exclusivamente de `VITALIA_KIT_DIR` / `kit_env_bootstrap.resolve_kit_dir()`.
- **Impacto na Spec:** Auditoria transversal de strings no repositório `source/` garantindo zero ocorrências de caminhos físicos locais.

### Adicional 4: Resolução Defensiva com Validação de Existência Física em Disco
- **Lacuna nos Documentos Anteriores:** `kit_env_bootstrap.py` retornava o valor de `VITALIA_KIT_DIR` do `.env` incondicionalmente, mesmo que o caminho apontado não existisse em disco, causando falha imediata nos hooks com `Errno 2: No such file or directory`.
- **Decisão Vinculante Assentada:**  
  `resolve_kit_dir()` deve validar fisicamente se o diretório existe (`if candidate.exists(): return candidate`). Caso o caminho configurado na variável de ambiente ou no `.env` não exista no filesystem, o sistema deve realizar fallback defensivo para a raiz do kit executável ativo (`script_kit_root` onde reside `profiles/constitution.yaml`), impedindo quebras operacionais em tempo de execução.
- **Impacto na Spec:** Inclusão de teste de falsificação `[TEST:BUGFIX]` e implementação defensiva em `kit_env_bootstrap.py`.

### Adicional 5: Nomenclatura Idempotente no Instalador (`skill_generator.sh`)
- **Lacuna nos Documentos Anteriores:** `skill_generator.sh` concatenava cegamente `update_skill "vitalia-${ext_name}"`. Se um arquivo de workflow já possuísse o prefixo (ex: `vitalia-route.toml`), gerava pastas com duplicação anômala (`.agents/skills/vitalia-vitalia-route/`).
- **Decisão Vinculante Assentada:**  
  Implementar normalização idempotente via strip de prefixo antes de gerar a skill:
  ```bash
  local base_name="${ext_name#vitalia-}"
  update_skill "vitalia-${base_name}" "${rendered}" "${skills_dir}" "${vitalia_dir}"
  ```
- **Impacto na Spec:** Garantir que 100% das pastas geradas em `.agents/skills/` sigam a convenção única `vitalia-<workflow>` com idempotência absoluta.

### Adicional 6: Delimitação Estrita do Escopo do MVP da Spec 003 aos 16 Workflows Canônicos
- **Lacuna nos Documentos Anteriores:** A coexistência de 28 workflows no ecossistema alargado (`revisao_contratual_agentes_especialistas.md`) criava ambiguidade sobre o escopo de entrega da versão inicial.
- **Decisão Vinculante Assentada:**  
  O MVP da Spec 003 compreende **exclusivamente os 16 workflows canônicos centrais** (`session-start`, `spec-specify`, `judge`, `spec-plan`, `spec-tasks`, `task-verifier`, `spec-implement`, `analyze`, `converge`, `clarify`, `research`, `session-end`, `session-consolidate`, `brainstorming`, `route` e `architect`). As extensões complementares de suporte (`pair.toml`, `debug.toml`, `review.toml`, `medical-gate.toml`, etc.) permanecem mapeadas e reservadas para specs incrementais posteriores.
- **Impacto na Spec:** O `plan.md` e o `tasks.md` da Spec 003 focarão na entrega 100% funcional dos 16 workflows centrais.

---

## 3. Matriz de Requisitos Adicionais para `spec.md`, `plan.md` e `tasks.md`

| Identificador | Requisito Adicional | Descrição Técnica | Artefato Impactado |
| :--- | :--- | :--- | :--- |
| **FR-010** | Persistência de Backups e Manifestos na Camada 4 | Redirecionar backups para `data_storage/backups/skills/` e manifestos para `data_storage/manifests/.vitalia-manifest`. | `agent_preserver.sh`, `skill_generator.sh` |
| **FR-011** | Purga Total da Matriz Temporária do Runtime | Banir `tmp_cleanup_matrix` do `guardian_json` e isolar o faxineiro em CLI de manutenção autônomo. | `vitalia_hook_runner.py` |
| **FR-012** | Invariante de Pureza de Caminhos e Zero Hardcode | Erradicar `source/` e `~/.vitalia` de todo o código-fonte, schemas e prompts produtivos. | Todos os arquivos em `source/` |
| **FR-013** | Resolução Defensiva com Validação Física de Existência | Validar `candidate.exists()` em `resolve_kit_dir()` com fallback para `script_kit_root`. | `kit_env_bootstrap.py` |
| **FR-014** | Nomenclatura Idempotente de Skills | Implementar strip de prefixo `vitalia-` pré-existente antes de aplicar convenção em `skill_generator.sh`. | `skill_generator.sh` |
| **FR-015** | Bounded MVP Scope dos 16 Workflows Canônicos | Formalizar os 16 workflows centrais como meta única de entrega do MVP da Spec 003. | `spec.md`, `plan.md`, `tasks.md` |

---

## 4. Encaminhamento e Próximo Passo

Com o corpus documental integralmente ancorado na pasta `specs/003-modular-runtime-and-sensor-suite/` e os adicionais acima formalizados:
1. O handoff determinístico para `/vitalia-route` já foi registrado em [`.vitalia/memory/data_storage/handoffs/handoff_brainstorming_to_route_ce8f646b.json`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.vitalia/memory/data_storage/handoffs/handoff_brainstorming_to_route_ce8f646b.json).
2. O próximo passo mandatório do pipeline SDD é o acionamento do despachante oficial:
   ```bash
   /vitalia-route
   ```
   para encaminhamento da concepção ao `/vitalia-architect` ou `/vitalia-spec-specify`.
