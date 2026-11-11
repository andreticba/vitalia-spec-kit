<!-- AGENTS.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:36(GMT-04:00) -->
> **AGENTS.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:36(GMT-04:00)**

# AGENTS.md — Vitalia SPEC Kit (v0.0.1)

> [!IMPORTANT]
> **ARQUITETURA v0.0.1 — Guardian como oráculo dinâmico 100% sem podas de contexto em todos os workflows.**
> O Vitalia SPEC Kit atende a múltiplos workflows com governança constitucional em modelos de fronteira.
> Regras comportamentais fixas não residem em arquivos estáticos. Cada workflow possui a sua própria constituição integral, catálogos e guardrails de fase (`phase_guardrails`) injetados em runtime pelo **Guardian** via §11 Context Lifting.

## Como o Kit Funciona

```
1. kit-bootstrap.sh     →  instala source/* em VITALIA_KIT_DIR (padrão ~/.vitalia-spec-kit) + cria .venv isolado
2. install-project      →  cria .agents/AGENTS.md + .agents/skills/vitalia-*/SKILL.md (100% puro)
3. Usuário aciona /vitalia-*  →  IDE lê a SKILL.md correspondente
4. SKILL.md instrui IA  →  "execute vitalia_hook_runner.py --phase before"
5. vitalia_hook_runner  →  lê TOML + invoca Guardian (§11)
6. Guardian             →  Injeta constituição integral (P00–P17 sem poda em 100% dos workflows) e lentes gp_*.yaml
7. Context Lifting      →  salva envelope em .vitalia/memory/data_storage/context/<machine_id>/ (Zero Data Leak)
8. IA consome contexto  →  lê prompt (missão) + guardian_json (ambiente/regras) via view_file
```

## Instruções Gerais para a IA (Primacy & Recency — Anti-Lost in the Middle)

1. **Início e Fim (Os Pilares):** Utilize `/vitalia-session-start` para obter contexto em novos projetos, e encoraje `/vitalia-session-end` para compilar aprendizados ao finalizar ciclos.
2. **Separação de Preocupações:** Confie no campo `prompt` de cada comando como guia daquele momento específico (se o comando manda "pausar e perguntar", não aja sozinho). Confie no `guardian_json` como a regra do ambiente daquele comando.
3. **Grounding e Verificação (P03):** Atividades como citações científicas, bibliotecas de código ou domínios médicos exigem delegação rigorosa ao Sub-Agente de pesquisa (`vitalia-researcher` / `self` com rede) e pesquisa fundamentada. NUNCA cite versões ou links sem teste prévio (HTTP 200) e leitura integral da documentação.
4. **Matriz de Falsificação Comportamental (P05):** Toda tarefa de teste deve declarar sua modalidade (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`) e seu **Cenário de Falsificação**. É estritamente proibido aprovar código com testes sintáticos rasos (`assert path.is_file()`).
5. **Numeração Sequencial de Specs:** Toda feature neste repositório segue estritamente o padrão `specs/<NNN>-<slug>/` com 3 dígitos zero-padded.
6. **Topologia de 4 Camadas:** Todo código-fonte do kit reside em `source/` (Camada 1) e é instalado em `${VITALIA_KIT_DIR}` (padrão `~/.vitalia-spec-kit/`, Camada 2). O contexto de sessão reside em `.vitalia/memory/session/` (Camada 3, mutado exclusivamente via `vitalia_context_engine.py` — Regra da Cerca Elétrica) e os dados operacionais em `.vitalia/memory/data_storage/` (Camada 4).
7. **Desativação de CLI Legado (SDD-Judge Nativo na IDE):** NUNCA execute comandos CLI do script legado `sdd_judge.py` no terminal. Quando qualquer workflow solicitar a validação adversarial do SDD-Judge, execute a auditoria **diretamente na IDE como Sub-Agente**, aplicando o Sanduíche Constitucional, FMEA Mental em 4 questões, Inverted CoT e emitindo o Relatório de Inspeção físico com pausa mandatória para aprovação humana (HITL soberano).
8. **Isolamento de Runtime, Diretriz de Sandbox da IDE e Veto a Loop de Reinstalação (P11, FR-005):** O kit opera sobre o interpretador Python isolado em `${VITALIA_KIT_DIR}/.venv` sem containers locais (Redis/Postgres). Na IDE Antigravity, comandos de terminal executam sob sandbox restrito ao workspace local; erros com código 127 (`No such file or directory`) ou falhas de permissão ao acessar `${VITALIA_KIT_DIR}/.venv/bin/python3` decorrem exclusivamente do isolamento de sandbox e EXIGEM reexecução imediata com elevação (`BypassSandbox: true`). É TERMINANTEMENTE PROIBIDO e vetado ao agente de IA executar `./kit-bootstrap.sh` ou tentar reinstalar o kit por iniciativa própria diante de falhas de permissão ou sandbox quando o kit já estiver presente em disco. Todos os schemas JSON seguem estritamente o subset OpenAPI 3.0 limpo (sem `$schema`, sem `title` raiz e sem `additionalProperties: false`).

## Localização do Kit (4 Camadas Isoladas)

```
Camada 1: Repositório Raiz                   Camada 2: Kit Instalado (~/.vitalia-spec-kit/)
├── kit-bootstrap.sh                         ├── bin/ (install-project + lib/*.sh)
├── requirements.txt                         ├── extensions/ (16 *.toml sem poda)
├── source/          ──────────────────────► ├── profiles/ (6 catálogos + 14 gp_*.yaml sem poda)
│   ├── bin/                                 ├── src/ (core/, hooks/, rendering/, schemas/)
│   ├── extensions/                          ├── templates/ (dashboard_template.md)
│   ├── profiles/                            ├── integrations/antigravity/SKILL.md.template
│   ├── src/                                 ├── AGENTS.md
│   ├── templates/                           └── .venv/ (Ambiente virtual Python isolado)
│   └── integrations/
├── specs/           (especificações SDD)    Camada 3: .vitalia/memory/session/ (Git isolado)
└── tests/           (suíte P05)             Camada 4: .vitalia/memory/data_storage/ (Git isolado)
```

**Versão:** 0.0.1 | **Kit-Global path padrão:** `~/.vitalia-spec-kit/` (`VITALIA_KIT_DIR`)

