<!-- relatorio_contratos_sdd_e_faxineiro.md | Vitalia SPEC Kit v0.0.1 | 09-11-2026 16:35(GMT-04:00) -->
> **relatorio_contratos_sdd_e_faxineiro.md | Vitalia SPEC Kit v0.0.1 | 09-11-2026 16:35(GMT-04:00)**

# Relatório Técnico: Contratos de Artefatos SDD, Centralização de Schemas e Especificação do Novo Faxineiro de Contexto

Este documento consolida as decisões de engenharia, a fundamentação baseada em pesquisa da indústria e o design detalhado de implementação para três frentes estratégicas do Vitalia SPEC Kit:
1. **Contratos Formais de Entrada/Saída para Artefatos SDD** (`spec.md`, `plan.md`, `tasks.md`, relatórios de inspeção).
2. **Centralização e Migração dos Schemas** (integração de schemas de teste em runtime e migração do legado).
3. **Design e Especificação do Novo Faxineiro de Contexto** (`vitalia_tmp_cleanup.py`).

---

## 1. Contratos Formais para Artefatos SDD: Pesquisa da Indústria e Matriz Decisória

A pesquisa técnica realizada na Web investigou padrões formais da indústria para especificação estruturada:
- **OpenSpec & GitHub Spec Kit:** O ciclo SDD opera como um Grafo Acíclico Dirigido (DAG), onde cada artefato (`proposal.md` $\rightarrow$ `spec.md` $\rightarrow$ `plan.md` $\rightarrow$ `tasks.md`) consome o anterior como pré-condição estrita e impõe identificadores rastreáveis (`FR-xxx`, `SC-xxx`, `Txxx`).
- **Google AIPs (`api-linter`) e AWS Smithy:** Regras de design de API e contratos não dependem de boa vontade; utilizam *Trait Constraints* (`@required`, `@pattern`, `@idRef`) e validadores determinísticos de tempo de compilação.
- **MADR (Markdown Architectural Decision Records):** Padrão consolidado que combina prosa rica com seções e metadados estruturados.

---

### 1.1. Matriz Decisória das Abordagens de Validação de Artefatos

| Critério de Avaliação | Abordagem A: Markdown Puro + Regex | Abordagem B: Frontmatter YAML + JSON Schema / Pydantic | Abordagem C: JSON/YAML Canônico Intermediário (IR) + Jinja2 | Abordagem D: Linting Semântico via AST (markdown-it-py) |
| :--- | :---: | :---: | :---: | :---: |
| **Resiliência a Espaçamentos e Linhas** | 🔴 Muito Baixa (quebra fácil) | 🟡 Alta no cabeçalho; Nula no corpo | 🟢 Máxima (indiferente à formatação) | 🟢 Muito Alta (ignora espaçamentos) |
| **Falsos Positivos em Blocos de Código** | 🔴 Alto Risco (confunde `# Titulo` dentro de bash) | 🟢 Zero no cabeçalho; Alto no corpo | 🟢 Zero (código é string isolada) | 🟢 Zero (blocos de código são nós `fence` isolados) |
| **Validação de DAG e Rastreabilidade** | 🔴 Muito Pobre | 🟢 Excelente (Pydantic valida tipos/listas) | 🟢 Excelente (JSON tipado em memória) | 🟡 Moderada |
| **Validação de Tabelas GFM e Seções** | 🟡 Frágil | 🔴 Inexistente para o corpo | 🟡 Rígida (força prosa em JSON) | 🟢 Ideal (valida colunas e nós de cabeçalho) |
| **Ergonomia e Edição Humana (Git)** | 🟢 Alta (Markdown comum) | 🟢 Excelente (padrão Hugo/Astro/Jekyll) | 🔴 Muito Ruim (Round-trip conflituoso) | 🟢 Excelente (Markdown padrão legível) |
| **Feedback de Auto-Correção para LLM** | 🔴 Ruidoso | 🟢 Preciso (`ValidationError`) | 🟢 Nativo e Preciso (`loc` do campo) | 🟢 Muito Preciso (linha, nó e regra) |

---

### 1.2. Decisão Arquitetural: A "Arquitetura Sanduíche" (Padrão Recomendado)

Adotamos a **Arquitetura Sanduíche**, combinando a **Abordagem B** (para o cabeçalho) com a **Abordagem D** (para o corpo):

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAMADA 1: CABEÇALHO FORMAL (YAML Frontmatter + Pydantic/OpenAPI 3.0)   │
│ Valida metadados em python-frontmatter: id, status, fuso GMT-04:00,   │
│ autor, versão SemVer e array requirements_index: ["FR-001", ...]       │
├────────────────────────────────────────────────────────────────────────┤
│ CAMADA 2: CORPO SEMÂNTICO (Validação de AST via markdown-it-py)        │
│ Valida hierarquia de seções (H1 -> H2 -> H3 sem saltos), tabelas GFM   │
│ com colunas obrigatórias e isolamento estrito de blocos de código.     │
├────────────────────────────────────────────────────────────────────────┤
│ CAMADA 3: GRAFO DE RASTREABILIDADE CRUZADA (Traceability Engine)       │
│ Valida que todo FR-xxx possui SC-xxx correspondente, e que toda tarefa │
│ Txxx em tasks.md referencia explicitamente um par (FR-xxx, SC-xxx).    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Centralização de Schemas e Migração do Legado

### 2.1. Onde os Schemas Devem Residir (Topologia Única)
- **Repositório Fonte:** `source/src/schemas/*.schema.json`
- **Kit Instalado no Host:** `${VITALIA_KIT_DIR}/src/schemas/*.schema.json`
- **Registro Centralizado:** Um módulo `source/src/core/schema_registry.py` com a função:
  ```python
  def get_schema_for_type(schema_type: str) -> Path
  ```
  Isso elimina as tuplas hardcoded nos testes e nos scripts. Qualquer componente que precise validar um YAML ou JSON simplesmente consulta o registry.

### 2.2. Como Trazer os Schemas de `~/.vitalia/` para o Novo Kit
1. **`ambiguity_taxonomy_schema.json` (Migrar e Adequar):**  
   - Mover para `source/src/schemas/ambiguity_taxonomy.schema.json`.  
   - Adequação: Remover `$schema`, remover `title` de raiz e assegurar conformidade estrita com OpenAPI 3.0 Limpo.  
   - Uso: Utilizado pelo `/vitalia-clarify` para validar o arquivo de métricas `specs/*/ambiguity_metrics.json`.
2. **Schemas Obsoletos do Legado (Descontinuar / Purgar):**  
   - `tmp_cleanup_matrix.schema.json`: Descontinuado (pertencia ao expurgo de `~/.vitalia/tmp/`).
   - `section_eval_schema.json` e `task_eval_schema.json`: Descontinuados (pertenciam ao script CLI `sdd_judge.py` fatiado em 400 tokens, substituído pelo Sub-Agente nativo SDD-Judge).

### 2.3. Como Ativar os Schemas em Runtime (Saindo do Escopo Apenas de Teste)
Para que os schemas operem em tempo real no produto:
- **No `vitalia_hook_runner.py`:** Antes de escrever o envelope JSON de contexto na pasta `.vitalia/memory/data_storage/context/<machine_id>/`, invocar `jsonschema.validate(instance=data, schema=context_envelope_schema)`. Se falhar, emitir erro descritivo no `stderr` e abortar antes de entregar dados corrompidos à IDE.
- **No `vitalia_context_engine.py`:** Antes de inserir itens em `learnings.jsonl` e `decisions.jsonl`, validar cada entrada contra `learning.schema.json` e `decision.schema.json`.
- **No `vitalia_handoff.py`:** Já valida contra `vitalia-handoff-v1.0.0.json` (manter ativo).

---

## 3. Especificação do Novo Faxineiro de Contexto (`vitalia_tmp_cleanup.py`)

### 3.1. Requisitos e Diagnóstico
- **Localização dos Envelopes no Kit Novo:**  
  `.vitalia/memory/data_storage/context/<machine_id>/*`
- **Problema de Apagar Indiscriminadamente:**  
  O desenvolvedor precisa ter acesso ao histórico de envelopes de sessões anteriores para debugar prompts ou auditar decisões. A limpeza nunca pode ser automática e silenciosa.

### 3.2. Comportamento Interativo e Terminal CLI
O utilitário será implementado em `source/src/maintenance/vitalia_tmp_cleanup.py` e disponibilizado via CLI (`vitalia-tmp-cleanup`) ou acionado pelo `session-start`.

#### Exemplo Visual da Saída no Terminal / Chat:

```text
[vitalia_tmp_cleanup] Arquivos por data em `.vitalia/memory/data_storage/context/`:

  📅 [1] 25-08-2026 (12 arquivos — 48 KB):
      session-start_20260825_112872_a1b2.json, brainstorming_20260825_113045_c3d4.json, ...

  📅 [2] 26-08-2026 (8 arquivos — 32 KB):
      spec-plan_20260826_091520_e5f6.json, spec-tasks_20260826_094012_g7h8.json, ...

  📅 [3] 27-08-2026 (6 arquivos — 24 KB):
      spec-implement_20260827_142010_i9j0.json, judge_20260827_153040_k1l2.json, ...

  📅 [4] 28-08-2026 (10 arquivos — 87 KB):
      brainstorming_20260828_180012_m3n4.json, session-end_20260828_191020_o5p6.json, ...

  📅 hoje (29-08-2026, sessão ativa — preservada automaticamente)

  ──────────────────────────────────────────────────────────────────────────
  Total elegível para limpeza (exceto hoje): 36 arquivos | 191 KB

  O que deseja fazer?
  [a] Apagar tudo (exceto hoje)
  [d] Selecionar datas para apagar
  [n] Não apagar nada (padrão)
  [t] Apagar tudo (inclusive hoje)
  Escolha [a/d/n/t]:
```

#### Comportamento da Opção `[d]` (Seleção Granular por Índices):
Ao escolher `d`, o sistema solicita os índices:
```text
  Datas para apagar (ex: 1,2,3 ou 1-3): 1,2
  [vitalia_tmp_cleanup] 20 arquivos das datas 25-08-2026 e 26-08-2026 movidos para a lixeira/expurgo (80 KB liberados).
```

### 3.3. Integração com `/vitalia-session-start` (Zero Ruído no Contexto)
Para não poluir o prompt do LLM (evitando o erro do kit legado):
1. O hook de `session-start` verifica rapidamente se existem arquivos de datas anteriores em `.vitalia/memory/data_storage/context/<machine_id>/`.
2. Se **não houver** arquivos antigos, o hook não emite nada.
3. Se **houver** arquivos de datas anteriores acumulados, o resumo não é injetado como um payload JSON pesado no prompt, mas exibido amigavelmente no chat no passo de apresentação:
   ```markdown
   💡 **Manutenção de Disco:** Existem 36 envelopes de sessões anteriores (191 KB) em `.vitalia/memory/data_storage/context/`.
   Para gerenciar a limpeza por datas, execute no terminal:
   `python3 {{VITALIA_KIT_DIR}}/src/maintenance/vitalia_tmp_cleanup.py`
   ```
4. Se o usuário quiser acionar de dentro do chat, o comando de manutenção pode ser disparado interativamente com `ask_question`.

---

## 4. Análise de Escopo: Bounded Context vs. Inchaço da Spec

Em relação ao ponto levantado sobre a delegação do **Architect** para os especialistas da **Vertical de Engenharia** (`django-stark`, `react-vinci`, `infra-nomad`, `cortex-analyst`, `figma-maestro`):

* **Diagnóstico de Engenharia:**  
  A divisão em Bounded Contexts é teoricamente perfeita, mas acionar ativamente todos os 5 especialistas na esteira de código neste momento causaria um **inchaço severo no escopo da spec**.  
* **Recomendação:**  
  Manter o `vitalia-architect` como o condutor central do pipeline SDD (`specify` $\rightarrow$ `clarify` $\rightarrow$ `plan` $\rightarrow$ `tasks` $\rightarrow$ `implement`), e manter os especialistas da Vertical de Engenharia documentados e disponíveis no catálogo e roteador como agentes de consulta e apoio especializado pontual, sem forçar sua execução síncrona obrigatória no pipeline padrão. Isso preserva a governança sem inflar a complexidade da entrega.

---
<sub>Relatório técnico salvo em `TEMP/` com especificações detalhadas prontas para fundamentar a elaboração da spec formal.</sub>

