# test_bootstrap.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import os
import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_SCRIPT = REPO_ROOT / "kit-bootstrap.sh"
REQUIREMENTS_FILE = REPO_ROOT / "requirements.txt"

def test_bootstrap_script_exists():
    """Valida se o script kit-bootstrap.sh existe e possui permissão de execução."""
    assert BOOTSTRAP_SCRIPT.exists(), "kit-bootstrap.sh deve existir na raiz do repositório"
    assert os.access(BOOTSTRAP_SCRIPT, os.X_OK), "kit-bootstrap.sh deve ter permissão de execução (+x)"

def test_requirements_file_exists():
    """Valida se requirements.txt existe e declara dependências essenciais."""
    assert REQUIREMENTS_FILE.exists(), "requirements.txt deve existir"
    content = REQUIREMENTS_FILE.read_text()
    assert "pyyaml" in content
    assert "jinja2" in content
    assert "click" in content

def test_bootstrap_execution_creates_isolated_runtime(tmp_path):
    """Testa a execução do bootstrap criando o diretório unificado e o virtualenv."""
    custom_home = tmp_path / "home"
    custom_home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(custom_home)
    
    # Executa o script apontando para HOME temporário
    result = subprocess.run(
        ["bash", str(BOOTSTRAP_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Bootstrap falhou: {result.stderr}\nOutput: {result.stdout}"
    
    # Verifica a criação do diretório global ~/.vitalia-spec-kit e .venv
    vitalia_dir = custom_home / ".vitalia-spec-kit"
    assert vitalia_dir.exists(), "Diretório unificado ~/.vitalia-spec-kit deve ser criado"
    
    venv_python = vitalia_dir / ".venv" / "bin" / "python3"
    assert venv_python.exists(), "Python isolado .venv/bin/python3 deve existir"
    
    # Verifica a existência dos shims em ~/.local/bin/
    local_bin = custom_home / ".local" / "bin"
    assert local_bin.exists(), "Diretório ~/.local/bin deve ser criado"
    
    shim_install = local_bin / "vitalia-install-project"
    assert shim_install.exists(), "Shim vitalia-install-project deve existir"
    assert os.access(shim_install, os.X_OK), "Shim deve ser executável"
