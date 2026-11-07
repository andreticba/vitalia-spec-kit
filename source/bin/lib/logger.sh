#!/usr/bin/env bash
# logger.sh | Vitalia SPEC Kit v0.0.1 | 06-11-2026 23:00(GMT-04:00)
# Biblioteca de logging padronizado com suporte ANSI, compatível com bash 3.2+ e set -euo pipefail.
# Referência: FR-006, FR-008, FR-009, NF-001, NF-002.

[ -n "${_VITALIA_LOGGER_LOADED:-}" ] && return 0
_VITALIA_LOGGER_LOADED=1

_VIT_RED='\033[0;31m'
_VIT_GREEN='\033[0;32m'
_VIT_YELLOW='\033[1;33m'
_VIT_CYAN='\033[0;36m'
_VIT_BOLD='\033[1m'
_VIT_NC='\033[0m'

_VITALIA_LOG_BUFFER=""

_vit_get_timestamp() {
    TZ='America/Manaus' date '+%d-%m-%Y %H:%M:%S(GMT-04:00)'
}

_vit_append_buffer() {
    local level="$1"
    shift
    local msg="$*"
    local ts
    ts="$(_vit_get_timestamp)"
    _VITALIA_LOG_BUFFER="${_VITALIA_LOG_BUFFER}[${ts}] [${level}] ${msg}\n"
}

log_ok() {
    _vit_append_buffer "OK" "$*"
    echo -e "${_VIT_GREEN}   ✅ $*${_VIT_NC}"
}

log_warn() {
    _vit_append_buffer "WARN" "$*"
    echo -e "${_VIT_YELLOW}   ⚠️  $*${_VIT_NC}"
}

log_error() {
    _vit_append_buffer "ERROR" "$*"
    echo -e "${_VIT_RED}   ❌ $*${_VIT_NC}" >&2
}

log_info() {
    _vit_append_buffer "INFO" "$*"
    echo -e "${_VIT_CYAN}   ℹ️  $*${_VIT_NC}"
}

log_step() {
    local step_num="${1:-}"
    local step_desc="${2:-}"
    _vit_append_buffer "STEP" "PASSO ${step_num} — ${step_desc}"
    echo -e "\n${_VIT_BOLD}${_VIT_CYAN}🔷 PASSO ${step_num} — ${step_desc}${_VIT_NC}"
}

write_install_log() {
    local target_path="${1:-}"
    if [ -z "${target_path}" ]; then
        return 1
    fi
    local dir
    dir="$(dirname "${target_path}")"
    mkdir -p "${dir}"
    printf "%b" "${_VITALIA_LOG_BUFFER}" > "${target_path}"
}
