#!/usr/bin/env bash
# kit-bootstrap.sh | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
# Instalador e inicializador universal idempotente do Vitalia SPEC Kit

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VITALIA_DIR="${HOME}/.vitalia-spec-kit"
VENV_DIR="${VITALIA_DIR}/.venv"
LOCAL_BIN="${HOME}/.local/bin"

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

# 2. Criação dos diretórios unificados
mkdir -p "${VITALIA_DIR}" "${LOCAL_BIN}"

# 3. Gerenciamento do Virtualenv Isolado (Idempotência)
if [ ! -x "${VENV_DIR}/bin/python3" ]; then
    echo "📦 Criando ambiente virtual Python isolado em ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
else
    echo "🔄 Ambiente virtual existente detectado em ${VENV_DIR}. Verificando integridade..."
fi

# 4. Instalação e atualização de dependências de runtime
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    echo "📦 Sincronizando dependências mínimas do runtime via pip..."
    "${VENV_DIR}/bin/pip" install --quiet --disable-pip-version-check -r "${SCRIPT_DIR}/requirements.txt"
fi

# 5. Sincronização dos componentes de source/ para o diretório global
echo "📦 Espelhando componentes canônicos para ${VITALIA_DIR}..."
mkdir -p "${VITALIA_DIR}/bin" "${VITALIA_DIR}/extensions" "${VITALIA_DIR}/profiles" "${VITALIA_DIR}/src"

if [ -d "${SCRIPT_DIR}/source/bin" ]; then
    cp -r "${SCRIPT_DIR}/source/bin/." "${VITALIA_DIR}/bin/"
fi
if [ -d "${SCRIPT_DIR}/source/extensions" ]; then
    cp -r "${SCRIPT_DIR}/source/extensions/." "${VITALIA_DIR}/extensions/"
fi
if [ -d "${SCRIPT_DIR}/source/profiles" ]; then
    cp -r "${SCRIPT_DIR}/source/profiles/." "${VITALIA_DIR}/profiles/"
fi
if [ -d "${SCRIPT_DIR}/source/src" ]; then
    cp -r "${SCRIPT_DIR}/source/src/." "${VITALIA_DIR}/src/"
fi

# Metadado de versão
echo "0.0.1" > "${VITALIA_DIR}/VERSION"

# Ajuste de permissões em bin
if [ -d "${VITALIA_DIR}/bin" ]; then
    chmod +x "${VITALIA_DIR}/bin/"* 2>/dev/null || true
fi

# 6. Geração idempotente de Shims em ~/.local/bin/
echo "⚙️ Configurando shims de execução em ${LOCAL_BIN}..."

cat << 'EOF' > "${LOCAL_BIN}/vitalia-install-project"
#!/usr/bin/env bash
# Shim universal gerado pelo Vitalia SPEC Kit
KIT_HOME="${HOME}/.vitalia-spec-kit"
export VITALIA_KIT_DIR="${KIT_HOME}"
export PATH="${KIT_HOME}/.venv/bin:${PATH}"
exec bash "${KIT_HOME}/bin/install-project" "$@"
EOF
chmod +x "${LOCAL_BIN}/vitalia-install-project"

echo "=========================================================="
echo "🎉 Vitalia SPEC Kit instalado e sincronizado com sucesso!"
echo "   Runtime isolado: ${VENV_DIR}"
echo "   Comandos disponíveis em: ${LOCAL_BIN}"
if [[ ":$PATH:" != *":${LOCAL_BIN}:"* ]]; then
    echo "⚠️  Aviso: Certifique-se de adicionar ${LOCAL_BIN} ao seu PATH (ex: export PATH=\"\$HOME/.local/bin:\$PATH\")"
fi
echo "=========================================================="
exit 0
