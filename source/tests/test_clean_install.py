# test_clean_install.py | Vitalia SDD v0.6.0 | 10-11-2026 16:50(GMT-04:00)
import os
import subprocess
from pathlib import Path
import pytest

script_path = Path(__file__).resolve().parent.parent / "bin" / "install-project"


def test_clean_install_in_isolated_project(tmp_path):
    """
    [TEST:NEW] Cenário de Falsificação:
    Falha se install-project em modo não-interativo não inicializar
    a estrutura pura da Camada 4 ou falhar em ambiente limpo sem prompts.
    """
    assert script_path.exists(), f"{script_path} deve existir"

    target_proj = tmp_path / "clean_workspace"
    target_proj.mkdir()

    env = os.environ.copy()
    env["VITALIA_KIT_DIR"] = str(Path(__file__).resolve().parent.parent)

    res = subprocess.run(
        [str(script_path), "--non-interactive"],
        cwd=str(target_proj),
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Instalação limpa falhou: {res.stderr}\nSaída: {res.stdout}"

    vitalia_dir = target_proj / ".vitalia"
    assert vitalia_dir.exists(), ".vitalia deve ser criado"
    assert (vitalia_dir / "feature.json").exists(), "feature.json deve ser criado"
    assert (vitalia_dir / "memory" / "data_storage").exists(), "data_storage deve existir na Camada 4"
    assert not (vitalia_dir / ".vitalia-manifest").exists(), "Manifesto não deve residir na raiz de .vitalia/"
