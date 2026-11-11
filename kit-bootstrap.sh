#!/usr/bin/env bash
# kit-bootstrap.sh | Vitalia SPEC Kit v0.0.1 | 10-11-2026 20:03(GMT-04:00)
# Instalador universal da máquina do desenvolvedor para o Vitalia SPEC Kit.
# Referência: FR-001, FR-002, FR-003, FR-004, SC-001..SC-004, ADR-0003.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/source"
REQ_FILE="${SCRIPT_DIR}/requirements.txt"
PREFLIGHT_LIB="${SOURCE_DIR}/bin/lib/preflight.sh"

DEFAULT_KIT_DIR="${HOME}/.vitalia-spec-kit"
TARGET_KIT_DIR="${VITALIA_KIT_DIR:-}"
NON_INTERACTIVE=0
VERBOSE=0

usage() {
    cat << 'EOF'
Uso: ./kit-bootstrap.sh [OPÇÕES]

Opções:
  --target-dir <PATH>   Diretório de instalação do kit (padrão: ~/.vitalia-spec-kit)
  --non-interactive     Executa sem prompts interativos (usa valores padrão)
  -v, --verbose         Habilita streaming direto de stdout/stderr de comandos externos
  -h, --help            Exibe esta mensagem de ajuda
EOF
}

expand_tilde() {
    local input_path="${1:-}"
    case "${input_path}" in
        "~")
            printf "%s\n" "${HOME}"
            ;;
        "~/"*)
            printf "%s/%s\n" "${HOME}" "${input_path#\~/}"
            ;;
        *)
            printf "%s\n" "${input_path}"
            ;;
    esac
}

while [ $# -gt 0 ]; do
    case "$1" in
        --target-dir)
            if [ -z "${2:-}" ]; then
                echo "❌ Erro: --target-dir requer um caminho." >&2
                exit 1
            fi
            TARGET_KIT_DIR="$2"
            shift 2
            ;;
        --target-dir=*)
            TARGET_KIT_DIR="${1#*=}"
            shift
            ;;
        --non-interactive)
            NON_INTERACTIVE=1
            shift
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "❌ Opção desconhecida: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if [ -z "${TARGET_KIT_DIR}" ]; then
    if [ "${NON_INTERACTIVE}" -eq 0 ] && [ -t 0 ]; then
        read -r -p "📂 Onde deseja instalar o Vitalia SPEC Kit? [${DEFAULT_KIT_DIR}]: " user_input || true
        TARGET_KIT_DIR="${user_input:-${DEFAULT_KIT_DIR}}"
    else
        TARGET_KIT_DIR="${DEFAULT_KIT_DIR}"
    fi
fi

TARGET_KIT_DIR="$(expand_tilde "${TARGET_KIT_DIR}")"
LOCAL_BIN_DIR="${HOME}/.local/bin"

# ─────────────────────────────────────────────────────────────
# PASSO 0: Pre-Flight Check Preventivo (FR-001)
# ─────────────────────────────────────────────────────────────
if [ ! -f "${PREFLIGHT_LIB}" ]; then
    echo "❌ Erro interno: biblioteca de pre-flight não encontrada em ${PREFLIGHT_LIB}." >&2
    exit 1
fi

# Carrega biblioteca modular de pre-flight
# shellcheck source=source/bin/lib/preflight.sh
source "${PREFLIGHT_LIB}"

echo "⏳ Executando verificações de ambiente e pré-requisitos (Pre-Flight Check)..."

# 1. Validação Semântica de Versão do Python (>= 3.10)
check_python_version_semver 3 10

# 2. Validação da Capacidade do Módulo venv
check_venv_capability

# 3. Validação Preventiva de Permissão de Escrita antes de criar pastas
check_writable_target "${TARGET_KIT_DIR}"
check_writable_target "${LOCAL_BIN_DIR}"

# 4. Validação de Git e Source
check_git_requirements

if [ ! -d "${SOURCE_DIR}" ]; then
    echo "❌ Erro: diretório source/ não encontrado em ${SOURCE_DIR}." >&2
    exit 1
fi

echo "✅ Pré-requisitos e permissões de escrita validados com sucesso."

# ─────────────────────────────────────────────────────────────
# Configuração de Log Isolado por UID (FR-003, ADR-0003)
# ─────────────────────────────────────────────────────────────
USER_UID="${UID:-$(id -u 2>/dev/null || echo 1000)}"
BOOTSTRAP_LOG="/tmp/vitalia-bootstrap-${USER_UID}.log"
if ! touch "${BOOTSTRAP_LOG}" 2>/dev/null; then
    BOOTSTRAP_LOG="$(mktemp /tmp/vitalia-bootstrap-XXXXXX.log 2>/dev/null || mktemp)"
fi
: > "${BOOTSTRAP_LOG}"

# ─────────────────────────────────────────────────────────────
# PASSO 1: Cópia integral da topologia source/ para TARGET_KIT_DIR
# ─────────────────────────────────────────────────────────────
echo "⏳ Instalando topologia Vitalia SPEC Kit em: ${TARGET_KIT_DIR}..."
mkdir -p "${TARGET_KIT_DIR}"

for subdir in bin extensions profiles src integrations templates; do
    if [ -d "${SOURCE_DIR}/${subdir}" ]; then
        rm -rf "${TARGET_KIT_DIR}/${subdir}"
        cp -R "${SOURCE_DIR}/${subdir}" "${TARGET_KIT_DIR}/${subdir}"
    fi
done

if [ -f "${SOURCE_DIR}/AGENTS.md" ]; then
    cp "${SOURCE_DIR}/AGENTS.md" "${TARGET_KIT_DIR}/AGENTS.md"
fi

if [ -f "${REQ_FILE}" ]; then
    cp "${REQ_FILE}" "${TARGET_KIT_DIR}/requirements.txt"
fi

echo "0.0.1" > "${TARGET_KIT_DIR}/VERSION"
chmod +x "${TARGET_KIT_DIR}/bin/install-project" 2>/dev/null || true
echo "✅ Topologia de arquivos instalada com sucesso."

# ─────────────────────────────────────────────────────────────
# PASSO 2: Criação do .venv isolado e instalação de dependências
# (Purga absoluta de --system-site-packages - FR-002, P11)
# ─────────────────────────────────────────────────────────────
VENV_DIR="${TARGET_KIT_DIR}/.venv"
echo "⏳ Provisionando ambiente virtual isolado em: ${VENV_DIR}..."

if [ ! -x "${VENV_DIR}/bin/python3" ]; then
    python3 -m venv "${VENV_DIR}" >> "${BOOTSTRAP_LOG}" 2>&1
fi

echo "⏳ Instalando dependências Python (pyyaml, jinja2, jsonschema)..."
if [ -f "${REQ_FILE}" ]; then
    set +e
    if [ "${VERBOSE}" -eq 1 ]; then
        "${VENV_DIR}/bin/pip" install --disable-pip-version-check -r "${REQ_FILE}" 2>&1 | tee -a "${BOOTSTRAP_LOG}"
        PIP_STATUS="${PIPESTATUS[0]}"
    else
        "${VENV_DIR}/bin/pip" install --disable-pip-version-check -r "${REQ_FILE}" >> "${BOOTSTRAP_LOG}" 2>&1
        PIP_STATUS=$?
    fi
    set -e

    if [ "${PIP_STATUS}" -ne 0 ]; then
        echo "❌ Erro: Falha ao instalar dependências via pip." >&2
        echo "   Log completo disponível em: ${BOOTSTRAP_LOG}" >&2
        echo "   Últimas linhas do erro:" >&2
        tail -n 15 "${BOOTSTRAP_LOG}" >&2 || true
        exit 1
    fi
fi

if ! "${VENV_DIR}/bin/python3" -c "import yaml, jinja2, jsonschema" >> "${BOOTSTRAP_LOG}" 2>&1; then
    echo "❌ Erro: dependências Python (pyyaml, jinja2, jsonschema) indisponíveis no .venv isolado." >&2
    echo "   Log completo em: ${BOOTSTRAP_LOG}" >&2
    exit 1
fi
echo "✅ Ambiente virtual e dependências configurados com sucesso."

# ─────────────────────────────────────────────────────────────
# PASSO 3: Geração do shim executável ~/.local/bin/vitalia-install-project
# ─────────────────────────────────────────────────────────────
mkdir -p "${LOCAL_BIN_DIR}"
SHIM_FILE="${LOCAL_BIN_DIR}/vitalia-install-project"

cat << EOF > "${SHIM_FILE}"
#!/usr/bin/env bash
# vitalia-install-project | Vitalia SPEC Kit v0.0.1
export VITALIA_KIT_DIR="\${VITALIA_KIT_DIR:-${TARGET_KIT_DIR}}"
exec "\${VITALIA_KIT_DIR}/bin/install-project" "\$@"
EOF
chmod +x "${SHIM_FILE}"

# ─────────────────────────────────────────────────────────────
# PASSO 4: Injeção idempotente em ~/.bashrc e ~/.zshrc (FR-004)
# ─────────────────────────────────────────────────────────────
inject_shell_rc() {
    local rc_file="${1:-}"
    [ -f "${rc_file}" ] || return 0

    local tmp_rc
    tmp_rc="$(mktemp)"
    grep -v -E 'VITALIA_KIT_DIR|vitalia-spec-kit/bin|\.local/bin.*vitalia' "${rc_file}" > "${tmp_rc}" 2>/dev/null || true
    {
        echo "# Vitalia SPEC Kit v0.0.1"
        echo "export VITALIA_KIT_DIR=\"${TARGET_KIT_DIR}\""
        echo "export PATH=\"\${HOME}/.local/bin:\${VITALIA_KIT_DIR}/bin:\${PATH}\""
    } >> "${tmp_rc}"
    mv "${tmp_rc}" "${rc_file}"
}

inject_shell_rc "${HOME}/.bashrc"
inject_shell_rc "${HOME}/.zshrc"

# ─────────────────────────────────────────────────────────────
# PASSO 5: Banner de Sucesso com Detecção Dinâmica de Shell (FR-004)
# ─────────────────────────────────────────────────────────────
ACTIVE_SHELL="bash"
if [ -n "${ZSH_VERSION:-}" ] || [[ "${SHELL:-}" == *"zsh"* ]]; then
    ACTIVE_SHELL="zsh"
fi

echo ""
echo "==================================================================="
echo "🎉 Vitalia SPEC Kit v0.0.1 instalado com sucesso!"
echo "   Destino: ${TARGET_KIT_DIR}"
echo "   Shim:    ${SHIM_FILE}"
echo ""
echo "👉 Para ativar os comandos nesta sessão do seu terminal, execute:"
echo "   source ~/.${ACTIVE_SHELL}rc"
echo ""
echo "   Ou, se estiver usando outro shell:"
if [ "${ACTIVE_SHELL}" = "zsh" ]; then
    echo "   source ~/.bashrc"
else
    echo "   source ~/.zshrc"
fi
echo "==================================================================="
