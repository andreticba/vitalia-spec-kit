<!-- quickstart.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:50(GMT-04:00) -->
> **quickstart.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:50(GMT-04:00)**

# Quickstart: Universal Bootstrap, Runtime Autônomo em 4 Camadas & Blindagem SDD (`specs/002-universal-bootstrap-runtime`)

## Pré-requisitos
- Sistema operacional Linux ou **WSL2** (`zsh` ou `bash`).
- `git` e `python3` com módulo `venv` (`python3-venv` instalado).
- **Zero containers necessários** (nenhum Redis, PostgreSQL ou Docker em execução).

---

## Cenário 1: Bootstrap Completo em Estação Limpa (`US-001`)
1. Clonar o repositório do kit e executar o instalador universal apontando para `~/.vitalia-spec-kit` (ou caminho isolado de teste):
   ```bash
   ./kit-bootstrap.sh --target-dir "$HOME/.vitalia-spec-kit" --non-interactive
   ```
2. Verificar o interpretador isolado e as 14 lentes sem poda:
   ```bash
   "$HOME/.vitalia-spec-kit/.venv/bin/python3" -c "import yaml, jinja2, jsonschema; print('OK')"
   ls -1 "$HOME/.vitalia-spec-kit/extensions/"*.toml | wc -l
   ls -1 "$HOME/.vitalia-spec-kit/profiles/gp_"*.yaml | wc -l
   ```
**Esperado**: Impressão de `OK`, `16` extensões `.toml` e `14` perfis `gp_*.yaml` instalados em `$HOME/.vitalia-spec-kit/`.

---

## Cenário 2: Ativação de Projeto Novo e Pureza de `.agents/skills/` (`US-002`)
1. Criar um diretório de projeto novo e ativar o kit:
   ```bash
   mkdir -p /tmp/meu-projeto-sdd && cd /tmp/meu-projeto-sdd && git init -b main
   "$HOME/.vitalia-spec-kit/bin/install-project" /tmp/meu-projeto-sdd --non-interactive
   ```
2. Inspecionar `.agents/skills/` e `.vitalia/memory/`:
   ```bash
   find /tmp/meu-projeto-sdd/.agents/skills -maxdepth 1 -name ".*"
   ls -d /tmp/meu-projeto-sdd/.agents/skills/vitalia-* | wc -l
   ```
**Esperado**: Nenhum arquivo/diretório oculto (`.trash` ou `.vitalia-manifest`) dentro de `.agents/skills/`, `16` skills geradas e repositórios Git inicializados em `.vitalia/memory/session/` e `.vitalia/memory/data_storage/`.

---

## Cenário 3: Context Lifting Isolado e 100% dos Workflows Sem Poda (`US-003`)
1. Executar o `vitalia_hook_runner.py` em um projeto ativado:
   ```bash
   cd /tmp/meu-projeto-sdd
   "$HOME/.vitalia-spec-kit/.venv/bin/python3" "$HOME/.vitalia-spec-kit/src/vitalia_hook_runner.py" \
     "$HOME/.vitalia-spec-kit/extensions/session-start.toml" --phase before --args=""
   ```
**Esperado**: Código de saída `0`, zero erros de Redis no `stderr`, arquivo JSON criado em `/tmp/meu-projeto-sdd/.vitalia/memory/data_storage/context/<machine_id>/session-start_*.json` contendo `token_budget: 0` e todos os `18` princípios (`P00`–`P17`) em `guardian_json.sources.constitution.principles`.

---

## Cenário 4: Consolidação 3-Tier e Ordenação Cronológica de Shards (`US-004`)
1. Executar a consolidação do motor de contexto:
   ```bash
   "$HOME/.vitalia-spec-kit/.venv/bin/python3" "$HOME/.vitalia-spec-kit/src/vitalia_context_engine.py" \
     --action consolidate --session-dir /tmp/meu-projeto-sdd/.vitalia/memory/session
   ```
**Esperado**: Geração de `README.md` rico (com grafo Mermaid entre aspas duplas, tabela HTML de máquinas e blocos `<details>`) e `SESSION_STATE.md` destacando sempre o shard com o timestamp `last_sync` (`DD-MM-YYYY HH:MM:SS(GMT-04:00)`) mais recente.

---

## Cenário 5: Execução da Suíte Comportamental P05 (`US-005`)
1. Na raiz do repositório `vitalia-spec-kit`, executar a suíte `pytest`:
   ```bash
   pytest -v tests/
   ```
**Esperado**: `100%` dos testes (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`) aprovados em subprocessos isolados.

