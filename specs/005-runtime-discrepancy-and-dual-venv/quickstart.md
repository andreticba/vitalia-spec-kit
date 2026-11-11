<!-- quickstart.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 09:59(GMT-04:00) -->
> **quickstart.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 09:59(GMT-04:00)**

# Quickstart de Validação: Spec 005 — Dual-Runtime e Inviolabilidade do Runner

---

## 1. Teste de Inviolabilidade do Hook Runner sob PATH Hostil (SC-001)

1. Criar um mock defeituoso de `python3` e pré-pender no `$PATH`:
   ```bash
   TMP_DIR="$(mktemp -d)"
   cat << 'EOF' > "${TMP_DIR}/python3"
   #!/usr/bin/env bash
   echo "MOCK HOSTIL INTERCEPTADO! NÃO DEVERIA SER EXECUTADO" >&2
   exit 127
   EOF
   chmod +x "${TMP_DIR}/python3"
   ```
2. Executar o hook runner utilizando o interpretador do kit:
   ```bash
   PATH="${TMP_DIR}:${PATH}" /home/andre/.vitalia-spec-kit/.venv/bin/python3 \
     /home/andre/.vitalia-spec-kit/src/vitalia_hook_runner.py \
     /home/andre/.vitalia-spec-kit/extensions/session-start.toml --phase before --args=""
   ```
3. **Esperado**:
   - Código de retorno `0`.
   - Saída JSON no stdout contendo status `ready`.
   - Nenhuma emissão da mensagem `"MOCK HOSTIL INTERCEPTADO!"` no stderr (provando que o runner usou `sys.executable`).
   - Limpeza: `rm -rf "${TMP_DIR}"`.

---

## 2. Teste de Descoberta de Ambiente Virtual Customizado (SC-002)

1. Criar um projeto temporário com virtualenv em caminho não-padronizado e configurar `.env`:
   ```bash
   PROJ_DIR="$(mktemp -d)"
   python3 -m venv "${PROJ_DIR}/custom_env"
   echo "PROJECT_VENV_PATH=./custom_env" > "${PROJ_DIR}/.env"
   ```
2. Executar diagnóstico de ambiente a partir do interpretador do kit:
   ```bash
   /home/andre/.vitalia-spec-kit/.venv/bin/python3 -c "
   import sys
   from pathlib import Path
   sys.path.insert(0, '/home/andre/.vitalia-spec-kit/src')
   import kit_env_bootstrap
   health = kit_env_bootstrap.check_environment_health(Path('${PROJ_DIR}'))
   assert health['project_runtime']['has_venv'] == True
   assert 'custom_env' in health['project_runtime']['python_bin']
   print('✅ Descoberta customizada validada!')
   "
   ```
3. **Esperado**:
   - `health['project_runtime']['has_venv']` é `True`.
   - `python_bin` aponta exatamente para o executável dentro de `custom_env`.
   - Limpeza: `rm -rf "${PROJ_DIR}"`.

---

## 3. Linter de Pureza Contratual nos 16 Workflows (SC-003)

1. Verificar que nenhum arquivo `.toml` contém a chamada legada desprotegida:
   ```bash
   grep -rn "python3 {{VITALIA_KIT_DIR}}" /home/andre/.vitalia-spec-kit/extensions/*.toml
   ```
2. **Esperado**:
   - Zero ocorrências encontradas (exit code `1` no `grep`).
   - Todos os hooks `before` declaram `{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/...`.

