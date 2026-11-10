#!/usr/bin/env bash
# agent_preserver.sh | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:56(GMT-04:00)
# Preservação não-destrutiva de AGENTS.md e SKILL.md via marcadores e manifesto SHA-256 fora de .agents/skills/.
# Referência: FR-003, PRES-03/BUG-03, RCA-04a.

[ -n "${_VITALIA_AGENT_PRESERVER_LOADED:-}" ] && return 0
_VITALIA_AGENT_PRESERVER_LOADED=1

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

START_MARKER="<!-- VITALIA:KIT:START -->"
END_MARKER="<!-- VITALIA:KIT:END -->"

update_agents_md() {
    local target_file="${1:-}"
    local kit_content="${2:-}"
    local backups_dir="${3:-}"

    if [ -z "${target_file}" ] || [ -z "${kit_content}" ]; then
        log_error "update_agents_md requer caminho do arquivo e conteúdo do Kit"
        return 1
    fi

    local target_dir
    target_dir="$(dirname "${target_file}")"
    mkdir -p "${target_dir}"

    if [ -z "${backups_dir}" ]; then
        backups_dir="$(dirname "${target_dir}")/.vitalia/memory/data_storage/backups"
    fi
    mkdir -p "${backups_dir}"

    local ts
    ts="$(date +%Y%m%d%H%M%S)"

    if [ ! -f "${target_file}" ]; then
        cat << EOF > "${target_file}"
${START_MARKER}
${kit_content}
${END_MARKER}
EOF
        log_ok "[CRIADO] AGENTS.md inicializado com marcadores do Kit"
        return 0
    fi

    if grep -qF "${START_MARKER}" "${target_file}" && grep -qF "${END_MARKER}" "${target_file}"; then
        local tmp_file
        tmp_file="$(mktemp)"

        sed -n "1,/${START_MARKER}/p" "${target_file}" | grep -vF "${START_MARKER}" > "${tmp_file}" || true
        echo "${START_MARKER}" >> "${tmp_file}"
        printf "%s\n" "${kit_content}" >> "${tmp_file}"
        echo "${END_MARKER}" >> "${tmp_file}"
        sed -n "/${END_MARKER}/,\$p" "${target_file}" | grep -vF "${END_MARKER}" >> "${tmp_file}" || true

        mv "${tmp_file}" "${target_file}"
        log_ok "[ATUALIZADO] AGENTS.md: bloco do Kit atualizado entre marcadores; regras customizadas preservadas"
        return 0
    fi

    if grep -q "AGENTS.md —" "${target_file}"; then
        local bak_file="${backups_dir}/AGENTS.md.bak.${ts}"
        cp "${target_file}" "${bak_file}"
        cat << EOF > "${target_file}"
${START_MARKER}
${kit_content}
${END_MARKER}
EOF
        log_ok "[MIGRADO] AGENTS.md legado migrado para marcadores (backup em .vitalia/backups/)"
        return 0
    fi

    local bak_file="${backups_dir}/AGENTS.md.bak.${ts}"
    cp "${target_file}" "${bak_file}"
    local tmp_file
    tmp_file="$(mktemp)"

    cat << EOF > "${tmp_file}"
${START_MARKER}
${kit_content}
${END_MARKER}

EOF
    cat "${target_file}" >> "${tmp_file}"
    mv "${tmp_file}" "${target_file}"
    log_ok "[PRESERVADO] Conteúdo customizado preservado abaixo do bloco do Kit"
    return 0
}

compute_skill_hash() {
    local file="${1:-}"
    if [ ! -f "${file}" ]; then
        echo ""
        return 1
    fi
    sha256sum "${file}" | awk '{print $1}'
}

get_manifest_hash() {
    local rel_path="${1:-}"
    local manifest_file="${2:-}"
    [ -f "${manifest_file}" ] || return 0
    (grep -E "[[:space:]]+${rel_path}\$" "${manifest_file}" 2>/dev/null || true) | awk '{print $1}' | head -n 1
}

set_manifest_hash() {
    local rel_path="${1:-}"
    local new_hash="${2:-}"
    local manifest_file="${3:-}"

    mkdir -p "$(dirname "${manifest_file}")"
    touch "${manifest_file}"
    local tmp_m
    tmp_m="$(mktemp)"

    grep -v -E "[[:space:]]+${rel_path}\$" "${manifest_file}" > "${tmp_m}" 2>/dev/null || true
    printf "%s  %s\n" "${new_hash}" "${rel_path}" >> "${tmp_m}"
    mv "${tmp_m}" "${manifest_file}"
}

update_skill() {
    local skill_name="${1:-}"
    local skill_content="${2:-}"
    local skills_dir="${3:-}"
    local vitalia_dir="${4:-}"

    if [ -z "${vitalia_dir}" ]; then
        vitalia_dir="$(dirname "$(dirname "${skills_dir}")")/.vitalia"
    fi

    local skill_folder="${skills_dir}/${skill_name}"
    local target_file="${skill_folder}/SKILL.md"
    local rel_path="${skill_name}/SKILL.md"
    local manifest_file="${vitalia_dir}/memory/data_storage/manifests/.vitalia-manifest"
    local backups_dir="${vitalia_dir}/memory/data_storage/backups/skills"

    mkdir -p "${skill_folder}" "${backups_dir}"
    local ts
    ts="$(date +%Y%m%d%H%M%S)"

    if [ ! -f "${target_file}" ]; then
        printf "%s\n" "${skill_content}" > "${target_file}"
        local new_hash
        new_hash="$(compute_skill_hash "${target_file}")"
        set_manifest_hash "${rel_path}" "${new_hash}" "${manifest_file}"
        log_ok "[CRIADA] ${rel_path}"
        return 0
    fi

    local current_hash
    current_hash="$(compute_skill_hash "${target_file}")"
    local manifest_hash
    manifest_hash="$(get_manifest_hash "${rel_path}" "${manifest_file}")"

    if [ -n "${manifest_hash}" ]; then
        if [ "${current_hash}" = "${manifest_hash}" ]; then
            printf "%s\n" "${skill_content}" > "${target_file}"
            local new_hash
            new_hash="$(compute_skill_hash "${target_file}")"
            set_manifest_hash "${rel_path}" "${new_hash}" "${manifest_file}"
            log_ok "[ATUALIZADA] ${rel_path} (silenciosa)"
            return 0
        else
            local bak_file="${backups_dir}/${skill_name}_SKILL.md.bak.${ts}"
            cp "${target_file}" "${bak_file}"
            log_warn "[BACKUP] Edição do usuário detectada em ${rel_path} -> backup em .vitalia/backups/skills/"
            printf "%s\n" "${skill_content}" > "${target_file}"
            local new_hash
            new_hash="$(compute_skill_hash "${target_file}")"
            set_manifest_hash "${rel_path}" "${new_hash}" "${manifest_file}"
            log_ok "[ATUALIZADA] ${rel_path} atualizada após backup de segurança"
            return 0
        fi
    fi

    local tmp_new
    tmp_new="$(mktemp)"
    printf "%s\n" "${skill_content}" > "${tmp_new}"

    if cmp -s "${target_file}" "${tmp_new}"; then
        rm -f "${tmp_new}"
        set_manifest_hash "${rel_path}" "${current_hash}" "${manifest_file}"
        log_ok "[MANIFESTO] ${rel_path} registrada no manifesto"
        return 0
    else
        rm -f "${tmp_new}"
        local bak_file="${backups_dir}/${skill_name}_SKILL.md.bak.${ts}"
        cp "${target_file}" "${bak_file}"
        log_warn "[BACKUP] Skill legada com alterações em ${rel_path} -> backup em .vitalia/backups/skills/"
        printf "%s\n" "${skill_content}" > "${target_file}"
        local new_hash
        new_hash="$(compute_skill_hash "${target_file}")"
        set_manifest_hash "${rel_path}" "${new_hash}" "${manifest_file}"
        log_ok "[ATUALIZADA] ${rel_path} migrada para manifesto após backup"
        return 0
    fi
}
