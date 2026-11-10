# test_sensor_purity.py | Vitalia SDD v0.6.0 | 10-11-2026 16:15(GMT-04:00)
import subprocess
import sys
from pathlib import Path
import pytest

sensors_dir = Path(__file__).resolve().parent.parent / "src" / "sensors"
purity_script = sensors_dir / "sensor_purity.py"


def test_sensor_purity_catches_impure_skills_directory(tmp_path):
    """
    [TEST:NEW] Cenário de Falsificação:
    Falha se o sensor retornar 0 quando o diretório .agents/skills/
    contiver arquivos soltos, pastas ocultas (.trash) ou SKILL.md malformado.
    """
    assert purity_script.exists(), f"Sensor {purity_script} deve existir"

    skills_dir = tmp_path / ".agents" / "skills"
    skills_dir.mkdir(parents=True)

    # 1. Caso Válido: pasta com SKILL.md contendo frontmatter válido
    valid_skill = skills_dir / "vitalia-demo"
    valid_skill.mkdir()
    (valid_skill / "SKILL.md").write_text("---\nname: vitalia-demo\ndescription: Demo skill\n---\n# Content\n", encoding="utf-8")

    res_valid = subprocess.run(
        [sys.executable, str(purity_script), "--target-dir", str(skills_dir)],
        capture_output=True,
        text=True,
    )
    assert res_valid.returncode == 0, f"Deveria passar com estrutura limpa: {res_valid.stderr}"

    # 2. Injeção de Anomalia 1: Arquivo solto na raiz de skills
    loose_file = skills_dir / "loose_manifest.txt"
    loose_file.write_text("corrupted", encoding="utf-8")

    res_loose = subprocess.run(
        [sys.executable, str(purity_script), "--target-dir", str(skills_dir)],
        capture_output=True,
        text=True,
    )
    assert res_loose.returncode != 0, "Sensor deve falhar ao detectar arquivo solto"
    assert "solto" in res_loose.stdout.lower() or "loose" in res_loose.stdout.lower()

    # Remover anomalia 1 e injetar Anomalia 2: Pasta oculta .trash
    loose_file.unlink()
    trash_dir = skills_dir / ".trash"
    trash_dir.mkdir()

    res_trash = subprocess.run(
        [sys.executable, str(purity_script), "--target-dir", str(skills_dir)],
        capture_output=True,
        text=True,
    )
    assert res_trash.returncode != 0, "Sensor deve falhar ao detectar pasta oculta .trash"

