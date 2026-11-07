<!-- requirements.md | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:30:00(GMT-04:00) -->
> **requirements.md | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:30:00(GMT-04:00)**

# Checklist de Requisitos — Spec 003: Fix Universal Bootstrap Omissions

## 1. Cobertura dos Cenários de Usuário (US1 a US5)
- [x] **US1 (Instalação Limpa Parametrizada):** Suporte a default interativo `~/.vitalia-spec-kit` e caminhos customizados com expansão de `~`.
- [x] **US2 (Ativação e Log em Memória):** Acumulação em memória, gravação condicional de log, backup condicional de `.agents` e purga do Gemini CLI.
- [x] **US3 (Governança Temporal e Padrão SRP):** 10 domínios canônicos em `grounding_domains.yaml`, 9 domínios em `dynamic_questioning.yaml` e decisões orientadas a SRP.
- [x] **US4 (Dashboard de Memória Rico):** Renderização fiel com badges, Mermaid, tabela rica e seções `<details>` colapsáveis.
- [x] **US5 (Workflow `/vitalia-analyze`):** Modos `after_tasks` e `after_implement` com Git Diff em 3 camadas, validação estática de call-sites e pausa HITL soberana.

## 2. Requisitos Funcionais (FR-001 a FR-023)
- [x] **FR-001 a FR-004:** Bootstrap global atômico, instalação filtrada sem `cp -r` cego, zero `gp_*`, zero `redis_detector.sh`, shim com `VITALIA_KIT_DIR`.
- [x] **FR-005 a FR-007:** Resolução em 3 níveis sem dependência de `source/` no runtime e purga total de `~/.vitalia`.
- [x] **FR-008 a FR-012:** Buffer de log, gravação condicional, proteção de `.agents`, eliminação do Gemini CLI e template `SKILL.md` válido na linha 1.
- [x] **FR-013 a FR-018:** 10 domínios canônicos com datas futuras e fontes autoritativas, padrão SRP em arquitetura e purga de `guardian_profile` nos 11 `.toml`.
- [x] **FR-019 a FR-020:** Template `dashboard_template.md` em `source/templates/` e integração no motor de consolidação em `vitalia_context_engine.py`.
- [x] **FR-021 a FR-022:** Extensão `analyze.toml` como workflow nativo de IDE com relatório dual e pausa HITL.
- [x] **FR-023:** Teste de fumaça E2E em sandbox temporário (`tmp_path`) sem tocar na máquina host.

## 3. Critérios Constitucionais
- [x] **P00 (Human Wellbeing First):** Segurança clínica e prioridade de valor humano preservadas.
- [x] **P01 (SDD Pipeline Inviolability):** Spec formal completa antes de qualquer código.
- [x] **P03 (External Verification Protocol / Grounding):** Todas as fontes externas e URLs canônicas verificadas.
- [x] **P04 (Timestamp GMT-04:00):** Cabeçalho duplo em formato de comentário HTML e citação visível com fuso GMT-04:00 imutável.
- [x] **P11 (Hardware Agnosticism):** Purga total de dependências locais de Redis, Celery, GPU/VRAM e Ollama.
