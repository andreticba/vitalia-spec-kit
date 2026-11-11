<!-- quickstart.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:30(GMT-04:00) -->
> **quickstart.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:30(GMT-04:00)**

# Quickstart de Validação: Spec 004 — Pre-Flight & Verbosidade

---

## 1. Teste de Pre-Flight em Diretório Somente-Leitura (Falha Precoce)

1. Simular diretório sem permissão de escrita e executar bootstrap:
   ```bash
   TMP_RO="$(mktemp -d)"
   chmod 555 "${TMP_RO}"
   ./kit-bootstrap.sh --target-dir "${TMP_RO}/kit" --non-interactive
   ```
2. **Esperado**:
   - Código de retorno `1`.
   - Mensagem clara no terminal: `❌ Erro: sem permissão de escrita no caminho alvo: ...`.
   - Nenhuma pasta criada dentro de `${TMP_RO}`.
   - Limpeza: `chmod 755 "${TMP_RO}" && rm -rf "${TMP_RO}"`.

---

## 2. Teste de Instalação Normal com Observabilidade e Log Estruturado

1. Executar bootstrap em destino isolado:
   ```bash
   TMP_HOME="$(mktemp -d)"
   HOME="${TMP_HOME}" ./kit-bootstrap.sh --target-dir "${TMP_HOME}/.vitalia-custom" --non-interactive
   ```
2. **Esperado**:
   - Status visual exibido para cada macro-etapa (`⏳`, `✅`).
   - Log completo gravado em `/tmp/vitalia-bootstrap-${UID}.log`.
   - Ausência completa de `--system-site-packages` no `.venv` criado.
   - Banner final exibindo o comando de reload correspondente ao shell ativo (`source ~/.bashrc` ou `source ~/.zshrc`).
   - Shim funcional em `${TMP_HOME}/.local/bin/vitalia-install-project --help` retornando código `0`.

