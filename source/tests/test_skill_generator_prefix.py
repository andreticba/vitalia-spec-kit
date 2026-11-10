# test_skill_generator_prefix.py | Vitalia SDD v0.6.0 | 10-11-2026 16:45(GMT-04:00)
import subprocess
from pathlib import Path
import pytest

generator_script = Path(__file__).resolve().parent.parent / "bin" / "lib" / "skill_generator.sh"


def test_skill_generator_normalizes_prefixed_extension_idempotently(tmp_path):
    """
    [TEST:BUGFIX] Cenário de Falsificação:
    Falha se skill_generator.sh gerar diretório anômalo duplicado 'vitalia-vitalia-*'
    quando um arquivo TOML já possuir o prefixo 'vitalia-' no nome (ex: vitalia-route.toml).
    """
    assert generator_script.exists(), f"{generator_script} deve existir"

    ext_dir = tmp_path / "extensions"
    ext_dir.mkdir()
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    vitalia_dir = tmp_path / ".vitalia"
    vitalia_dir.mkdir()

    # Criar template básico
    template_file = tmp_path / "skill_template.md"
    template_file.write_text("---\nname: {{NAME}}\ndescription: {{DESCRIPTION}}\n---\n# {{NAME}}\n", encoding="utf-8")

    # Criar arquivo TOML com prefixo vitalia- pré-existente
    (ext_dir / "vitalia-route.toml").write_text('description = "Roteamento inteligente"\n', encoding="utf-8")

    cmd = f"""
    source "{generator_script}"
    sanitize_and_generate_skills "{ext_dir}" "{skills_dir}" "{template_file}" "0.0.1" "/fake/kit" "{vitalia_dir}"
    """

    res = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
    assert res.returncode == 0, f"Falha na execução: {res.stderr}"

    # Asserção de falsificação: NÃO DEVE existir vitalia-vitalia-route
    duplicated_dir = skills_dir / "vitalia-vitalia-route"
    assert not duplicated_dir.exists(), f"Diretório duplicado anômalo encontrado: {duplicated_dir}"

    # DEVE existir estritamente vitalia-route
    canonical_dir = skills_dir / "vitalia-route"
    assert canonical_dir.exists(), f"Diretório canônico {canonical_dir} não foi gerado"

