<!-- plan.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:20(GMT-04:00) -->
> **plan.md | Vitalia SPEC Kit v0.0.1 | 02-11-2026 23:20(GMT-04:00)**

# Implementation Plan: Sub-Agente SDD-Judge & Governança Constitucional Nativa

**Branch**: `001-sdd-judge-subagent` | **Data**: 02-11-2026 23:20(GMT-04:00)  
**Spec**: [specs/001-sdd-judge-subagent/spec.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/001-sdd-judge-subagent/spec.md)  
**Status**: DRAFT (Submetido a Gate Constitucional HITL)  

---

## 1. Summary

Implementação do **Sub-Agente `sdd-judge`** como auditor constitucional adversarial de primeira classe operando nativamente dentro da IDE Antigravity com modelos de fronteira (Gemini Pro, 1M–2M tokens). A solução substitui o script CLI legado (`sdd_judge.py`) que sofria de estouros de VRAM de 400 tokens e truncamentos cegos.

O plano estrutura:
1. O registro do agente em `source/profiles/agents_catalog.yaml`.
2. A extensão `source/extensions/judge.toml` e a skill `.agents/skills/vitalia-judge/SKILL.md`.
3. As técnicas anti-diluição (Sanduíche Constitucional, Inverted CoT, Delimitação XML e Matriz de Confronto 1-a-1).
4. O saneamento das 4 extensões do ciclo em `source/extensions/` (`spec-specify.toml`, `spec-plan.toml`, `spec-tasks.toml`, `converge.toml`), eliminando comandos CLI legados.
5. A padronização estrita de schemas em dialeto OpenAPI 3.0 puro (sem `$schema`, sem `title` no nó raiz e sem `additionalProperties: false`), prevenindo falhas HTTP 400 no compilador REST do Google Gemini.
6. A preservação absoluta da herança estável de 31-10-2026 (`source/bin/lib/*.sh` e `resolve_project_root()` em `vitalia_handoff.py`).

---

## 2. Technical Context

- **Linguagem / Runtime**: Python 3.10+ (scripts auxiliares e runners) e Shell Bash/Zsh (POSIX compliant).
- **Ambiente de Orquestração**: IDE Google Antigravity com Context Lifting (§11 Guardian via `vitalia_hook_runner.py`).
- **Nível de Modelo LLM**: `frontier` (Google Gemini 1.5/2.0/3.0 Pro, 1M-2M tokens) para raciocínio adversarial e ingestão holística de ~3.000 tokens de constituição.
- **Formato de Contratos**: YAML 1.2 e JSON Dialeto OpenAPI 3.0 (Zero meta-campos).
- **Repositório**: Scaffold Puro com espelhamento direto de `source/` para kit global `~/.vitalia/`.
- **Fronteiras e Restrições Invioláveis**:
  - `source/bin/lib/*.sh`: intocável.
  - `source/src/vitalia_handoff.py` (`resolve_project_root()`, `resolve_storage_dir()`): intocável.
  - Ollama local / GPU 6GB: em repouso até produção com PHI/PII on-premise.

---

## 3. Constitution Check (Resultado da Avaliação Prévia)

| Princípio | Requisito / Diretriz | Status no Plano | Racional |
|---|---|:---:|---|
| **P00** | Human Wellbeing First | ✅ APROVADO | Elimina frustração técnica com falhas silenciosas de auditoria e garante integridade do código gerado. |
| **P01** | SDD Pipeline Inviolability | ✅ APROVADO | Respeita a ordem estrita: `spec.md` aprovado ➔ `plan.md` formalizado ➔ `tasks.md` atômico. |
| **P02** | User Impact Declaration | ✅ APROVADO | Declaração explícita de impacto e mitigação de riscos documentada na spec e neste plano. |
| **P03** | Grounding Protocol | ✅ APROVADO | Todas as decisões técnicas ancoradas em fontes com HTTP 200 verificado em [research.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/001-sdd-judge-subagent/research.md). |
| **P04** | Timestamp GMT-04:00 | ✅ APROVADO | Todos os artefatos com cabeçalho duplo e fuso `GMT-04:00` padronizado. |
| **P06** | Secrets Never in Git | ✅ APROVADO | Zero segredos; chaves e credenciais gerenciadas exclusivamente via ambiente `.env` local. |
| **P07** | Privacy by Design | ✅ APROVADO | Isolamento de memória remota em `.vitalia/memory/` fora do versionamento do produto. |
| **P11** | Hardware Agnosticism & Schemas | ✅ APROVADO | Modelos parametrizados via perfis Guardian e schemas 100% OpenAPI 3.0 limpos (sem erro 400). |

---

## 4. Technical Decisions

Decisões detalhadas e registradas formalmente em [specs/001-sdd-judge-subagent/research.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/001-sdd-judge-subagent/research.md):
- **ADR-001**: Sub-Agente nativo da IDE Antigravity com perfil `frontier` em substituição ao script CLI fatiado.
- **ADR-002**: Adoção do Sanduíche Constitucional + Inverted CoT + Matriz 1-a-1 contra a diluição de regras.
- **ADR-003**: Padronização mandatória em OpenAPI 3.0 puro, eliminando meta-campos (`$schema`, `title`, `additionalProperties: false`).
- **ADR-004**: Saneamento das 4 extensões do SDD em `source/extensions/` substituindo o CLI pelo despacho do `/vitalia-judge`.

---

## 5. Project Structure

### Documentation (esta feature)
```
specs/001-sdd-judge-subagent/
├── checklists/
│   └── requirements.md                       # Checklist de qualidade da spec
├── contracts/
│   └── judge-verdict.schema.json             # Contrato OpenAPI 3.0 do veredito de inspeção
├── data-model.md                             # Modelagem de dados e entidades
├── plan.md                                   # Este plano de implementação
├── quickstart.md                             # Guia executável de validação
├── Relatório de Inspeção - specify.md        # Parecer constitucional da spec (PASS)
├── Relatório de Inspeção - plan.md           # Parecer constitucional do plan (PASS)
├── research-brainstorming.md                 # Concepção inicial
├── research.md                              # Rastro técnico e justificativas de arquitetura
├── sdd-session-briefing.md                   # Briefing de transição e escopo
└── spec.md                                   # Especificação formal aprovada
```

### Source Code (arquivos afetados no repositório)
```
source/
├── extensions/
│   ├── converge.toml                         # Refatoração: remoção de sdd_judge.py
│   ├── judge.toml                            # Criação: extensão nativa do Sub-Agente SDD-Judge
│   ├── spec-plan.toml                        # Refatoração: remoção de sdd_judge.py
│   ├── spec-specify.toml                     # Refatoração: remoção de sdd_judge.py
│   └── spec-tasks.toml                       # Refatoração: remoção de sdd_judge.py
├── profiles/
│   └── agents_catalog.yaml                   # Atualização: registro oficial do agente sdd-judge
└── .agents/skills/
    └── vitalia-judge/
        └── SKILL.md                          # Criação: skill de acionamento do juiz na IDE
```

---

## 6. Phase Overview

### Fase 1: Setup & Registro de Identidade (Fundação)
- Registrar o agente `sdd-judge` em [source/profiles/agents_catalog.yaml](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/profiles/agents_catalog.yaml) com status `active`, `model_hint: "frontier"`, gates e `hitl_required: true`.
- Validar a integridade sintática de `agents_catalog.yaml`.

### Fase 2: Implementação do Sub-Agente SDD-Judge & Skill
- Criar a extensão canônica [source/extensions/judge.toml](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/extensions/judge.toml) configurando a injeção do `constitution.yaml` integral, `context_decisions` e `context_learnings`.
- Injetar no prompt do sub-agente o protocolo de **Sanduíche Constitucional**, **Inverted Chain-of-Thought**, delimitação por tags XML e matriz 1-a-1.
- Criar a skill correspondente em `.agents/skills/vitalia-judge/SKILL.md` para acionamento transparente na IDE Antigravity.

### Fase 3: Saneamento das Extensões SDD & Governança OpenAPI 3.0
- Refatorar [source/extensions/spec-specify.toml](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/extensions/spec-specify.toml), removendo hooks legados de `sdd_judge.py`.
- Refatorar [source/extensions/spec-plan.toml](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/extensions/spec-plan.toml), removendo hooks legados de `sdd_judge.py`.
- Refatorar [source/extensions/spec-tasks.toml](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/extensions/spec-tasks.toml), removendo hooks legados de `sdd_judge.py`.
- Refatorar [source/extensions/converge.toml](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/extensions/converge.toml), removendo hooks legados de `sdd_judge.py`.
- Auditar todos os schemas do projeto para certificar 100% de conformidade com OpenAPI 3.0 (sem `$schema`, sem `title` raiz).

### Fase 4: Integração, Testes de Regressão e Verificação Final
- Executar testes automatizados via `pytest` para certificar que os runners e hooks carregam as novas extensões sem erros de sintaxe.
- Testar a execução do Sub-Agente `/vitalia-judge` nos modos `specify` e `plan`.
- Validar que a herança estável (`source/bin/lib/*.sh` e `resolve_project_root()`) permaneceu intacta.
- Emitir o relatório de prontidão para fechamento da feature.
