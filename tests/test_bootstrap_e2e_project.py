# test_bootstrap_e2e_project.py | Vitalia SPEC Kit v0.0.1 | 06-11-2026 23:00(GMT-04:00)
import os
import subprocess
import glob
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_SCRIPT = REPO_ROOT / "kit-bootstrap.sh"


def test_kit_bootstrap_atom_by_atom_and_no_legacy(tmp_path):
    """Valida instalação isolada e átomo a átomo do kit global sem tocar no host."""
    sandbox_home = tmp_path / "home"
    sandbox_kit = tmp_path / "global_kit"
    sandbox_bin = tmp_path / "local_bin"
    sandbox_home.mkdir()
    sandbox_bin.mkdir()

    env = os.environ.copy()
    env["HOME"] = str(sandbox_home)
    env["VITALIA_KIT_DIR"] = str(sandbox_kit)
    env["LOCAL_BIN"] = str(sandbox_bin)

    # Executa kit-bootstrap.sh em sandbox
    result = subprocess.run(
        ["bash", str(BOOTSTRAP_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"kit-bootstrap falhou:\n{result.stderr}\n{result.stdout}"

    # Valida componentes átomo a átomo copiados
    assert (sandbox_kit / "bin" / "install-project").is_file()
    assert (sandbox_kit / "bin" / "lib" / "logger.sh").is_file()
    assert (sandbox_kit / "bin" / "lib" / "env_manager.sh").is_file()
    assert (sandbox_kit / "bin" / "lib" / "agent_preserver.sh").is_file()
    assert (sandbox_kit / "bin" / "lib" / "git_storage_manager.sh").is_file()
    assert (sandbox_kit / "templates" / "dashboard_template.md").is_file()
    assert (sandbox_kit / "integrations" / "antigravity" / "SKILL.md.template").is_file()
    assert (sandbox_kit / "AGENTS.md").is_file()
    assert (sandbox_kit / "VERSION").is_file()
    assert (sandbox_kit / "extensions" / "analyze.toml").is_file()

    # Valida purga absoluta de legados (FR-003)
    assert not (sandbox_kit / "bin" / "lib" / "redis_detector.sh").exists()
    gp_files = list((sandbox_kit / "profiles").glob("gp_*.yaml"))
    assert len(gp_files) == 0, f"Perfis legados encontrados: {gp_files}"

    # Valida shim gerado em LOCAL_BIN (FR-004)
    shim_file = sandbox_bin / "vitalia-install-project"
    assert shim_file.is_file()
    assert os.access(shim_file, os.X_OK)
    shim_content = shim_file.read_text()
    assert f'export VITALIA_KIT_DIR="{sandbox_kit}"' in shim_content


def test_install_project_in_host_repository(tmp_path):
    """Valida ativação completa em repositório hospedeiro usando o kit instalado."""
    sandbox_home = tmp_path / "home"
    sandbox_kit = tmp_path / "global_kit"
    sandbox_bin = tmp_path / "local_bin"
    host_project = tmp_path / "sample_host_app"
    sandbox_home.mkdir(exist_ok=True)
    sandbox_bin.mkdir(exist_ok=True)
    host_project.mkdir()

    env = os.environ.copy()
    env["HOME"] = str(sandbox_home)
    env["VITALIA_KIT_DIR"] = str(sandbox_kit)
    env["LOCAL_BIN"] = str(sandbox_bin)

    # 1. Bootstrap
    res_boot = subprocess.run(
        ["bash", str(BOOTSTRAP_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert res_boot.returncode == 0

    # 2. Executa install-project dentro do projeto hospedeiro
    install_script = sandbox_kit / "bin" / "install-project"
    res_inst = subprocess.run(
        ["bash", str(install_script)],
        cwd=str(host_project),
        env=env,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert res_inst.returncode == 0, f"install-project falhou:\n{res_inst.stderr}\n{res_inst.stdout}"

    # Valida estrutura .vitalia criada
    vitalia_dir = host_project / ".vitalia"
    assert vitalia_dir.is_dir()
    assert (vitalia_dir / "feature.json").is_file()
    assert (vitalia_dir / "config.yml").is_file()

    # Valida ausência do Gemini CLI em config.yml (FR-011)
    config_content = (vitalia_dir / "config.yml").read_text()
    assert "gemini_cli" not in config_content
    assert "antigravity: true" in config_content

    # Valida registro de analyze em extensions.yml (FR-021)
    extensions_yml = (vitalia_dir / "extensions.yml").read_text()
    assert "analyze" in extensions_yml

    # Valida .env do projeto
    env_content = (host_project / ".env").read_text()
    assert f"VITALIA_KIT_DIR={sandbox_kit}" in env_content

    # Valida geração das skills
    skills_dir = host_project / ".agents" / "skills"
    assert (skills_dir / "vitalia-analyze" / "SKILL.md").is_file()
    assert (skills_dir / "vitalia-session-start" / "SKILL.md").is_file()

    # Valida que SKILL.md inicia rigorosamente na linha 1 com '---' (FR-012, SC-003)
    skill_content = (skills_dir / "vitalia-analyze" / "SKILL.md").read_text()
    first_line = skill_content.splitlines()[0]
    assert first_line == "---", f"Linha 1 da skill deve ser '---', mas foi: '{first_line}'"

    # Valida log de instalação detalhado gerado na raiz (FR-008, FR-009)
    log_files = list(host_project.glob("install_*.log"))
    assert len(log_files) >= 1, "Arquivo install_*.log deve ser gerado"
    log_content = log_files[0].read_text()
    assert "[STEP] PASSO 1" in log_content
    assert "[OK]" in log_content


def test_context_engine_rich_dashboard_consolidation(tmp_path):
    """Valida renderização completa do Dashboard canônico rico sem Redis."""
    sandbox_kit = tmp_path / "global_kit"
    sandbox_bin = tmp_path / "local_bin"
    host_project = tmp_path / "sample_host_app"
    sandbox_bin.mkdir(parents=True, exist_ok=True)
    host_project.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")
    env["VITALIA_KIT_DIR"] = str(sandbox_kit)
    env["LOCAL_BIN"] = str(sandbox_bin)

    # 1. Bootstrap & Ativação
    subprocess.run(["bash", str(BOOTSTRAP_SCRIPT)], cwd=str(REPO_ROOT), env=env, check=True)
    subprocess.run(["bash", str(sandbox_kit / "bin" / "install-project")], cwd=str(host_project), env=env, check=True)

    # 2. Cria dados sintéticos de sessão
    session_dir = host_project / ".vitalia" / "memory" / "session"
    session_history = session_dir / "session_history.jsonl"
    session_history.write_text(
        '{"session_id": "ses-001", "started_at": "06-11-2026 22:00:00(GMT-04:00)", "machine_id": "test-box-01", "summary": "Sessão de Teste E2E"}\n'
    )
    decisions = host_project / ".vitalia" / "memory" / "data_storage" / "decisions.jsonl"
    decisions.parent.mkdir(parents=True, exist_ok=True)
    decisions.write_text(
        '{"id": "DEC-001", "timestamp": "06-11-2026 22:10:00(GMT-04:00)", "title": "Adoção de SRP", "rationale": "Desacoplamento e coesão."}\n'
    )

    # 3. Executa consolidate
    engine_script = sandbox_kit / "src" / "vitalia_context_engine.py"
    res_cons = subprocess.run(
        ["python3", str(engine_script), "--action", "consolidate"],
        cwd=str(host_project),
        env=env,
        capture_output=True,
        text=True
    )
    assert res_cons.returncode == 0, f"Consolidação falhou:\n{res_cons.stderr}\n{res_cons.stdout}"

    # 4. Inspeciona o README gerado (SC-006, FR-019, FR-020)
    readme_file = session_dir / "README.md"
    assert readme_file.is_file(), "README.md consolidado deve existir"
    readme_text = readme_file.read_text()

    assert "Vitalia SPEC Kit" in readme_text
    assert "GMT-04:00" in readme_text
    assert "```mermaid" in readme_text
    assert "flowchart TD" in readme_text
    assert "<details>" in readme_text
    assert "</details>" in readme_text
    assert "test-box-01" in readme_text
    assert "DEC-001" in readme_text
    assert "redis" not in readme_text.lower(), "Nenhuma menção a redis permitida"
