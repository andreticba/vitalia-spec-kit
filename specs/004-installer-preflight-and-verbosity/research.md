<!-- research.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:30(GMT-04:00) -->
> **research.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:30(GMT-04:00)**

# Technical Research: Spec 004 — Installer Preflight and Verbosity

---

## 1. Decisão: Validação Semântica de Versão do Python sem Ferramentas Externas

- **Escolhido**: Inspeção determinística via one-liner Python:
  ```bash
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
  ```
- **Verificado em**: https://docs.python.org/3/library/sys.html#sys.version_info em 10-11-2026
- **Justificativa**: `sys.version_info` é nativo do interpretador Python desde o Python 2.0 e retorna uma tupla comparável `(major, minor)`. Elimina dependência de comandos externos como `cut`, `awk`, `sed` ou `sort -V`, funcionando igualmente em Linux, macOS, Alpine, Debian e WSL2/zsh.
- **Alternativas**:
  - `python3 --version | cut -d' ' -f2 | awk ...`: rejeitado porque a formatação da string de versão varia entre distribuições e quebra em flags de compilação ou versões de desenvolvimento.
  - Expressão regular em Bash (`[[ $ver =~ ... ]]`): rejeitada por não realizar comparação aritmética correta de versões menores (ex: 3.9 vs 3.10 vs 3.14).

---

## 2. Decisão: Validação de Permissão de Escrita em Diretórios Inexistentes

- **Escolhido**: Resolução recursiva do primeiro ancestral existente e teste de criação/remoção de arquivo probe via `mktemp`:
  ```bash
  check_writable_target() {
      local target="$1"
      local cur="$target"
      while [ ! -d "$cur" ]; do
          cur="$(dirname "$cur")"
      done
      local probe
      if ! probe="$(mktemp "${cur}/.vitalia_probe_XXXXXX" 2>/dev/null)"; then
          return 1
      fi
      rm -f "${probe}"
      return 0
  }
  ```
- **Verificado em**: https://man7.org/linux/man-pages/man1/mktemp.1.html em 10-11-2026
- **Justificativa**: Testa diretamente a operação real do kernel no sistema de arquivos. Funciona confiavelmente sob montagens `ro` (read-only), sandboxes de segurança restritas e flags de usuário, sem criar as pastas finais de destino prematuramente caso o pre-flight aborte.
- **Alternativas**:
  - `[ -w "$dir" ]`: rejeitado porque testa apenas bits de permissão estáticos POSIX, falhando silenciosamente se o filesystem estiver montado como read-only ou sob sandboxes com namespaces isolados.
  - `mkdir -p "$dir"` no preflight: rejeitado porque deixa diretórios órfãos parciais em caso de falha posterior nas etapas seguintes.

---

## 3. Decisão: Isolamento de Logs Temporários sem Colisão Multi-Usuário

- **Escolhido**: Log com sufixo do UID do usuário corrente:
  ```bash
  LOG_FILE="/tmp/vitalia-bootstrap-${UID:-$(id -u)}.log"
  # Fallback se houver colisão de permissão
  if [ -e "${LOG_FILE}" ] && [ ! -w "${LOG_FILE}" ]; then
      LOG_FILE="$(mktemp /tmp/vitalia-bootstrap-XXXXXX.log)"
  fi
  ```
- **Verificado em**: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html em 10-11-2026
- **Justificativa**: Em sistemas compartilhados com `/tmp` sob sticky bit (`1777`), o arquivo criado pelo usuário A não pode ser modificado nem sobrescrito pelo usuário B. O uso do UID isola a sessão de cada desenvolvedor e o fallback `mktemp` garante que o instalador nunca aborte por permissão negada no log.
- **Alternativas**:
  - `/tmp/vitalia-bootstrap.log` fixo: rejeitado por falha inevitável de `Permission Denied` em servidores multi-usuário.
  - Log gravado diretamente em `${TARGET_KIT_DIR}`: rejeitado porque, se o erro ocorrer durante a validação ou criação da pasta do kit, o log não poderia ser gravado.

---

## 4. Decisão: Purga Incondicional de `--system-site-packages`

- **Escolhido**: Remoção completa de `--system-site-packages` do instalador `kit-bootstrap.sh`. Em caso de falha no `pip`, exibir as últimas 15 linhas do log e abortar com código de saída 1:
  ```bash
  if ! "${VENV_DIR}/bin/pip" install --quiet --disable-pip-version-check -r "${REQ_FILE}" >> "${LOG_FILE}" 2>&1; then
      echo "❌ Erro: falha ao instalar dependências no .venv isolado." >&2
      tail -n 15 "${LOG_FILE}" >&2
      echo "   Consulte o log completo em: ${LOG_FILE}" >&2
      exit 1
  fi
  ```
- **Verificado em**: https://docs.python.org/3/library/venv.html em 10-11-2026
- **Justificativa**: O kit v0.0.1 depende de contratos estritos de `pyyaml`, `jinja2`, `jsonschema` e `pytest`. O fallback anterior para bibliotecas do sistema criava um "teatro de sucesso", permitindo que o instalador terminasse com código 0 enquanto comandos subsequentes falhavam por dependências ausentes no sistema global.
- **Alternativas**:
  - Manter fallback para `--system-site-packages`: rejeitado por decisão explícita do usuário no Brainstorming e violação do princípio P11 (Runtime Autonomy).

---

## 5. Decisão: Detecção Dinâmica de Shell para o Banner Pós-Instalação

- **Escolhido**: Detecção em 3 camadas (`$ZSH_VERSION`, `$BASH_VERSION`, basename de `$SHELL`):
  ```bash
  detect_user_shell() {
      if [ -n "${ZSH_VERSION:-}" ] || [[ "${SHELL:-}" =~ zsh$ ]]; then
          echo "zsh"
      else
          echo "bash"
      fi
  }
  ```
- **Verificado em**: https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html em 10-11-2026
- **Justificativa**: Zsh é o padrão no macOS e muito popular em WSL2; Bash é o padrão no Ubuntu/Debian. Identificar o shell ativo permite emitir o comando de reload cirúrgico (`source ~/.zshrc` ou `source ~/.bashrc`), reduzindo atrito de onboarding.

