# test_skills_pure.py | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:58(GMT-04:00)
"""
Testes de integridade, pureza e elevação proativa de sandbox para skills (T001).
Cenário de Falsificação (P05): Falha se o Passo 1 do template ou de qualquer skill compilada
omitir a prescrição explícita de elevação proativa de sandbox (BypassSandbox: true) ou contiver
artefatos impuros no diretório de skills.
"""

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "source" / "integrations" / "antigravity" / "SKILL.md.template"
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"


def test_template_prescribes_proactive_sandbox_elevation():
    """
    FR-001.1: O Passo 1 de SKILL.md.template DEVE prescrever proativamente
    a execução com elevação de sandbox (BypassSandbox: true) para a IDE Antigravity.
    """
    assert TEMPLATE_PATH.exists(), f"Template não encontrado em: {TEMPLATE_PATH}"
    content = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Extrai o trecho do Passo 1 até o Passo 2
    match = re.search(r"1\.\s+Execute o script nativo.*?(?=2\.\s+O script ejetará)", content, re.DOTALL)
    assert match is not None, "Passo 1 não encontrado no template de SKILL.md"

    step_1_text = match.group(0)

    # O Passo 1 deve conter a instrução proativa de BypassSandbox: true
    assert "BypassSandbox: true" in step_1_text, (
        "Cenário de Falsificação atingido: Passo 1 do template omite a elevação proativa de sandbox (BypassSandbox: true)."
    )
    # Deve indicar execução inicial com elevação, e não meramente reexecução reativa
    assert any(term in step_1_text for term in ["proativo", "proativamente", "inicial", "fora da sandbox"]), (
        "Passo 1 do template deve prescrever execução inicial/proativa fora da sandbox."
    )


def test_compiled_skills_prescribe_proactive_sandbox_elevation():
    """
    FR-001.2: Todas as skills compiladas em .agents/skills/*/SKILL.md DEVEM
    prescrever a elevação proativa de sandbox no Passo 1.
    """
    assert SKILLS_DIR.exists(), f"Diretório de skills não encontrado: {SKILLS_DIR}"
    skill_files = list(SKILLS_DIR.glob("*/SKILL.md"))
    assert len(skill_files) > 0, "Nenhuma skill encontrada para validação"

    for skill_file in skill_files:
        content = skill_file.read_text(encoding="utf-8")
        match = re.search(r"1\.\s+Execute o script nativo.*?(?=2\.\s+O script ejetará)", content, re.DOTALL)
        assert match is not None, f"Passo 1 não encontrado em {skill_file}"

        step_1_text = match.group(0)
        assert "BypassSandbox: true" in step_1_text, (
            f"Cenário de Falsificação atingido: Passo 1 em {skill_file.parent.name} omite 'BypassSandbox: true'."
        )
        assert any(term in step_1_text for term in ["proativo", "proativamente", "inicial", "fora da sandbox"]), (
            f"Passo 1 em {skill_file.parent.name} omite prescrição de elevação inicial/proativa."
        )


def test_skills_directory_purity():
    """
    SC-002: O diretório .agents/skills/ deve conter exclusivamente pastas de skills válidas,
    sem lixo (.trash, backups, arquivos temporários).
    """
    assert SKILLS_DIR.exists()
    for item in SKILLS_DIR.iterdir():
        assert not item.name.startswith("."), f"Item oculto encontrado em skills: {item.name}"
        assert not item.name.endswith(".bak"), f"Arquivo de backup encontrado em skills: {item.name}"
        assert item.name != ".trash", "Diretório .trash encontrado em skills"
        assert item.is_dir(), f"Arquivo solto fora de pasta de skill: {item.name}"
        skill_md = item / "SKILL.md"
        assert skill_md.exists(), f"Pasta de skill {item.name} não contém SKILL.md"
