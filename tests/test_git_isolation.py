# test_git_isolation.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import os
import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_PROJECT_SCRIPT = REPO_ROOT / "source" / "bin" / "install-project"

def test_install_project_creates_gitignore_with_memory_protection(tmp_path):
    """
    Testa se a execução de install-project num projeto sem .gitignore cria o arquivo
    e adiciona compulsoriamente a proteção para .vitalia/memory/.
    """
    project_dir = tmp_path / "target_project"
    project_dir.mkdir()

    env = os.environ.copy()
    env["VITALIA_KIT_DIR"] = str(REPO_ROOT)
    
    # Executa em modo não-interativo (stdin fechado /dev/null)
    result = subprocess.run(
        ["bash", str(INSTALL_PROJECT_SCRIPT)],
        cwd=str(project_dir),
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"install-project falhou: {result.stderr}\nStdout: {result.stdout}"

    gitignore = project_dir / ".gitignore"
    assert gitignore.exists(), ".gitignore deve ser criado se inexistente"
    content = gitignore.read_text(encoding="utf-8")

    assert ".vitalia/memory/" in content, ".vitalia/memory/ deve estar protegido no .gitignore"
    assert ".env" in content, ".env deve estar protegido no .gitignore"

def test_install_project_purged_redis_detector():
    """Valida que install-project não referencia mais redis_detector.sh nem variáveis de Redis."""
    content = INSTALL_PROJECT_SCRIPT.read_text(encoding="utf-8")
    assert "redis_detector.sh" not in content, "redis_detector.sh não deve ser carregado"
    assert "detect_redis" not in content, "detect_redis não deve ser chamado"
