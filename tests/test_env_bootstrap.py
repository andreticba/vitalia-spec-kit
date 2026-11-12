# test_env_bootstrap.py | Vitalia SPEC Kit v0.0.1 | 11-11-2026 22:01(GMT-04:00)
"""
Testes de auto-descoberta de ambiente e purga de VITALIA_KIT_DIR do .env (T003 / FR-003).
Cenário de Falsificação (P05): Falha se manage_kit_env gravar VITALIA_KIT_DIR no .env do cliente
ou se resolve_kit_dir e find_project_root falharem na auto-descoberta sem a variável no .env.
"""

from pathlib import Path
import os
import subprocess
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "source" / "src"
ENV_MANAGER_SCRIPT = REPO_ROOT / "source" / "bin" / "lib" / "env_manager.sh"

import sys
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from kit_env_bootstrap import find_project_root, resolve_kit_dir, resolve_kit_python


def test_auto_discovery_without_env_variable(tmp_path, monkeypatch):
    """
    FR-003: resolve_kit_dir e find_project_root devem resolver corretamente
    sem exigir VITALIA_KIT_DIR no os.environ ou no arquivo .env do projeto cliente.
    """
    monkeypatch.delenv("VITALIA_KIT_DIR", raising=False)

    project_dir = tmp_path / "fake_project"
    vitalia_dir = project_dir / ".vitalia"
    vitalia_dir.mkdir(parents=True)

    # Cria .env no projeto cliente SEM VITALIA_KIT_DIR
    env_file = project_dir / ".env"
    env_file.write_text("VITALIA_ENVIRONMENT=development\n", encoding="utf-8")

    # Verifica descoberta do project_root
    discovered_root = find_project_root(project_dir)
    assert discovered_root == project_dir, "Falha ao identificar raiz do projeto"

    # Verifica resolução do kit_dir
    resolved_kit = resolve_kit_dir(project_dir)
    assert resolved_kit.exists(), f"Kit dir resolvido não existe: {resolved_kit}"
    assert resolved_kit.name in [".vitalia-spec-kit", "source", "vitalia-spec-kit"], (
        f"Kit dir resolvido inesperado: {resolved_kit}"
    )


def test_manage_kit_env_purges_kit_dir_variable(tmp_path):
    """
    FR-003 / Cenário de Falsificação:
    Ao executar manage_kit_env para inicializar ou atualizar o .env do cliente,
    a chave VITALIA_KIT_DIR NÃO deve ser escrita no arquivo .env.
    """
    env_file = tmp_path / ".env"
    fake_kit_dir = "/home/user/.vitalia-spec-kit"
    fake_session_repo = "git@github.com:test/session.git"
    fake_data_repo = "git@github.com:test/data.git"

    bash_code = f"""
    source "{ENV_MANAGER_SCRIPT}"
    manage_kit_env "{env_file}" "{fake_kit_dir}" "{fake_session_repo}" "{fake_data_repo}"
    """
    res = subprocess.run(
        ["bash", "-c", bash_code],
        capture_output=True,
        text=True,
        check=False
    )
    assert res.returncode == 0, f"Erro ao executar manage_kit_env: {res.stderr}"

    assert env_file.exists()
    env_content = env_file.read_text(encoding="utf-8")

    # Cenário de Falsificação: Falha se a chave VITALIA_KIT_DIR for escrita no .env do cliente
    assert "VITALIA_KIT_DIR" not in env_content, (
        "Cenário de Falsificação atingido: manage_kit_env ainda injeta 'VITALIA_KIT_DIR' no .env do cliente."
    )
    assert "VITALIA_ENVIRONMENT=development" in env_content
    assert "SESSION_REPO=" in env_content
    assert "DATA_REPO=" in env_content

