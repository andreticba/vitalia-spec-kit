<!-- quickstart.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:10(GMT-04:00) -->
> **quickstart.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:10(GMT-04:00)**

# Guia de Validação Rápida (Quickstart) — Spec 002

* **Feature:** [specs/002-universal-bootstrap-runtime](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime)
* **Objetivo:** Fornecer os passos executáveis para verificar a conformidade dos cenários de aceite implementados.

---

## 1. Pré-Requisitos do Sistema
* Sistema operacional: Linux (Debian/Ubuntu/Fedora/Arch) ou macOS.
* Utilitários do sistema: `bash` (v4+), `git` (v2.30+), `python3` (v3.10+).
* Zero dependência de Docker, Redis ou daemons adicionais.

---

## 2. Cenário 1: Bootstrap Idempotente em Máquina Limpa ou Existente (SC-001)

### Passo 1: Execução do instalador universal
```bash
./kit-bootstrap.sh
```

### Comportamento Esperado:
- O script detecta ou cria o diretório de destino `~/.vitalia-spec-kit/`.
- Cria o interpretador isolado em `~/.vitalia-spec-kit/.venv/` com `requirements.txt`.
- Instala os shims executáveis em `~/.local/bin/`.
- Ao reexecutar `./kit-bootstrap.sh` uma segunda vez, valida o ambiente existente e conclui com código 0 (idempotência confirmada).

---

## 3. Cenário 2: Diagnóstico de Ambiente Desacoplado (SC-002)

### Passo 1: Execução do hook de diagnóstico
```bash
python3 source/src/hooks/scan_environment.py
```

### Comportamento Esperado:
- Saída JSON compatível com `contracts/scan-environment.schema.json`.
- Campo `"status"` reportando `"HEALTHY"` sem requisições de portas TCP `6379` ou `5432`.
- `"runtime_isolated_ok": true`.

---

## 4. Cenário 3: Context Lifting em Armazenamento Local Seguro (SC-003)

### Passo 1: Disparo de um comando via Hook Runner
```bash
python3 source/src/vitalia_hook_runner.py source/extensions/session-start.toml --phase before --args=""
```

### Comportamento Esperado:
- O arquivo gerado é depositado em:
  `.vitalia/memory/data_storage/context/session-start_<timestamp>_<machine_id>_<hash>.json`
- Nenhum arquivo é gravado no diretório global `/tmp/`.
- O comando `git status` no projeto não acusa arquivos pendentes de commit (pasta `.vitalia/memory` protegida por `.gitignore`).

---

## 5. Cenário 4: Geração do Dashboard no Repositório de Contexto (SC-006)

### Passo 1: Execução da consolidação
```bash
python3 source/src/vitalia_context_engine.py --action consolidate
```

### Comportamento Esperado:
- Geração de `.vitalia/memory/session/README.md` contendo shields e diagramas Mermaid nativos.
- Geração das visões puras `SESSION_STATE.md`, `LEARNINGS.md` e `DECISIONS.md`.
