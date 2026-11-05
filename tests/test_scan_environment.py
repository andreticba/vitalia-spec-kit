# test_scan_environment.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import os
import sys
import json
import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_SCRIPT = REPO_ROOT / "source" / "src" / "hooks" / "scan_environment.py"
CONTRACT_SCHEMA = REPO_ROOT / "specs" / "002-universal-bootstrap-runtime" / "contracts" / "scan-environment.schema.json"

def test_scan_environment_script_exists():
    """Valida se o script scan_environment.py existe na topologia source/."""
    assert HOOK_SCRIPT.exists(), "source/src/hooks/scan_environment.py deve existir"

def test_scan_environment_conforms_to_schema(tmp_path):
    """Executa scan_environment em diretório temporário e valida estritamente o contrato."""
    # Simula projeto com .env
    test_project = tmp_path / "my_project"
    test_project.mkdir()
    (test_project / ".env").write_text("APP_ENV=testing\n")
    (test_project / ".git").mkdir()

    # Executa o script passando --cwd
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT), "--cwd", str(test_project)],
        cwd=str(test_project),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"Script falhou: {result.stderr}"

    data = json.loads(result.stdout)
    assert "status" in data
    assert "project_root" in data
    assert "has_env" in data
    assert "runtime_isolated_ok" in data
    assert "issues" in data

    assert data["status"] in ["HEALTHY", "DEGRADED", "CRITICAL"]
    assert data["has_env"] is True
    assert isinstance(data["issues"], list)
    assert isinstance(data["runtime_isolated_ok"], bool)

def test_scan_environment_purged_tcp_probes(tmp_path):
    """Garante que scan_environment não tenta se conectar a portas TCP 6379 (Redis) nem 5432 (Postgres)."""
    content = HOOK_SCRIPT.read_text(encoding="utf-8")
    assert "6379" not in content, "Porta 6379 (Redis) deve ser purgada de scan_environment"
    assert "5432" not in content, "Porta 5432 (Postgres) deve ser purgada de scan_environment"
    assert "redis.from_url" not in content, "Chamadas a cliente redis devem ser purgadas"
    assert "socket.socket" not in content, "Sondagens de socket TCP devem ser purgadas de scan_environment"

def test_scan_environment_degraded_when_no_env(tmp_path):
    """Quando .env está ausente, o status deve ser DEGRADED e registrar issue, mas com exit code tolerante (0)."""
    test_project = tmp_path / "empty_project"
    test_project.mkdir()

    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT), "--cwd", str(test_project)],
        cwd=str(test_project),
        capture_output=True,
        text=True,
        timeout=10
    )
    # Status de saída deve ser 0 (tolerante a ausência de .env)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "DEGRADED"
    assert data["has_env"] is False
    assert any(".env" in issue for issue in data["issues"])

def test_scan_environment_validates_isolated_runtime(tmp_path):
    """Valida detecção de integridade do runtime isolado quando ausente."""
    test_project = tmp_path / "app"
    test_project.mkdir()
    (test_project / ".env").write_text("APP=1\n")

    env = os.environ.copy()
    env["VITALIA_KIT_DIR"] = str(tmp_path / "non_existent_kit_dir")

    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT), "--cwd", str(test_project)],
        cwd=str(test_project),
        env=env,
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["runtime_isolated_ok"] is False
    assert data["status"] == "DEGRADED"
    assert any("Runtime isolado" in issue for issue in data["issues"])

