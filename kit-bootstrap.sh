#!/usr/bin/env bash
# kit-bootstrap.sh | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:55(GMT-04:00)
# Instalador universal da máquina do desenvolvedor para o Vitalia SPEC Kit.
# Referência: FR-001, FR-002, RN-001, RN-002, ADR-0001.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/source"
REQ_FILE="${SCRIPT_DIR}/requirements.txt"

DEFAULT_KIT_DIR="${HOME}/.vitalia-spec-kit"
TARGET_KIT_DIR="${VITALIA_KIT_DIR:-}"
NON_INTERACTIVE=0

usage() {
    cat << 'EOF'
Uso: ./kit-bootstrap.sh [OPÇÕES]

Opções:
  --target-dir <PATH>   Diretório de instalação do kit (padrão: ~/.vitalia-spec-kit)
  --non-interactive     Executa sem prompts interativos (usa valores padrão)
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

# ─────────────────────────────────────────────────────────────
# PASSO 1: Pré-validação de pré-requisitos ANTES de criar diretórios (RCA-02)
# ─────────────────────────────────────────────────────────────
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Erro: python3 (>= 3.10) não encontrado no PATH." >&2
    exit 1
fi

if ! command -v git >/dev/null 2>&1; then
    echo "❌ Erro: git não encontrado no PATH." >&2
    exit 1
fi

if [ ! -d "${SOURCE_DIR}" ]; then
    echo "❌ Erro: diretório source/ não encontrado em ${SOURCE_DIR}." >&2
    exit 1
fi

# Teste real de criação de venv em diretório temporário ANTES de tocar em TARGET_KIT_DIR
_TMP_VENV_CHECK="$(mktemp -d)"
if ! python3 -m venv "${_TMP_VENV_CHECK}/probe" >/dev/null 2>&1; then
    rm -rf "${_TMP_VENV_CHECK}"
    echo "❌ Erro: falha ao criar ambiente virtual com 'python3 -m venv'." >&2
    echo "   Em sistemas Ubuntu/Debian/WSL2, instale o pacote python3-venv:" >&2
    echo "   sudo apt update && sudo apt install -y python3-venv" >&2
    exit 1
fi
rm -rf "${_TMP_VENV_CHECK}"

# ─────────────────────────────────────────────────────────────
# PASSO 2: Cópia integral da topologia source/ para TARGET_KIT_DIR
# ─────────────────────────────────────────────────────────────
echo "📦 Instalando Vitalia SPEC Kit v0.0.1 em: ${TARGET_KIT_DIR}"
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

# ─────────────────────────────────────────────────────────────
# PASSO 3: Criação do .venv isolado e instalação de dependências
# ─────────────────────────────────────────────────────────────
VENV_DIR="${TARGET_KIT_DIR}/.venv"
if [ ! -x "${VENV_DIR}/bin/python3" ]; then
    python3 -m venv "${VENV_DIR}"
fi

# Tenta instalar via pip; se sem rede (sandbox/offline), recria com --system-site-packages
if [ -f "${REQ_FILE}" ]; then
    if ! "${VENV_DIR}/bin/pip" install --quiet --disable-pip-version-check -r "${REQ_FILE}" >/dev/null 2>&1; then
        rm -rf "${VENV_DIR}"
        python3 -m venv --system-site-packages "${VENV_DIR}"
    fi
fi

if ! "${VENV_DIR}/bin/python3" -c "import yaml, jinja2, jsonschema" >/dev/null 2>&1; then
    rm -rf "${VENV_DIR}"
    python3 -m venv --system-site-packages "${VENV_DIR}"
    if ! "${VENV_DIR}/bin/python3" -c "import yaml, jinja2, jsonschema" >/dev/null 2>&1; then
        echo "❌ Erro: dependências Python (pyyaml, jinja2, jsonschema) indisponíveis no .venv." >&2
        exit 1
    fi
fi

# ─────────────────────────────────────────────────────────────
# PASSO 4: Geração do shim executável ~/.local/bin/vitalia-install-project
# ─────────────────────────────────────────────────────────────
LOCAL_BIN_DIR="${HOME}/.local/bin"
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
# PASSO 5: Injeção idempotente em ~/.bashrc e ~/.zshrc
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

echo "✅ Vitalia SPEC Kit v0.0.1 instalado com sucesso em ${TARGET_KIT_DIR}"
echo "   Shim criado em: ${SHIM_FILE}"

