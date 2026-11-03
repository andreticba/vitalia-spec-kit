<!-- data-model.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:20(GMT-04:00) -->
> **data-model.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:20(GMT-04:00)**

# Modelagem de Dados e Entidades Contratuais (OpenAPI 3.0 Clean)

**Data:** 02-11-2026 23:20(GMT-04:00)  
**Feature:** `specs/001-sdd-judge-subagent`  
**Conformidade:** Dialeto OpenAPI 3.0 (Zero meta-campos: sem `$schema`, sem `title` raiz, sem `additionalProperties: false`)  

---

## 1. Entidade: Registro do Sub-Agente no Catálogo (`source/profiles/agents_catalog.yaml`)

Define a estrutura do agente no catálogo de especialistas do kit.

```yaml
type: object
required:
  - id
  - name
  - emoji
  - status
  - gates
  - command
  - role
  - model_hint
  - hitl_required
  - description
properties:
  id:
    type: string
    description: "Identificador único kebab-case do agente (ex: sdd-judge)"
  name:
    type: string
    description: "Nome de exibição amigável"
  emoji:
    type: string
    description: "Glifo visual do agente"
  status:
    type: string
    enum:
      - "active"
      - "planned"
      - "deprecated"
  gates:
    type: array
    items:
      type: string
    description: "Fases do ciclo SDD em que o agente atua"
  command:
    type: string
    description: "Slash command de ativação na IDE"
  role:
    type: string
    description: "Missão e papel funcional no ecossistema SDD"
  model_hint:
    type: string
    enum:
      - "lightweight"
      - "heavy"
      - "frontier"
  sub_agents:
    type: array
    items:
      type: string
    description: "Sub-agentes subordinados (se houver)"
  hitl_required:
    type: boolean
    description: "Exigência mandatória de aprovação humana"
  description:
    type: string
    description: "Descrição detalhada do comportamento e escopo do agente"
```

### Instância Canônica para o SDD-Judge:
```yaml
id: "sdd-judge"
name: "SDD Constitutional Judge"
emoji: "⚖️"
status: "active"
gates: ["specify", "plan", "tasks", "converge"]
command: "/vitalia-judge"
role: "Auditoria constitucional adversarial e guardrail do pipeline SDD"
model_hint: "frontier"
sub_agents: []
data_inputs:
  - type: "feature_graph"
data_outputs:
  - type: "inspection_report"
    format: "markdown"
    path: "specs/{feature}/Relatório de Inspeção - {phase}.md"
hitl_required: true
description: |
  Auditor adversarial de primeira classe nativo na IDE Antigravity.
  Executa inspeção constitucional massiva contra P00 a P20 via Sanduíche Constitucional,
  Inverted Chain-of-Thought e Matriz de Confronto 1-a-1, emitindo relatório físico
  com pausa mandatória para aprovação humana soberana.
```

---

## 2. Entidade: Veredito de Inspeção e Relatório de Conformidade

Define a estrutura de dados serializável emitida pela auditoria adversarial.

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
      "description": "Diretório relativo da feature (ex: specs/001-sdd-judge-subagent)"
    },
    "verdict": {
      "type": "string",
      "enum": ["PASS", "WARN", "BLOCK"]
    },
    "timestamp": {
      "type": "string",
      "description": "Timestamp ISO 8601 com fuso GMT-04:00"
    },
    "summary": {
      "type": "string",
      "description": "Síntese executiva da avaliação"
    },
    "evaluations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "principle_id",
          "principle_name",
          "severity",
          "status",
          "critique"
        ],
        "properties": {
          "principle_id": {
            "type": "string",
            "description": "ID do princípio (ex: P01, P02, P11)"
          },
          "principle_name": {
            "type": "string",
            "description": "Nome canônico do princípio"
          },
          "severity": {
            "type": "string",
            "enum": ["BLOCKING", "WARNING", "INFO"]
          },
          "status": {
            "type": "string",
            "enum": ["COMPLIANT", "VIOLATION", "NOT_APPLICABLE"]
          },
          "line_reference": {
            "type": "string",
            "description": "Linhas do artefato onde a evidência foi encontrada"
          },
          "evidence": {
            "type": "string",
            "description": "Citação factual extraída do documento"
          },
          "critique": {
            "type": "string",
            "description": "Análise crítica do juiz adversarial"
          },
          "suggested_fix": {
            "type": "string",
            "description": "Recomendação prescritiva em caso de não-conformidade"
          }
        }
      }
    }
  }
}
```

---

## 3. Entidade: Configuração de Estado Ativo (`.vitalia/feature.json`)

Instância plana de dados usada para coordenar o ciclo de vida da feature ativa.

```json
{
  "feature_directory": "specs/001-sdd-judge-subagent",
  "feature_numbering": "sequential"
}
```
*(Nota de conformidade: `.vitalia/feature.json` é estritamente uma instância de runtime, não uma definição de schema, evitando erros de metapropriedades).*
