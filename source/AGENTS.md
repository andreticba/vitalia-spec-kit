<!-- AGENTS.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 22:05(GMT-04:00) -->
> **AGENTS.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 22:05(GMT-04:00)**

# AGENTS.md — Vitalia SPEC Kit

> [!IMPORTANT]
> **Governança Constitucional Dinâmica via §11 Context Lifting.**
> Regras comportamentais, catálogos e guardrails de fase são injetados dinamicamente em runtime pelo **Guardian**. Confie no campo `prompt` do envelope de contexto como guia da missão ativa e em `guardian_json` como as regras constitucionais soberanas do ambiente.

## Topologia Real de 3 Camadas

O ecossistema opera sobre 3 camadas estritamente isoladas:
1. **Camada 1 — Projeto Cliente (`<project_root>/`):** Código-fonte da aplicação, especificações SDD (`specs/`), manifesto `.agents/AGENTS.md` e skills ativas em `.agents/skills/`.
2. **Camada 2 — Kit Global (`<kit_dir>/`, padrão `~/.vitalia-spec-kit/`):** Runtime isolado em `.venv`, executáveis (`bin/`), perfis (`profiles/`), extensões (`extensions/`) e módulos centrais (`src/`).
3. **Camada 3 — Memória e Governança Local (`<project_root>/.vitalia/`):** Metadados de pipeline, backups, contexto de sessão (`memory/session/`) e armazenamento seguro de envelopes (`memory/data_storage/`).

## Diretrizes de Operação e Convivência

1. **Separação de Preocupações:** Cada workflow aciona o `vitalia_hook_runner.py` no Passo 1 com elevação proativa (`BypassSandbox: true`), carregando o envelope JSON integral gerado pelo Guardian sem podas de contexto.
2. **Ciclo de Desenvolvimento Orientado a Especificações (SDD):** Toda evolução de funcionalidade inicia pela especificação formal (`specs/<NNN>-<slug>/`), planejamento arquitetural (`plan.md`), decomposição atômica (`tasks.md`) e auditoria constitucional antes da implementação.
3. **Desenvolvimento Orientado a Testes e Falsificação Comportamental:** Tarefas de teste declaram sua modalidade e Cenário de Falsificação. A governança e os critérios de aceitação BDD (Given/When/Then) são assegurados pelas regras constitucionais ativas injetadas no workflow.
4. **Sessão Contínua:** Inicie novas sessões de trabalho via `/vitalia-session-start` para restauração do estado cognitivo e consolide aprendizados e shards ao finalizar via `/vitalia-session-end`.
