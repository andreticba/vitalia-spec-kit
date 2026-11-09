<!-- cli-contracts.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:50(GMT-04:00) -->
> **cli-contracts.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:50(GMT-04:00)**

# Contratos Públicos de CLI — Vitalia SPEC Kit v0.0.1 (`specs/002-universal-bootstrap-runtime`)

## 1. `./kit-bootstrap.sh` (Camada 1 $\rightarrow$ Camada 2)
- **Assinatura:** `./kit-bootstrap.sh [--target-dir <path>] [--non-interactive] [--help]`
- **Variáveis de Ambiente Suportadas:** `VITALIA_KIT_DIR`
- **Comportamento:**
  1. Se invocado com `--help`, imprime instruções didáticas e encerra com código `0`.
  2. Resolve `<target_dir>` via `--target-dir`, `VITALIA_KIT_DIR` ou prompt interativo (default `~/.vitalia-spec-kit`), expandindo `~` para `${HOME}`.
  3. Pré-valida `python3 -m venv` em diretório temporário **antes** de criar `<target_dir>`; em caso de falha, remove o diretório temporário, imprime instrução diagnóstica (`sudo apt install python3-venv`) no `stderr` e aborta com código `!= 0`.
  4. Copia integralmente `source/{bin,extensions,profiles,src,integrations,templates,AGENTS.md}` para `<target_dir>/` (sem o diretório `source/`), cria `<target_dir>/.venv`, instala `requirements.txt`, valida `import yaml, jinja2, jsonschema` e gera `~/.local/bin/vitalia-install-project`.

## 2. `vitalia-install-project` / `source/bin/install-project` (Camada 2 $\rightarrow$ Projeto Hospedeiro)
- **Assinatura:** `install-project [<project_dir>] [--session-repo <url>] [--data-repo <url>] [--non-interactive] [--help]`
- **Comportamento:**
  1. Preserva customizações existentes do usuário em `.vitalia/backups/` (jamais dentro de `.agents/skills/`).
  2. Configura `.vitalia/memory/session/` e `.vitalia/memory/data_storage/` via `git_storage_manager.sh` (`git ls-remote` $\rightarrow$ `git clone --depth=1` se URL remota tiver commits, ou `git init -b main` se vazio/local).
  3. Gera `.agents/AGENTS.md` e `.agents/skills/vitalia-<workflow>/SKILL.md` para todas as 16 extensões canônicas com `{{VITALIA_KIT_DIR}}` resolvido.
  4. Atualiza `.env` e `.gitignore` do projeto hospedeiro.

## 3. `vitalia_hook_runner.py` (Runtime de Context Lifting — §11)
- **Assinatura:** `python3 vitalia_hook_runner.py <path_to_toml> --phase <before|after> [--args="<user_args>"] [--help]`
- **Saída (`stdout`):** Stub JSON contendo:
  - `status`: `"ready"`
  - `workflow`: `<workflow_name>`
  - `workflow_context_file`: `<project_root>/.vitalia/memory/data_storage/context/<machine_id>/<workflow>_<ts>_<hash>.json`
  - `action_required`: instrução para leitura via `view_file`.
- **Invariantes:** Código de saída `0` sem Redis; zero escrita em `tmp/` do kit; 100% dos 16 workflows sem poda (`token_budget: 0`, `18/18` princípios `P00`–`P17`).

## 4. `vitalia_context_engine.py` (Motor de Sessão 3-Tier)
- **Assinatura:** `python3 vitalia_context_engine.py --action <init|end|consolidate> [--session-dir <path>] [--summary <text>] [--p0-next <text>] [--decisions-json <json>] [--learnings-json <json>] [--help]`
- **Invariantes:**
  - `init`: garante estrutura `{data,shards,state}` em `.vitalia/memory/session/`.
  - `end`: grava entradas em `data/{decisions,learnings,session_history}.jsonl` com timestamp `DD-MM-YYYY HH:MM:SS(GMT-04:00)`, atualiza `shards/<machine_id>.yaml` e executa `consolidate`.
  - `consolidate`: carrega shards ordenados por `last_sync` decrescente (`shards[0]` = máquina mais recente) e renderiza `README.md` (via `dashboard_template.md`), `SESSION_STATE.md`, `DECISIONS.md`, `LEARNINGS.md` e `SESSION_HISTORY.md`.

## 5. `vitalia_handoff.py` (Handoff Inter-Agente Determinístico)
- **Assinatura:** `python3 vitalia_handoff.py <create|pending|consume> [options] [--help]`
- **Invariantes:** Resolve `<project_root>` via `resolve_project_root()`, valida contra `vitalia-handoff-v1.0.0.json` (OpenAPI 3.0 limpo) e grava/consome atomicamente em `<project_root>/.vitalia/memory/data_storage/handoffs/`.

