#!/usr/bin/env bash
# env_manager.sh | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:55(GMT-04:00)
# Biblioteca de gestão idempotente e segura de variáveis em .env (Matriz S1–S7), sem Redis.

[ -n "${_VITALIA_ENV_MANAGER_LOADED:-}" ] && return 0
_VITALIA_ENV_MANAGER_LOADED=1

if ! command -v log_ok >/dev/null 2>&1; then
    _LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "${_LIB_DIR}/logger.sh" ]; then
        # shellcheck source=/dev/null
        source "${_LIB_DIR}/logger.sh"
    else
        log_ok()    { echo "   ✅ $*"; }
        log_warn()  { echo "   ⚠️  $*"; }
        log_error() { echo "   ❌ $*" >&2; }
        log_step()  { echo -e "\n🔷 PASSO $1 — $2"; }
    fi
fi

mask_credential() {
    local val="${1:-}"
    if [ -z "$val" ]; then
        echo ""
        return 0
    fi
    if echo "$val" | grep -E '://[^:]+:[^@]+@' >/dev/null 2>&1; then
        echo "$val" | sed -E 's/(:\/\/[^:]+:)[^@]+(@)/\1****\2/'
        return 0
    fi
    local len="${#val}"
    if [ "$len" -gt 12 ]; then
        local prefix="${val:0:4}"
        local suffix="${val: -4}"
        echo "${prefix}****${suffix}"
        return 0
    fi
    echo "$val"
}

has_env_var() {
    local var_name="${1:-}"
    local env_file="${2:-}"
    [ -f "${env_file}" ] || return 1
    grep -E '^[[:space:]]*(export[[:space:]]+)?'"${var_name}"'[[:space:]]*=' "${env_file}" >/dev/null 2>&1
}

get_env_var() {
    local var_name="${1:-}"
    local env_file="${2:-}"
    [ -f "${env_file}" ] || return 1
    sed -n -E 's/^[[:space:]]*(export[[:space:]]+)?'"${var_name}"'[[:space:]]*=[[:space:]]*//p' "${env_file}" \
        | head -n 1 \
        | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"
}

ensure_env_file() {
    local env_file="${1:-}"
    local template_content="${2:-}"

    local dir_path
    dir_path="$(dirname "${env_file}")"

    if [ -f "${env_file}" ] && [ ! -w "${env_file}" ]; then
        log_warn "[ALERTA] configure manualmente: sem permissão de escrita em ${env_file}"
        return 1
    fi
    if [ ! -f "${env_file}" ] && [ ! -w "${dir_path}" ]; then
        log_warn "[ALERTA] configure manualmente: sem permissão de criação em ${dir_path}"
        return 1
    fi

    if [ ! -f "${env_file}" ]; then
        if [ -n "${template_content}" ]; then
            printf "%s\n" "${template_content}" > "${env_file}"
        else
            cat << 'EOF' > "${env_file}"
# .env | Vitalia SPEC Kit v0.0.1
VITALIA_ENVIRONMENT=development
EOF
        fi
        log_ok "[CRIADO] ${env_file} inicializado a partir do template"
        return 0
    fi

    local bak_file="${env_file}.bak"
    if [ -e "${bak_file}" ]; then
        log_ok "[BACKUP] preservado (${bak_file} histórico mantido)"
    else
        cp "${env_file}" "${bak_file}"
        log_ok "[BACKUP] criado (${bak_file})"
    fi
    return 0
}

ensure_env_var() {
    local var_name="${1:-}"
    local default_val="${2:-}"
    local env_file="${3:-}"
    local comment="${4:-}"

    if [ -f "${env_file}" ] && [ ! -w "${env_file}" ]; then
        log_warn "[ALERTA] configure manualmente: sem permissão de escrita em ${env_file}"
        return 1
    fi

    if has_env_var "${var_name}" "${env_file}"; then
        local current_val
        current_val="$(get_env_var "${var_name}" "${env_file}")"
        local masked_val
        masked_val="$(mask_credential "${current_val}")"

        if [ "${current_val}" = "${default_val}" ]; then
            log_ok "[PRESERVADA] ${var_name} (valor padrão: ${masked_val})"
        else
            log_ok "[PRESERVADA] valor customizado: ${var_name}=${masked_val}"
        fi
    else
        local masked_default
        masked_default="$(mask_credential "${default_val}")"
        if [ -n "${comment}" ]; then
            printf "\n# %s\n" "${comment}" >> "${env_file}"
        fi
        printf "%s=%s\n" "${var_name}" "${default_val}" >> "${env_file}"
        log_ok "[ADICIONADA] ${var_name}=${masked_default}"
    fi
    return 0
}

manage_kit_env() {
    local env_file="${1:-}"
    local kit_dir_val="${2:-}"
    local session_repo_val="${3:-}"
    local data_repo_val="${4:-}"

    if [ -z "${env_file}" ]; then
        log_error "manage_kit_env requer o caminho do arquivo .env"
        return 1
    fi

    ensure_env_file "${env_file}" || return 1

    ensure_env_var "VITALIA_ENVIRONMENT" "development" "${env_file}" "Ambiente de execução do Vitalia SPEC Kit"

    if [ -n "${session_repo_val}" ]; then
        ensure_env_var "SESSION_REPO" "${session_repo_val}" "${env_file}" "Repositório Git de memória de sessão"
    fi

    if [ -n "${data_repo_val}" ]; then
        ensure_env_var "DATA_REPO" "${data_repo_val}" "${env_file}" "Repositório Git de dados e artefatos"
    fi

    return 0
}
