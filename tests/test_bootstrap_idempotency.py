# test_bootstrap_idempotency.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import os
import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_SCRIPT = REPO_ROOT / "kit-bootstrap.sh"

def test_repeated_bootstrap_runs_idempotently(tmp_path):
    """
    Executa kit-bootstrap.sh duas vezes consecutivas sobre o mesmo HOME simulado
    e valida que ambas retornam código 0 mantendo o ambiente íntegro.
    """
    custom_home = tmp_path / "home_user"
    custom_home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(custom_home)

    # 1ª Execução (Instalação Limpa)
    res1 = subprocess.run(
        ["bash", str(BOOTSTRAP_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert res1.returncode == 0, f"1ª Execução falhou: {res1.stderr}"

    vitalia_dir = custom_home / ".vitalia-spec-kit"
    shim = custom_home / ".local" / "bin" / "vitalia-install-project"
    assert vitalia_dir.exists()
    assert shim.exists()

    # Cria arquivo customizado do usuário em ~/.vitalia-spec-kit/custom_marker.txt
    user_marker = vitalia_dir / "user_marker.txt"
    user_marker.write_text("dados_preservados_do_usuario")

    # 2ª Execução (Reinstalação / Atualização)
    res2 = subprocess.run(
        ["bash", str(BOOTSTRAP_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert res2.returncode == 0, f"2ª Execução falhou: {res2.stderr}"

    # Valida preservação não-destrutiva
    assert user_marker.exists()
    assert user_marker.read_text() == "dados_preservados_do_usuario"
    assert shim.exists()
    assert os.access(shim, os.X_OK)

def test_bootstrap_repairs_missing_shim(tmp_path):
    """
    Simula cenário de reparo: o shim em ~/.local/bin/ foi excluído pelo usuário,
    e a re-execução do bootstrap restaura o shim mantendo o runtime já existente.
    """
    custom_home = tmp_path / "home_repair"
    custom_home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(custom_home)

    # Execução inicial
    res1 = subprocess.run(
        ["bash", str(BOOTSTRAP_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert res1.returncode == 0

    shim = custom_home / ".local" / "bin" / "vitalia-install-project"
    assert shim.exists()

    # Exclusão intencional do shim
    shim.unlink()
    assert not shim.exists()

    # Execução de reparo
    res2 = subprocess.run(
        ["bash", str(BOOTSTRAP_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert res2.returncode == 0
    assert shim.exists(), "Bootstrap deve restaurar shims faltantes"
    assert os.access(shim, os.X_OK)
