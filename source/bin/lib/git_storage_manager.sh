#!/usr/bin/env bash
# git_storage_manager.sh | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:55(GMT-04:00)
# Gestão modular de repositórios Git de memória (session e data_storage) com suporte a clone remoto e fallback init.

[ -n "${_VITALIA_GIT_STORAGE_LOADED:-}" ] && return 0
_VITALIA_GIT_STORAGE_LOADED=1

_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v log_ok >/dev/null 2>&1 && [ -f "${_LIB_DIR}/logger.sh" ]; then
    # shellcheck source=/dev/null
    source "${_LIB_DIR}/logger.sh"
else
    log_ok()    { echo "   ✅ $*"; }
    log_warn()  { echo "   ⚠️  $*"; }
    log_error() { echo "   ❌ $*" >&2; }
fi

ensure_subdirectories() {
    local repo_path="${1:-}"
    local initial_subdirs="${2:-}"
    if [ -n "${initial_subdirs}" ]; then
        for sub in ${initial_subdirs}; do
            mkdir -p "${repo_path}/${sub}"
        done
    fi
}

setup_git_repo() {
    local repo_path="${1:-}"
    local remote_url="${2:-}"
    local commit_msg="${3:-init: storage}"
    local initial_subdirs="${4:-}"

    if [ -z "${repo_path}" ]; then
        log_error "setup_git_repo requer o caminho do repositório"
        return 1
    fi

    # Se já for repositório Git, apenas garante remote e subdiretórios
    if [ -d "${repo_path}/.git" ]; then
        ensure_subdirectories "${repo_path}" "${initial_subdirs}"
        if [ -n "${remote_url}" ]; then
            git -C "${repo_path}" remote set-url origin "${remote_url}" 2>/dev/null \
                || git -C "${repo_path}" remote add origin "${remote_url}" 2>/dev/null \
                || true
        fi
        return 0
    fi

    # Se remote_url foi fornecido e possui commits remotos (git ls-remote), clona com --depth=1 (RCA-04b / PRES-02)
    if [ -n "${remote_url}" ]; then
        local remote_refs=""
        remote_refs="$(git ls-remote "${remote_url}" 2>/dev/null || true)"
        if [ -n "${remote_refs}" ]; then
            rm -rf "${repo_path}"
            mkdir -p "$(dirname "${repo_path}")"
            if git clone --depth=1 "${remote_url}" "${repo_path}" >/dev/null 2>&1; then
                ensure_subdirectories "${repo_path}" "${initial_subdirs}"
                return 0
            fi
        fi
    fi

    # Fallback: Inicialização local (git init -b main)
    mkdir -p "${repo_path}"
    ensure_subdirectories "${repo_path}" "${initial_subdirs}"

    git -C "${repo_path}" init -b main >/dev/null 2>&1 || git -C "${repo_path}" init >/dev/null 2>&1 || true
    git -C "${repo_path}" config user.email "vitalia@local" 2>/dev/null || true
    git -C "${repo_path}" config user.name "Vitalia Kit" 2>/dev/null || true

    if [ -n "${remote_url}" ]; then
        git -C "${repo_path}" remote add origin "${remote_url}" 2>/dev/null || true
    fi

    touch "${repo_path}/.gitkeep"
    git -C "${repo_path}" add . >/dev/null 2>&1 || true
    git -C "${repo_path}" commit -m "${commit_msg}" >/dev/null 2>&1 || true

    if [ -n "${remote_url}" ]; then
        git -C "${repo_path}" push -u origin main >/dev/null 2>&1 || true
    fi

    return 0
}

setup_session_repo() {
    local memory_dir="${1:-}"
    local remote_url="${2:-}"

    local session_path="${memory_dir}/session"
    setup_git_repo "${session_path}" "${remote_url}" "init: session tracking" ""

    if [ -n "${remote_url}" ]; then
        log_ok "Sessão: ${remote_url}"
    else
        log_ok "Sessão: ${session_path} (local)"
    fi
}

setup_data_repo() {
    local memory_dir="${1:-}"
    local remote_url="${2:-}"

    local data_path="${memory_dir}/data_storage"
    setup_git_repo "${data_path}" "${remote_url}" "init: data storage" "reviews research specs handoffs context"

    if [ -n "${remote_url}" ]; then
        log_ok "Dados: ${remote_url}"
    else
        log_ok "Dados: ${data_path} (local)"
    fi
}
