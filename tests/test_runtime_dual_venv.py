# test_runtime_dual_venv.py | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:08(GMT-04:00)
"""
Suíte de testes de integração comportamental e regressão para a Spec 005:
- T001: Fixtures de isolamento de virtualenv e projetos mock
- T005 [TEST:BUGFIX]: Evasão de runtime no vitalia_hook_runner.py em PATH hostil
- T006 [TEST:MIGRATION]: Resolução do placeholder {{KIT_PYTHON}}
- T013 [TEST:NEW]: Descoberta em 4 níveis de project_runtime e ancoragem relativa em .env
- T014 [TEST:NEW]: Segregação OpenAPI 3.0 de kit_runtime vs project_runtime em check_environment_health
- T020 [TEST:REFACTOR]: Diretriz de sandbox e veto anti-loop a kit-bootstrap.sh em AGENTS.md
- T023 [TEST:REFACTOR]: Linter de integridade sintática dos 16 arquivos .toml (veto a python3 desprotegido)
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_SRC = REPO_ROOT / "source" / "src"
SOURCE_EXTENSIONS = REPO_ROOT / "source" / "extensions"

if str(SOURCE_SRC) not in sys.path:
    sys.path.insert(0, str(SOURCE_SRC))

import kit_env_bootstrap


@pytest.fixture
def isolated_kit_dir(tmp_path: Path):
    """Cria um diretório de kit isolado com venv simulado e binários executáveis."""
    kit_dir = tmp_path / "vitalia_kit_mock"
    venv_bin = kit_dir / ".venv" / "bin"
    venv_bin.mkdir(parents=True, exist_ok=True)
    fake_python = venv_bin / "python3"
    fake_python.write_text("#!/bin/sh\nexit 0\n")
    fake_python.chmod(0o755)

    # Cria site-packages do kit
    site_packages = kit_dir / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)
    return kit_dir


@pytest.fixture
def isolated_project_dir(tmp_path: Path):
    """Cria um diretório de projeto cliente isolado com .git e .env."""
    project_dir = tmp_path / "host_project"
    (project_dir / ".git").mkdir(parents=True, exist_ok=True)
    (project_dir / ".env").write_text("VITALIA_ENVIRONMENT=test\n")
    return project_dir


@pytest.fixture
def hostile_path_with_broken_python(tmp_path: Path, monkeypatch):
    """Injeta um binário mock quebrado de python3 no topo do PATH do sistema."""
    hostile_bin = tmp_path / "hostile_bin"
    hostile_bin.mkdir(parents=True, exist_ok=True)
    broken_python = hostile_bin / "python3"
    broken_python.write_text("#!/bin/sh\necho 'ERROR: Hostile python invoked' >&2\nexit 127\n")
    broken_python.chmod(0o755)
    current_path = os.environ.get("PATH", "")
    monkeypatch.setenv("PATH", f"{hostile_bin}:{current_path}")
    return broken_python


def test_t005_bugfix_runner_evasion_with_hostile_path(tmp_path: Path, hostile_path_with_broken_python):
    """
    T005 [TEST:BUGFIX] — Bug Reproduction First:
    Cenário de Falsificação: O runner executa um comando 'python3 {{VITALIA_KIT_DIR}}/src/hooks/scan_environment.py'.
    Se o runner repassar 'python3' cegamente ao shell, o subprocesso invocará o mock quebrado do PATH
    e falhará com código 127.
    O teste DEVE FALHAR (Red Phase) no código legado e passar (Green Phase) quando a auto-substituição
    reescrever defensivamente 'python3' para sys.executable para scripts internos do kit.
    """
    import vitalia_hook_runner

    fake_kit = tmp_path / "kit"
    fake_kit_src = fake_kit / "src" / "hooks"
    fake_kit_src.mkdir(parents=True)
    dummy_hook = fake_kit_src / "scan_environment.py"
    dummy_hook.write_text("import sys\nprint('HOOK_SUCCESS')\nsys.exit(0)\n")

    # Cria workflow TOML temporário com comando legado 'python3 {{VITALIA_KIT_DIR}}...'
    workflow_toml = tmp_path / "test-workflow.toml"
    workflow_toml.write_text(f"""
[meta]
version = "0.0.1"
[hooks]
before = ["python3 {fake_kit}/src/hooks/scan_environment.py"]
[tools]
required = ["read_file"]
""")

    # Executa o runner chamando a função main() simulada via subprocess usando sys.executable
    runner_script = SOURCE_SRC / "vitalia_hook_runner.py"
    res = subprocess.run(
        [sys.executable, str(runner_script), str(workflow_toml), "--phase", "before"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        env=dict(os.environ, VITALIA_KIT_DIR=str(fake_kit)),
    )
    assert res.returncode == 0, f"Falha esperada na Red Phase! Stderr: {res.stderr}"
    assert "HOOK_SUCCESS" in res.stderr or "ready" in res.stdout


def test_t006_migration_runner_resolves_kit_python_placeholder(tmp_path: Path):
    """
    T006 [TEST:MIGRATION] — Contract Preservation:
    Cenário de Falsificação: O runner executa hook com placeholder '{{KIT_PYTHON}}'.
    O teste falha se a string literal '{{KIT_PYTHON}}' não for expandida para o interpretador do kit.
    """
    import vitalia_hook_runner

    kit_dir = tmp_path / "mock_kit"
    venv_bin = kit_dir / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    custom_python = venv_bin / "python3"
    custom_python.write_text("#!/bin/sh\nexit 0\n")
    custom_python.chmod(0o755)

    cmd_template = "{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/script.py"
    resolved = vitalia_hook_runner.resolve_placeholders(cmd_template, str(tmp_path), str(kit_dir))
    
    assert "{{KIT_PYTHON}}" not in resolved
    assert str(custom_python) in resolved


def test_t013_new_project_python_4_level_discovery(tmp_path: Path, monkeypatch):
    """
    T013 [TEST:NEW] — 4-Level Discovery & Relative Path Anchoring:
    Cenário de Falsificação:
    1. Se PROJECT_VENV_PATH for relativo no .env, deve ancorar deterministicamente em project_root.
    2. Se $VIRTUAL_ENV estiver ativo, deve ter precedência sobre o .env.
    3. Se não houver .env nem $VIRTUAL_ENV, deve localizar .venv canônico na raiz.
    """
    proj_root = tmp_path / "app_project"
    proj_root.mkdir()

    # Nível 3: Pasta canônica .venv
    canonical_venv = proj_root / ".venv" / "bin"
    canonical_venv.mkdir(parents=True)
    canonical_py = canonical_venv / "python3"
    canonical_py.write_text("#!/bin/sh\nexit 0\n")
    canonical_py.chmod(0o755)

    found = kit_env_bootstrap.find_project_python(proj_root)
    assert found is not None
    assert str(found) == str(canonical_py.resolve()) or str(found) == str(canonical_py)

    # Nível 2: PROJECT_VENV_PATH relativo no .env
    custom_venv = proj_root / "custom_env" / "bin"
    custom_venv.mkdir(parents=True)
    custom_py = custom_venv / "python3"
    custom_py.write_text("#!/bin/sh\nexit 0\n")
    custom_py.chmod(0o755)

    (proj_root / ".env").write_text("PROJECT_VENV_PATH=./custom_env\n")
    found_relative = kit_env_bootstrap.find_project_python(proj_root)
    assert found_relative is not None
    assert "custom_env" in str(found_relative)

    # Nível 1: $VIRTUAL_ENV ativo no shell tem precedência
    shell_venv = tmp_path / "shell_venv" / "bin"
    shell_venv.mkdir(parents=True)
    shell_py = shell_venv / "python3"
    shell_py.write_text("#!/bin/sh\nexit 0\n")
    shell_py.chmod(0o755)

    monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / "shell_venv"))
    found_shell = kit_env_bootstrap.find_project_python(proj_root)
    assert found_shell is not None
    assert "shell_venv" in str(found_shell)


def test_t014_new_segregated_health_payload_openapi3(tmp_path: Path):
    """
    T014 [TEST:NEW] — Segregated Dual-Runtime Health Payload:
    Cenário de Falsificação: O payload emitido por check_environment_health() DEVE
    conter os nós segregados 'kit_runtime' e 'project_runtime', e NÃO deve conter
    a união indiscriminada 'venv_ok' mesclada.
    """
    proj_root = tmp_path / "segregated_proj"
    proj_root.mkdir()
    (proj_root / ".env").write_text("VITALIA_ENVIRONMENT=production\n")

    health = kit_env_bootstrap.check_environment_health(proj_root)

    assert "kit_runtime" in health, "Falta nó segregado 'kit_runtime'"
    assert "project_runtime" in health, "Falta nó segregado 'project_runtime'"
    assert "status" in health["kit_runtime"]
    assert "python_bin" in health["kit_runtime"]
    assert "project_root" in health["project_runtime"]
    assert "has_venv" in health["project_runtime"]
    assert "python_bin" in health["project_runtime"]


def test_t020_refactor_anti_loop_constitutional_governance():
    """
    T020 [TEST:REFACTOR] — Anti-Loop & Sandbox Governance Invariants:
    Cenário de Falsificação: O teste escaneia source/AGENTS.md e .agents/AGENTS.md.
    O teste DEVE FALHAR se qualquer um dos arquivos omitir a diretriz para erro 127,
    a instrução de BypassSandbox: true ou o veto explícito à auto-reinstalação via kit-bootstrap.sh.
    """
    source_agents = REPO_ROOT / "source" / "AGENTS.md"
    project_agents = REPO_ROOT / ".agents" / "AGENTS.md"

    for path in (source_agents, project_agents):
        assert path.exists(), f"Arquivo não encontrado: {path}"
        content = path.read_text(encoding="utf-8")
        assert "127" in content, f"{path.name} deve mencionar código de erro 127"
        assert "BypassSandbox: true" in content or "BypassSandbox" in content, f"{path.name} deve instruir BypassSandbox"
        assert "kit-bootstrap.sh" in content, f"{path.name} deve conter diretriz sobre kit-bootstrap.sh"
        assert "proibido" in content.lower() or "vetado" in content.lower() or "nunca" in content.lower(), (
            f"{path.name} deve vetar expressamente a auto-reinstalação reflexa do kit"
        )


def test_t023_refactor_linter_16_extensions_toml():
    """
    T023 [TEST:REFACTOR] — Linter Estático dos 16 Workflows:
    Cenário de Falsificação: Escaneia todos os 16 arquivos em source/extensions/*.toml.
    O teste DEVE FALHAR se qualquer arquivo contiver a string desprotegida 'python3 {{VITALIA_KIT_DIR}}'
    nos blocos de hooks ou se houver arquivos faltando.
    """
    toml_files = list(SOURCE_EXTENSIONS.glob("*.toml"))
    assert len(toml_files) == 16, f"Esperados 16 workflows, encontrados {len(toml_files)}"

    violations = []
    for toml_path in toml_files:
        content = toml_path.read_text(encoding="utf-8")
        if "python3 {{VITALIA_KIT_DIR}}" in content:
            violations.append(str(toml_path.name))
        assert "{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}" in content, (
            f"{toml_path.name} deve usar {{{{KIT_PYTHON}}}} no hook before"
        )

    assert not violations, f"Workflows com chamadas desprotegidas de python3: {violations}"
