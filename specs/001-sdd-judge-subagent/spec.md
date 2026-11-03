<!-- spec.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:15(GMT-04:00) -->
> **spec.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:15(GMT-04:00)**

# Especificação de Funcionalidade: Sub-Agente SDD-Judge & Governança Constitucional Nativa

**Data:** 02-11-2026  
**Versão:** 0.0.1  
**Autor/Agente:** Vitalia SPEC Kit Architect  
**Feature:** `specs/001-sdd-judge-subagent`  
**Status:** DRAFT (Aguardando Aprovação HITL)  

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

### 1.1 Declaração de Impacto ao Usuário e Desenvolvedor (Princípio P02)
No ciclo de desenvolvimento guiado por especificações (Spec-Driven Development - SDD), a confiabilidade dos gates de qualidade define a integridade do código gerado. O modelo legado de auditoria (`sdd_judge.py`) operava via chamadas CLI restritas, sujeitas a buffers rígidos de 400 tokens de VRAM e truncamentos arbitrários, resultando no fenômeno de "rule dilution" (diluição de regras), alucinações em modelos locais de 7B e falhas silenciosas na detecção de desvios constitucionais.

Esta funcionalidade estabelece o **Sub-Agente `sdd-judge`** como auditor constitucional adversarial de primeira classe operando nativamente dentro da IDE Antigravity. O novo componente utiliza a janela de contexto de modelos de fronteira (Gemini Pro, 1M–2M tokens) para processar a Constituição integral (`constitution.yaml`) sem fatiamento, assegurando que nenhum princípio bloqueante (P00 a P20) seja violado.

Simultaneamente, a feature formaliza a gênese do repositório **Vitalia SPEC Kit (v0.0.1)** como um Scaffold Puro:
1. Adota a convenção de numeração sequencial da indústria (`specs/<NNN>-<slug>/`).
2. Saneia as 4 extensões centrais em `source/extensions/` (`spec-specify.toml`, `spec-plan.toml`, `spec-tasks.toml`, `converge.toml`), eliminando comandos legados com cortes de tokens.
3. Padroniza todos os schemas contratuais em dialeto **OpenAPI 3.0 limpo** (livre de meta-campos como `$schema`, `title` na raiz e `additionalProperties: false`), prevenindo falhas HTTP 400 em compiladores de Structured Outputs.
4. Preserva integralmente a infraestrutura herdada e testada em 31-10-2026 (`source/bin/lib/*.sh` e `resolve_project_root()` em `vitalia_handoff.py`).

---

## 2. Requisitos Funcionais

### FR-001: Numeração Sequencial Padrão Spec-Kit
O sistema **MUST** exigir que todas as features e comandos do ciclo SDD operem sob o padrão sequencial numérico com 3 dígitos zero-padded (`specs/<NNN>-<slug>/`, ex: `specs/001-sdd-judge-subagent/`).
- O estado ativo **MUST** ser gravado em `.vitalia/feature.json` no formato plano `{"feature_directory": "specs/<NNN>-<slug>", "feature_numbering": "sequential"}`.
- Comandos que criam novas specs **MUST** identificar automaticamente o próximo número disponível escaneando o diretório `specs/`.

### FR-002: Identidade e Catálogo do Sub-Agente SDD-Judge
O arquivo de catálogo `source/profiles/agents_catalog.yaml` **MUST** registrar a entidade oficial do sub-agente `sdd-judge` contendo:
- Identificador `id: "sdd-judge"` e nome descritivo `"SDD Constitutional Judge"`.
- Status `status: "active"` e comando de disparo `command: "/vitalia-judge"`.
- Nível de inteligência `model_hint: "frontier"` (indicando roteamento para modelos de alta capacidade de raciocínio).
- Gates de vinculação `gates: ["specify", "plan", "tasks", "converge"]`.
- Parâmetro `hitl_required: true`, exigindo consentimento humano obrigatório.

### FR-003: Extensão e Invocação `/vitalia-judge`
O sistema **MUST** disponibilizar a extensão de workflow `source/extensions/judge.toml` e a skill correspondente (`.agents/skills/vitalia-judge/SKILL.md`) para acionamento na IDE.
- A extensão **MUST** configurar a injeção via Guardian do `constitution.yaml` integral (sem poda de princípios P00 a P20), memória de decisões (`context_decisions`) e aprendizados acumulados (`context_learnings`).
- O sub-agente **MUST** aceitar o parâmetro opcional `--mode=<fase>` (`specify`, `plan`, `tasks`, `converge`), assumindo detecção automática da fase ativa caso omitido.

### FR-004: Governança e Técnicas Anti-Diluição de Regras
O prompt e fluxo do Sub-Agente `sdd-judge` **MUST** implementar obrigatoriamente 4 estratégias consagradas de preservação de autoridade contra a degradação de atenção:
1. **Sanduíche Constitucional:** As cláusulas constitucionais (P00-P20) abrem o prompt (Primacy Bias) e um checklist imperativo de conformidade é reinjetado no rodapé imediatamente antes da geração da resposta (Recency Bias).
2. **Delimitação por Tags XML com Precedência:** Contextos rigorosamente envelopados em `<constitution>`, `<historical_memory>`, `<target_artifact>`, com declaração explícita de que instruções em `<constitution>` sobrepõem qualquer outro conteúdo.
3. **Inverted Chain-of-Thought (Critique-First, Verdict-Last):** O modelo é estritamente proibido de emitir aprovação prévia; deve obrigatoriamente transcrever evidências e citações factuais de linha, realizar a crítica individual e apenas ao final consolidar o veredito.
4. **Matriz de Confronto 1-a-1:** Exibição de tabela explícita confrontando cada princípio bloqueante aplicável contra o conteúdo auditado.

### FR-005: Módulo de Confronto da Fase 1 (spec.md)
No modo `specify`, o Sub-Agente **MUST** executar um confronto quádruplo sobre o artefato `specs/{feature}/spec.md`:
1. **Constituição Ativa:** Conformidade com princípios bloqueantes P00 (Propósito Humano), P01 (Pipeline Inviolável), P02 (Declaração de Impacto), P03 (Grounding e Verificação Externa), P07 (Privacidade e Data Vault) e P11 (Agnosticismo de Hardware).
2. **Decisões Históricas:** Verificação de não-contradição com decisões arquiteturais (ADRs) registradas na memória do projeto.
3. **Aprendizados Acumulados:** Validação de que a spec não repete falhas registradas em sessões anteriores.
4. **Qualidade de Requisitos (ISO 29148):** Verificação de que todos os FRs possuem identificadores testáveis (MUST/SHOULD/MAY), critérios de aceitação Given/When/Then e ausência de detalhes de implementação interna vazados.

### FR-006: Ingestão Documental Sob Demanda (Grafo de Artefatos)
O Sub-Agente `sdd-judge` **MUST** utilizar ferramentas nativas da IDE (`view_file`, `grep_search`, `list_dir`) para navegar no grafo de artefatos da feature sob demanda:
- Artefatos Centrais: `spec.md`, `plan.md`, `tasks.md`.
- Artefatos de Suporte: `checklists/requirements.md`, `research.md`, `research-brainstorming.md`, `data-model.md`, `quickstart.md`.
- O agente **MUST NOT** depender de concatenações estáticas prévias que truncam ou corrompem referências de arquivos.

### FR-007: Relatório de Inspeção e Gate HITL Soberano
Ao concluir qualquer auditoria, o Sub-Agente **MUST**:
1. Criar e persistir o artefato físico `specs/{feature}/Relatório de Inspeção - {fase}.md`.
2. Registrar o veredito oficial com um dos três status: `PASS` (Aprovado sem ressalvas), `WARN` (Aprovado com recomendações não-bloqueantes), ou `BLOCK` (Reprovado por violação constitucional).
3. Em caso de `BLOCK`, detalhar o princípio violado, a evidência textual, o número da linha e a recomendação de correção.
4. Pausar a execução e solicitar confirmação explícita do desenvolvedor (Human-in-the-Loop soberano) antes de considerar a fase formalmente concluída.

### FR-008: Saneamento de Extensões SDD e Contratos OpenAPI 3.0
As 4 extensões do ciclo em `source/extensions/` (`spec-specify.toml`, `spec-plan.toml`, `spec-tasks.toml` e `converge.toml`) **MUST** ser saneadas:
- Remover invocações ao comando legado `sdd_judge.py` e substituir pelas diretrizes de acionamento do Sub-Agente `/vitalia-judge`.
- Todo schema formal de validação ou contrato de entidade gerado no kit **MUST** aderir estritamente ao dialeto OpenAPI 3.0, sendo estritamente proibido o uso de `$schema`, `title` (como nó de topo) e `additionalProperties: false`.

---

## 3. Requisitos Não-Funcionais e Restrições Arquiteturais

### RN-001: Capacidade de Contexto e Anti-"Lost in the Middle"
O sub-agente deve operar em modelos com janela mínima de 1.000.000 tokens e raciocínio avançado (Gemini 1.5/2.0/3.0 Pro), eliminando a fragmentação de regras e suportando a leitura holística da Constituição (~3.000 tokens) e dos documentos de requisitos.

### RN-002: Compatibilidade Estrita com Compiladores OpenAPI 3.0 (Gemini REST Compliant)
Todos os schemas JSON de contratos devem ser 100% interoperáveis com o compilador de Structured Outputs da Google GenAI, assegurando ausência total de meta-campos que disparam erro HTTP 400.

### RN-003: Padronização de Carimbo Temporal e Assinatura Oficial (Princípio P04)
Todos os artefatos de documentação e código gerados ou modificados devem conter o carimbo institucional:
- Markdown: `<!-- {arquivo} | Vitalia SPEC Kit v0.0.1 | {timestamp} -->`
- Código: `# {arquivo} | Vitalia SPEC Kit v0.0.1 | {timestamp}`

### RN-004: Inviolabilidade da Herança Estável de 31-10-2026
É estritamente proibido recriar, renomear ou modificar a infraestrutura base aprovada:
- `source/src/vitalia_handoff.py`: funções `resolve_project_root()` e `resolve_storage_dir()`.
- `source/bin/lib/*.sh`: bibliotecas `logger.sh`, `env_manager.sh`, `agent_preserver.sh`, `redis_detector.sh`, `git_storage_manager.sh`.
- `source/bin/install-project`.

### RN-005: Isolamento de Memória Remota ("Zero Data Leak", Princípio P07)
Os repositórios de sessão e storage localizados em `.vitalia/memory/session/` e `.vitalia/memory/data_storage/` devem permanecer rigorosamente isolados e fora do controle de versão do produto principal via `.gitignore`.

### RN-006: Desempenho e Latência de Inspeção
A auditoria completa de uma fase deve ser computada e apresentar o relatório de inspeção na IDE em menos de 30 segundos sob conexão estável.

---

## 4. Histórias de Usuário (User Stories)

### US-001: Auditoria Constitucional Integral na Especificação
**Como um** Engenheiro de Software ou Arquiteto de Sistemas,  
**eu quero** acionar `/vitalia-judge --mode=specify` diretamente na IDE ao concluir a redação de um `spec.md`,  
**para que** a especificação seja confrontada contra toda a Constituição do projeto e ADRs históricas sem truncamento de regras, prevenindo que requisitos defeituosos avancem para o planejamento.

### US-002: Saneamento dos Workflows SDD Sem Quebras de Execução
**Como um** Desenvolvedor operando o ciclo SDD (`/vitalia-spec-specify`, `/vitalia-spec-plan`, etc.),  
**eu quero** que as extensões do kit não dependam de scripts CLI que falham por estouro de VRAM de 400 tokens,  
**para que** o fluxo de desenvolvimento seja fluido, transparente e orientado pelo Sub-Agente especialista.

### US-003: Validação Sem Erro 400 em Chamadas de Estruturação
**Como um** Desenvolvedor de integrações com modelos de IA de fronteira,  
**eu quero** que todos os schemas de entidades do kit sigam OpenAPI 3.0 limpo sem `$schema` ou `title`,  
**para que** as chamadas de Structured Outputs e validações contratuais nunca sofram rejeição HTTP 400 pela API do Google Gemini.

### US-004: Governança Transparente com Human-in-the-Loop Soberano
**Como um** Tech Lead ou Mantenedor do Produto,  
**eu quero** que todo parecer do juiz seja registrado em arquivo persistente (`Relatório de Inspeção - {fase}.md`) e exija aprovação explícita no chat,  
**para que** a IA atue como auditor adversarial rigoroso, mas o humano mantenha a soberania final de decisão e aceite do código.

---

## 5. Critérios de Aceite e Cenários de Usuário (BDD Given/When/Then)

### Cenário 1: Auditoria Bem-Sucedida de spec.md (Veredito PASS)
- **Dado que** o arquivo `specs/001-sdd-judge-subagent/spec.md` existe, contém os 8 requisitos funcionais com tags RFC 2119, critérios Given/When/Then e declaração de impacto ao usuário (P02),
- **Quando** o desenvolvedor executa o comando `/vitalia-judge --mode=specify`,
- **Então** o Sub-Agente `sdd-judge` deve carregar a Constituição integral, executar o Sanduíche Constitucional, gerar o artefato `specs/001-sdd-judge-subagent/Relatório de Inspeção - specify.md` com status `PASS`, exibir a matriz de confronto 1-a-1 e pausar aguardando aprovação humana.

### Cenário 2: Detecção de Violação Constitucional Bloqueante (Veredito BLOCK)
- **Dado que** um arquivo `spec.md` omite a seção de impacto ao usuário (violação P02) ou inclui afirmações técnicas de bibliotecas externas sem rastro de pesquisa (violação P03),
- **Quando** o Sub-Agente `sdd-judge` for acionado para validar o documento,
- **Então** o agente deve apontar a citação textual exata da omissão, emitir status `BLOCK` no relatório de inspeção, listar a ação corretiva necessária e impedir a recomendação de avanço para a fase de planejamento (`/vitalia-spec-plan`).

### Cenário 3: Validação de Conformidade dos TOMLs Saneados
- **Dado que** as extensões `source/extensions/spec-specify.toml`, `spec-plan.toml`, `spec-tasks.toml` e `converge.toml` foram refatoradas,
- **Quando** o comando `grep -rn "sdd_judge.py" source/extensions/` for executado no repositório,
- **Então** nenhuma ocorrência da chamada CLI legada deve ser encontrada nos hooks de fase dessas extensões.

### Cenário 4: Interoperabilidade dos Schemas JSON OpenAPI 3.0
- **Dado** qualquer arquivo de schema JSON formal presente no projeto (ex: `source/src/schemas/`),
- **Quando** o arquivo for submetido à validação de conformidade OpenAPI 3.0,
- **Então** as propriedades `$schema`, `title` (como nó raiz de schemas de validação) e `additionalProperties: false` não devem existir no documento.

### Cenário 5: Verificação de Integridade da Herança Estável
- **Dado** o repositório `vitalia-spec-kit`,
- **Quando** inspecionados os arquivos `source/src/vitalia_handoff.py` e `source/bin/lib/*.sh`,
- **Então** as funções `resolve_project_root()`, `resolve_storage_dir()` e as 5 bibliotecas modulares de shell devem permanecer exatamente com a interface e comportamento aprovados em 31-10-2026.

---

## 6. Success Criteria (Critérios de Sucesso Mensuráveis)

| Métrica | Meta | Método de Medição |
|---|---|---|
| **Cobertura de Requisitos** | 100% dos 8 FRs com cenários BDD | Inspeção visual e checklist de qualidade |
| **Diluição Constitucional** | 0% de princípios ignorados | Matriz de Confronto 1-a-1 no relatório de inspeção |
| **Saneamento de Extensões** | 4 de 4 extensões refatoradas (100%) | `grep` nos TOMLs de `source/extensions/` |
| **Conformidade OpenAPI 3.0** | 100% dos schemas limpos de meta-campos | Validador sintático de schemas JSON |
| **Auditoria Persistente HITL** | 100% das avaliações geram relatório MD | Presença de `Relatório de Inspeção - {fase}.md` |
| **Preservação de Herança** | 0 linhas reimplementadas de infra estável | `git diff` sobre `vitalia_handoff.py` e `lib/*.sh` |

---

## 7. Modelos de Dados e Entidades (Dialeto OpenAPI 3.0 Puro)

### 7.1 Schema do Registro no Catálogo de Agentes (`source/profiles/agents_catalog.yaml`)
```yaml
type: object
required:
  - id
  - name
  - status
  - command
  - role
  - model_hint
  - hitl_required
properties:
  id:
    type: string
    description: "Identificador kebab-case do agente"
  name:
    type: string
    description: "Nome de exibição do agente"
  emoji:
    type: string
    description: "Ícone representativo"
  status:
    type: string
    enum: ["active", "planned", "deprecated"]
  gates:
    type: array
    items:
      type: string
  command:
    type: string
    description: "Slash command para ativação na IDE"
  role:
    type: string
    description: "Papel funcional no ecossistema SDD"
  model_hint:
    type: string
    enum: ["lightweight", "heavy", "frontier"]
  hitl_required:
    type: boolean
    description: "Obrigatoriedade de consentimento humano"
  description:
    type: string
```

### 7.2 Schema do Veredito Estruturado de Inspeção (OpenAPI 3.0 Compliant)
```json
{
  "type": "object",
  "required": [
    "phase",
    "feature",
    "verdict",
    "timestamp",
    "evaluations"
  ],
  "properties": {
    "phase": {
      "type": "string",
      "enum": ["specify", "plan", "tasks", "converge"]
    },
    "feature": {
      "type": "string",
      "description": "Diretório relativo da feature auditada"
    },
    "verdict": {
      "type": "string",
      "enum": ["PASS", "WARN", "BLOCK"]
    },
    "timestamp": {
      "type": "string",
      "description": "Timestamp ISO 8601 com fuso GMT-04:00"
    },
    "evaluations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "principle_id",
          "principle_name",
          "status",
          "critique"
        ],
        "properties": {
          "principle_id": {
            "type": "string",
            "description": "Identificador do princípio (ex: P01, P02)"
          },
          "principle_name": {
            "type": "string",
            "description": "Nome canônico do princípio constitucional"
          },
          "status": {
            "type": "string",
            "enum": ["COMPLIANT", "VIOLATION", "NOT_APPLICABLE"]
          },
          "evidence": {
            "type": "string",
            "description": "Citação factual extraída do artefato avaliado"
          },
          "critique": {
            "type": "string",
            "description": "Análise crítica do avaliador"
          },
          "suggested_fix": {
            "type": "string",
            "description": "Recomendação acionável de correção em caso de violação"
          }
        }
      }
    }
  }
}
```

---

## 8. Fora do Escopo (Out of Scope)

- **Inferência Local via Ollama / VRAM 6GB:** Congelada formalmente nesta versão; o sistema opera exclusivamente via modelos de fronteira na IDE.
- **Reimplementação de Infraestrutura Shell:** Proibida a recriação das funções modulares em `source/bin/lib/*.sh` (`env_manager.sh`, `agent_preserver.sh`, `logger.sh`, etc.).
- **Reimplementação de Resolvedor de Projeto:** Proibida a alteração das rotinas `resolve_project_root()` e `resolve_storage_dir()` em `vitalia_handoff.py`.
- **Symlinks Atômicos de Deploy (Capistrano Swap):** Descartados em prol do espelhamento canônico direto de `source/` para `~/.vitalia/`.
- **Dashboards Visuais e Interfaces Gráficas Externas:** O escopo é estritamente confinado ao ecossistema de sub-agentes, skills, CLI e hooks da IDE Antigravity.

---

## 9. Suposições e Dependências

- **Ambiente de Execução:** IDE Antigravity com suporte ativo a sub-agentes, leitura de contexto dinâmico via Guardian (§11) e comandos slash nativos.
- **Modelos de IA:** Disponibilidade de modelos de raciocínio de alta janela (Gemini 1.5/2.0/3.0 Pro) sem cotas restritivas de VRAM local para esta etapa.
- **Topologia de Diretórios:** O repositório opera como Scaffold Puro, espelhando sua pasta `source/` para o kit global em `~/.vitalia/`.

---

## 10. Suposições Verificadas e Rastro de Grounding (Princípio P03)

Todas as fontes e afirmações técnicas foram verificadas via requisição direta com retorno HTTP 200 confirmado:

| # | Afirmação Técnica / Conceito | Fonte Oficial Verificada (HTTP 200) | Data | Status |
|---|---|---|:---:|:---:|
| 1 | Arquitetura de Constitutional AI baseada em princípios e autoridade explícita | [Anthropic Research — Constitutional AI (arXiv:2212.08073)](https://arxiv.org/abs/2212.08073) | 02-11-2026 | Confirmado |
| 2 | Degradação de atenção posicional em LLMs de contexto longo ("Lost in the Middle") | [arXiv:2307.03172 — Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) | 02-11-2026 | Confirmado |
| 3 | Convenção sequencial de numeração para especificações (`specs/<NNN>-<slug>/`) | [GitHub Spec Kit Repository](https://github.com/github/spec-kit) | 02-11-2026 | Confirmado |
| 4 | Framework de avaliação de modelos e rubricas estruturadas de auditoria | [OpenAI Evals Framework](https://github.com/openai/evals) | 02-11-2026 | Confirmado |
| 5 | Princípios de IV&V (Independent Verification & Validation) e Red Teaming em IA | [NIST AI Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/itl/ai-risk-management-framework) | 02-11-2026 | Confirmado |
| 6 | Governança de segurança e guardrails arquiteturais no ciclo de desenvolvimento com IA | [Google Secure AI Framework (SAIF)](https://safety.google/safety/saif/) | 02-11-2026 | Confirmado |
| 7 | Engenharia de requisitos, atomicidade e verificabilidade conforme padrão ISO 29148 | [ISO/IEC/IEEE 29148 Systems and Software Engineering](https://standards.ieee.org/ieee/29148/7212/) | 02-11-2026 | Confirmado |

---

<!-- Fim da spec.md | Vitalia SPEC Kit v0.0.1 -->
