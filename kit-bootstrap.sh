#!/usr/bin/env bash
# kit-bootstrap.sh | Vitalia SPEC Kit v0.0.1 | 06-11-2026 23:00(GMT-04:00)
# Instalador e inicializador universal idempotente do Vitalia SPEC Kit
# Referências: FR-001, FR-002, FR-003, FR-004, SC-001, SC-007

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_BIN="${LOCAL_BIN:-${HOME}/.local/bin}"

echo "=========================================================="
echo "  Vitalia SPEC Kit v0.0.1 — Universal Bootstrap & Runtime"
echo "  Fuso Horário Canônico: America/Cuiaba (GMT-04:00)"
echo "=========================================================="

# 1. Validação de pré-requisitos do sistema host
if ! command -v python3 &>/dev/null; then
    echo "❌ Erro: python3 não encontrado no PATH do sistema." >&2
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Erro: Python 3.10 ou superior é obrigatório. Versão encontrada: ${PYTHON_VERSION}" >&2
    exit 1
fi

echo "✅ Python host compatível: v${PYTHON_VERSION}"

# 2. Definição interativa do diretório de instalação do Kit (FR-001)
DEFAULT_KIT_DIR="${HOME}/.vitalia-spec-kit"
if [ -n "${VITALIA_KIT_DIR:-}" ]; then
    TARGET_KIT_DIR="${VITALIA_KIT_DIR}"
elif [ -t 0 ]; then
    echo ""
    read -r -p "Diretório de instalação do Kit [Padrão: ~/.vitalia-spec-kit]: " USER_INPUT_DIR || true
    TARGET_KIT_DIR="${USER_INPUT_DIR:-$DEFAULT_KIT_DIR}"
else
    TARGET_KIT_DIR="$DEFAULT_KIT_DIR"
fi

# Expansão do til (~)
TARGET_KIT_DIR="${TARGET_KIT_DIR/#\~/$HOME}"
mkdir -p "${TARGET_KIT_DIR}" "${LOCAL_BIN}"
TARGET_KIT_DIR="$(cd "${TARGET_KIT_DIR}" && pwd)"

VENV_DIR="${TARGET_KIT_DIR}/.venv"

echo "📂 Diretório do Kit: ${TARGET_KIT_DIR}"

# 3. Gerenciamento do Virtualenv Isolado (Idempotência)
if [ ! -x "${VENV_DIR}/bin/python3" ]; then
    echo "📦 Criando ambiente virtual Python isolado em ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
else
    echo "🔄 Ambiente virtual existente detectado em ${VENV_DIR}."
fi

# 4. Instalação e atualização de dependências de runtime
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    echo "📦 Sincronizando dependências mínimas do runtime via pip..."
    "${VENV_DIR}/bin/pip" install --quiet --disable-pip-version-check -r "${SCRIPT_DIR}/requirements.txt"
fi

# 5. Sincronização átomo a átomo de componentes autorizados (FR-002, FR-003)
echo "📦 Espelhando componentes autorizados para ${TARGET_KIT_DIR}..."
mkdir -p "${TARGET_KIT_DIR}/bin/lib" \
         "${TARGET_KIT_DIR}/extensions" \
         "${TARGET_KIT_DIR}/profiles" \
         "${TARGET_KIT_DIR}/src/hooks" \
         "${TARGET_KIT_DIR}/templates" \
         "${TARGET_KIT_DIR}/integrations/antigravity"

# bin/ e bin/lib/ (estritamente sem redis_detector.sh)
if [ -f "${SCRIPT_DIR}/source/bin/install-project" ]; then
    cp "${SCRIPT_DIR}/source/bin/install-project" "${TARGET_KIT_DIR}/bin/"
fi

for lib in logger.sh env_manager.sh agent_preserver.sh git_storage_manager.sh; do
    if [ -f "${SCRIPT_DIR}/source/bin/lib/${lib}" ]; then
        cp "${SCRIPT_DIR}/source/bin/lib/${lib}" "${TARGET_KIT_DIR}/bin/lib/"
    fi
done

# extensions/ (.toml)
if [ -d "${SCRIPT_DIR}/source/extensions" ]; then
    for ext in "${SCRIPT_DIR}"/source/extensions/*.toml; do
        [ -f "${ext}" ] && cp "${ext}" "${TARGET_KIT_DIR}/extensions/"
    done
fi

# profiles/ (estritamente sem gp_*.yaml)
if [ -d "${SCRIPT_DIR}/source/profiles" ]; then
    for prof in grounding_domains.yaml dynamic_questioning.yaml brainstorming_intents.yaml; do
        if [ -f "${SCRIPT_DIR}/source/profiles/${prof}" ]; then
            cp "${SCRIPT_DIR}/source/profiles/${prof}" "${TARGET_KIT_DIR}/profiles/"
        fi
    done
fi

# src/ e src/hooks/
if [ -d "${SCRIPT_DIR}/source/src" ]; then
    for src_file in kit_env_bootstrap.py vitalia_context_engine.py vitalia_hook_runner.py vitalia_handoff.py; do
        if [ -f "${SCRIPT_DIR}/source/src/${src_file}" ]; then
            cp "${SCRIPT_DIR}/source/src/${src_file}" "${TARGET_KIT_DIR}/src/"
        fi
    done
fi

if [ -d "${SCRIPT_DIR}/source/src/hooks" ]; then
    for hook_file in guardian_context.py scan_environment.py; do
        if [ -f "${SCRIPT_DIR}/source/src/hooks/${hook_file}" ]; then
            cp "${SCRIPT_DIR}/source/src/hooks/${hook_file}" "${TARGET_KIT_DIR}/src/hooks/"
        fi
    done
fi

# templates/
if [ -f "${SCRIPT_DIR}/source/templates/dashboard_template.md" ]; then
    cp "${SCRIPT_DIR}/source/templates/dashboard_template.md" "${TARGET_KIT_DIR}/templates/"
fi

# integrations/
if [ -f "${SCRIPT_DIR}/source/integrations/antigravity/SKILL.md.template" ]; then
    cp "${SCRIPT_DIR}/source/integrations/antigravity/SKILL.md.template" "${TARGET_KIT_DIR}/integrations/antigravity/"
fi

# AGENTS.md
if [ -f "${SCRIPT_DIR}/source/AGENTS.md" ]; then
    cp "${SCRIPT_DIR}/source/AGENTS.md" "${TARGET_KIT_DIR}/"
fi

# Metadado de versão
echo "0.0.1" > "${TARGET_KIT_DIR}/VERSION"

# Ajuste de permissões de execução
chmod +x "${TARGET_KIT_DIR}/bin/install-project" 2>/dev/null || true
chmod +x "${TARGET_KIT_DIR}/bin/lib/"*.sh 2>/dev/null || true

# 6. Geração de Shims parametrizados (FR-004)
echo "⚙️ Configurando shim de execução em ${LOCAL_BIN}/vitalia-install-project..."

cat << EOF > "${LOCAL_BIN}/vitalia-install-project"
#!/usr/bin/env bash
# Shim universal gerado pelo Vitalia SPEC Kit
export VITALIA_KIT_DIR="${TARGET_KIT_DIR}"
export PATH="\${VITALIA_KIT_DIR}/.venv/bin:\${PATH}"
exec bash "\${VITALIA_KIT_DIR}/bin/install-project" "\$@"
EOF
chmod +x "${LOCAL_BIN}/vitalia-install-project"

echo "=========================================================="
echo "🎉 Vitalia SPEC Kit instalado e sincronizado com sucesso!"
echo "   Kit instalado em: ${TARGET_KIT_DIR}"
echo "   Runtime isolado: ${VENV_DIR}"
echo "   Shim configurado: ${LOCAL_BIN}/vitalia-install-project"
if [[ ":$PATH:" != *":${LOCAL_BIN}:"* ]]; then
    echo "⚠️  Aviso: Certifique-se de adicionar ${LOCAL_BIN} ao seu PATH (ex: export PATH=\"\$HOME/.local/bin:\$PATH\")"
fi
echo "=========================================================="
exit 0
