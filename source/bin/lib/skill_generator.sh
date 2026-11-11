#!/usr/bin/env bash
# skill_generator.sh | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:24(GMT-04:00)
# Geração e higienização estrita de .agents/skills/vitalia-*/SKILL.md mantendo pureza 100% do diretório do cliente.
# Referência: FR-003, PRES-03/BUG-03, RCA-04a.

[ -n "${_VITALIA_SKILL_GENERATOR_LOADED:-}" ] && return 0
_VITALIA_SKILL_GENERATOR_LOADED=1

_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v log_ok >/dev/null 2>&1 && [ -f "${_LIB_DIR}/logger.sh" ]; then
    # shellcheck source=/dev/null
    source "${_LIB_DIR}/logger.sh"
fi
if ! command -v update_skill >/dev/null 2>&1 && [ -f "${_LIB_DIR}/agent_preserver.sh" ]; then
    # shellcheck source=/dev/null
    source "${_LIB_DIR}/agent_preserver.sh"
fi

sanitize_and_generate_skills() {
    local extensions_dir="${1:-}"
    local skills_dir="${2:-}"
    local template_file="${3:-}"
    local version="${4:-0.0.1}"
    local kit_dir="${5:-}"
    local vitalia_dir="${6:-}"

    if [ ! -d "${extensions_dir}" ] || [ ! -f "${template_file}" ]; then
        log_error "sanitize_and_generate_skills: diretório de extensões ou template ausente"
        return 1
    fi

    if [ -z "${vitalia_dir}" ]; then
        vitalia_dir="$(dirname "$(dirname "${skills_dir}")")/.vitalia"
    fi

    local backups_dir="${vitalia_dir}/memory/data_storage/backups/skills"
    mkdir -p "${skills_dir}" "${backups_dir}"

    local ts
    ts="$(date +%Y%m%d%H%M%S)"

    # 1. Purgar quaisquer entradas ocultas legadas (.trash, .vitalia-manifest) de dentro de .agents/skills/
    for hidden_item in "${skills_dir}"/.*; do
        local base_hidden
        base_hidden="$(basename "${hidden_item}")"
        if [ "${base_hidden}" = "." ] || [ "${base_hidden}" = ".." ]; then
            continue
        fi
        if [ -e "${hidden_item}" ]; then
            mv "${hidden_item}" "${backups_dir}/${base_hidden}.${ts}" 2>/dev/null || rm -rf "${hidden_item}"
        fi
    done

    # 2. Expurgar pastas com prefixo duplicado (vitalia-vitalia-*) para .vitalia/backups/skills/
    for dup_dir in "${skills_dir}"/vitalia-vitalia-*; do
        if [ -d "${dup_dir}" ]; then
            local dup_name
            dup_name="$(basename "${dup_dir}")"
            log_warn "Movendo skill duplicada para .vitalia/backups/skills/: ${dup_name}"
            mv "${dup_dir}" "${backups_dir}/${dup_name}.${ts}"
        fi
    done

    # 3. Mover skills vitalia-* órfãs/descontinuadas para .vitalia/backups/skills/
    for existing_skill_dir in "${skills_dir}"/vitalia-*; do
        if [ -d "${existing_skill_dir}" ]; then
            local skill_folder_name
            skill_folder_name="$(basename "${existing_skill_dir}")"
            local skill_base="${skill_folder_name#vitalia-}"
            if [ ! -f "${extensions_dir}/${skill_base}.toml" ]; then
                log_warn "Movendo skill descontinuada para .vitalia/backups/skills/: ${skill_folder_name}"
                mv "${existing_skill_dir}" "${backups_dir}/${skill_folder_name}.${ts}"
            fi
        fi
    done

    # 4. Gerar as skills ativas a partir de extensions/*.toml com normalização idempotente
    for toml_file in "${extensions_dir}"/*.toml; do
        [ -f "${toml_file}" ] || continue
        local raw_ext_name
        raw_ext_name="$(basename "${toml_file}" .toml)"
        local base_name="${raw_ext_name#vitalia-}"

        local desc
        desc="$(grep -E '^[[:space:]]*description[[:space:]]*=' "${toml_file}" | head -n 1 | sed -E 's/^[[:space:]]*description[[:space:]]*=[[:space:]]*["'"'"']?//; s/["'"'"'][[:space:]]*$//')"
        [ -z "${desc}" ] && desc="Workflow ${base_name} do Vitalia SPEC Kit."

        local kit_python="${kit_dir}/.venv/bin/python3"
        [ ! -f "${kit_python}" ] && kit_python="python3"

        local rendered
        rendered="$(sed \
            -e "s|{{NAME}}|${base_name}|g" \
            -e "s|{{DESCRIPTION}}|${desc}|g" \
            -e "s|{{VERSION}}|${version}|g" \
            -e "s|{{KIT_PYTHON}}|${kit_python}|g" \
            -e "s|{{VITALIA_KIT_DIR}}|${kit_dir}|g" \
            "${template_file}")"

        update_skill "vitalia-${base_name}" "${rendered}" "${skills_dir}" "${vitalia_dir}"
    done

    return 0
}

