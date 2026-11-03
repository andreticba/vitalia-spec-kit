<!-- quickstart.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:20(GMT-04:00) -->
> **quickstart.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:20(GMT-04:00)**

# Quickstart & Guia de Validação: Sub-Agente SDD-Judge

**Feature:** `specs/001-sdd-judge-subagent`  
**Objetivo:** Instruções práticas para validação end-to-end do Sub-Agente SDD-Judge e das extensões saneadas na IDE Antigravity.  

---

## 1. Pré-Requisitos

- IDE Antigravity com workspace aberto em `/home/andre/projetos/assistidos/vitalia-spec-kit`.
- Kit Vitalia instalado e espelhado em `~/.vitalia/`.
- Repositório operando como Scaffold Puro com convenção sequencial `specs/<NNN>-<slug>/`.

---

## 2. Cenários de Validação

### Cenário 1: Auditoria Constitucional da Fase de Especificação (`specify`)

1. Abra a IDE e acione o comando:
   ```text
   /vitalia-judge --mode=specify
   ```
2. **Comportamento Esperado:**
   - O Sub-Agente carrega `constitution.yaml` integral via Guardian (§11).
   - Lê sob demanda `specs/001-sdd-judge-subagent/spec.md` e `checklists/requirements.md`.
   - Aplica o Sanduíche Constitucional e Inverted CoT.
   - Emite o artefato físico `specs/001-sdd-judge-subagent/Relatório de Inspeção - specify.md`.
   - Exibe a Matriz de Confronto 1-a-1 no chat e **pausa** para aprovação humana (HITL soberano).

---

### Cenário 2: Auditoria da Fase de Planejamento (`plan`)

1. Acione o comando:
   ```text
   /vitalia-judge --mode=plan
   ```
2. **Comportamento Esperado:**
   - Valida `specs/001-sdd-judge-subagent/plan.md` contra `spec.md`, ADRs e P00-P20.
   - Gera o artefato físico `specs/001-sdd-judge-subagent/Relatório de Inspeção - plan.md`.
   - Pausa para aprovação humana.

---

### Cenário 3: Verificação de Saneamento dos TOMLs em `source/extensions/`

1. Execute no terminal da IDE:
   ```bash
   grep -rn "sdd_judge.py" source/extensions/
   ```
2. **Resultado Esperado:**
   - Nenhuma linha retornada (zero invocações ao CLI legado em `spec-specify.toml`, `spec-plan.toml`, `spec-tasks.toml` e `converge.toml`).

---

### Cenário 4: Validação de Conformidade OpenAPI 3.0 dos Schemas

1. Execute no terminal da IDE:
   ```bash
   grep -rn "\$schema" specs/001-sdd-judge-subagent/contracts/
   ```
2. **Resultado Esperado:**
   - Retorno vazio. O schema `judge-verdict.schema.json` é 100% puro OpenAPI 3.0, livre de meta-campos incompatíveis com o compilador do Gemini REST.

---

### Cenário 5: Verificação de Registro no Catálogo de Agentes

1. Inspecione `source/profiles/agents_catalog.yaml`:
   ```bash
   grep -A 10 "id:.*sdd-judge" source/profiles/agents_catalog.yaml
   ```
2. **Resultado Esperado:**
   - Entidade registrada com `status: "active"`, `model_hint: "frontier"`, `gates: ["specify", "plan", "tasks", "converge"]` e `hitl_required: true`.
