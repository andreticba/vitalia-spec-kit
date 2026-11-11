#!/usr/bin/env bash
# preflight.sh | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:50(GMT-04:00)
# Módulo modular de pré-validação de ambiente, runtime e permissões.

set -euo pipefail

# 1. Validação Semântica de Versão do Python
check_python_version_semver() {
    local min_major="${1:-3}"
    local min_minor="${2:-10}"

    if ! command -v python3 >/dev/null 2>&1; then
        echo "❌ Erro: python3 não encontrado no PATH." >&2
        echo "   O Vitalia SPEC Kit requer Python >= ${min_major}.${min_minor}." >&2
        return 1
    fi

    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (${min_major}, ${min_minor}) else 1)" >/dev/null 2>&1; then
        local current_ver
        current_ver=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || echo "desconhecida")
        echo "❌ Erro: Versão do Python incompatível (${current_ver})." >&2
        echo "   O Vitalia SPEC Kit requer Python >= ${min_major}.${min_minor}." >&2
        return 1
    fi

    return 0
}

# 2. Validação da Capacidade do Módulo venv
check_venv_capability() {
    local probe_dir
    probe_dir=$(mktemp -d /tmp/vitalia-probe-venv-XXXXXX 2>/dev/null || mktemp -d)

    if ! python3 -m venv "$probe_dir" >/dev/null 2>&1; then
        rm -rf "$probe_dir" 2>/dev/null || true
        echo "❌ Erro: O módulo 'venv' do Python não está funcional ou 'ensurepip' está ausente." >&2
        echo "   Para corrigir em sistemas baseados em Debian/Ubuntu, execute:" >&2
        echo "     sudo apt update && sudo apt install -y python3-venv" >&2
        return 1
    fi

    rm -rf "$probe_dir" 2>/dev/null || true
    return 0
}

# 3. Validação Preventiva de Permissão de Escrita com Probe Temporário
check_writable_target() {
    local target="$1"
    if [[ -z "$target" ]]; then
        echo "❌ Erro: Caminho de destino não especificado para teste de permissão de escrita." >&2
        return 1
    fi

    # Localiza o primeiro diretório ancestral existente
    local curr="$target"
    while [[ ! -d "$curr" ]]; do
        local parent
        parent=$(dirname "$curr")
        if [[ "$parent" == "$curr" ]]; then
            break
        fi
        curr="$parent"
    done

    # Realiza teste com probe temporário via mktemp no diretório existente
    local probe_file
    if ! probe_file=$(TMPDIR="$curr" mktemp "$curr/.vitalia-write-probe-XXXXXX" 2>/dev/null); then
        echo "❌ Erro: sem permissão de escrita no diretório alvo '$target' (ancestral '$curr' somente-leitura ou restrito)." >&2
        return 1
    fi

    rm -f "$probe_file" 2>/dev/null || true
    return 0
}

# 4. Validação dos Requisitos de Git
check_git_requirements() {
    if ! command -v git >/dev/null 2>&1; then
        echo "❌ Erro: git não encontrado no PATH. Instale o git para continuar." >&2
        return 1
    fi

    # Validação sintática preliminar de repositórios remotos se fornecidos
    local session_repo="${1:-}"
    local data_repo="${2:-}"

    for repo in "$session_repo" "$data_repo"; do
        if [[ -n "$repo" ]]; then
            # Rejeita strings que claramente não são caminhos ou URLs
            if [[ "$repo" =~ [[:space:]] ]]; then
                echo "❌ Erro: URL do repositório Git inválida (contém espaços): '$repo'" >&2
                return 1
            fi
        fi
    done

    return 0
}

