# test_bootstrap_and_install.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:53(GMT-04:00)
"""
Suíte de testes comportamentais de Caixa-Preta (E2E) para US1 e US2:
- T011 [TEST:NEW]: test_kit_bootstrap_clean_machine_e2e
- T012 [TEST:BUGFIX]: test_kit_bootstrap_aborts_cleanly_when_venv_missing (RCA-02)
- T014 [TEST:BUGFIX]: test_install_project_skills_directory_purity (RCA-04a)
- T015 [TEST:MIGRATION]: test_git_storage_manager_remote_clone_and_local_init_fallback (RCA-04b)
"""

import os
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_16_WORKFLOWS = [
    "analyze.toml",
    "architect.toml",
    "brainstorming.toml",
    "clarify.toml",
    "converge.toml",
    "judge.toml",
    "research.toml",
    "route.toml",
    "session-consolidate.toml",
    "session-end.toml",
    "session-start.toml",
    "spec-implement.toml",
    "spec-plan.toml",
    "spec-specify.toml",
    "spec-tasks.toml",
    "task-verifier.toml",
]

CANONICAL_14_LENSES = [
    "gp_analyze.yaml",
    "gp_architect.yaml",
    "gp_brainstorming.yaml",
    "gp_research.yaml",
    "gp_sdd-judge.yaml",
    "gp_session-consolidate.yaml",
    "gp_session-end.yaml",
    "gp_session-start.yaml",
    "gp_spec-implement.yaml",
    "gp_spec-plan.yaml",
    "gp_spec-specify.yaml",
    "gp_spec-tasks.yaml",
    "gp_task-verifier.yaml",
    "gp_vitalia-route.yaml",
]


def test_kit_bootstrap_clean_machine_e2e(tmp_path: Path):
    """
    T011 [TEST:NEW] — Executa ./kit-bootstrap.sh em HOME isolado e valida:
    1. Código de retorno 0;
    2. Importação de yaml, jinja2, jsonschema no .venv/bin/python3 do kit instalado;
    3. Presença funcional dos 16 workflows .toml, 14 lentes gp_*.yaml, templates, schemas e módulos;
    4. Idempotência de injeção em .bashrc e .zshrc;
    5. Execução funcional do shim ~/.local/bin/vitalia-install-project --help.
    """
    fake_home = tmp_path / "home"
    fake_home.mkdir(parents=True)
    (fake_home / ".bashrc").write_text("# bashrc\n", encoding="utf-8")
    (fake_home / ".zshrc").write_text("# zshrc\n", encoding="utf-8")

    target_kit_dir = fake_home / ".vitalia-spec-kit-custom"
    bootstrap_script = REPO_ROOT / "kit-bootstrap.sh"

    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    env.pop("VITALIA_KIT_DIR", None)

    proc = subprocess.run(
        [str(bootstrap_script), "--target-dir", str(target_kit_dir), "--non-interactive"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"kit-bootstrap.sh failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

    venv_python = target_kit_dir / ".venv" / "bin" / "python3"
    assert venv_python.exists(), "Isolated .venv/bin/python3 was not created"

    import_check = subprocess.run(
        [str(venv_python), "-c", "import yaml, jinja2, jsonschema; print('OK')"],
        capture_output=True,
        text=True,
    )
    assert import_check.returncode == 0, f".venv python failed to import dependencies: {import_check.stderr}"
    assert "OK" in import_check.stdout

    for wf in CANONICAL_16_WORKFLOWS:
        assert (target_kit_dir / "extensions" / wf).is_file(), f"Missing workflow {wf} in installed kit"

    for lens in CANONICAL_14_LENSES:
        assert (target_kit_dir / "profiles" / lens).is_file(), f"Missing lens {lens} in installed kit"

    for core_profile in [
        "constitution.yaml",
        "grounding_domains.yaml",
        "dynamic_questioning.yaml",
        "brainstorming_intents.yaml",
        "agents_catalog.yaml",
        "routing_table.yaml",
    ]:
        assert (target_kit_dir / "profiles" / core_profile).is_file(), f"Missing {core_profile}"

    assert (target_kit_dir / "templates" / "dashboard_template.md").is_file()
    assert (target_kit_dir / "integrations" / "antigravity" / "SKILL.md.template").is_file()
    assert (target_kit_dir / "AGENTS.md").is_file()
    assert not (target_kit_dir / "bin" / "lib" / "redis_detector.sh").exists()

    shim_path = fake_home / ".local" / "bin" / "vitalia-install-project"
    assert shim_path.is_file() and os.access(shim_path, os.X_OK), "Shim vitalia-install-project not executable"

    help_proc = subprocess.run(
        [str(shim_path), "--help"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert help_proc.returncode == 0, f"vitalia-install-project --help failed: {help_proc.stderr}"

    # Re-run to verify RC idempotency
    proc2 = subprocess.run(
        [str(bootstrap_script), "--target-dir", str(target_kit_dir), "--non-interactive"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc2.returncode == 0
    zshrc_content = (fake_home / ".zshrc").read_text(encoding="utf-8")
    assert zshrc_content.count("export VITALIA_KIT_DIR=") == 1, "Duplicate VITALIA_KIT_DIR export in .zshrc"


def test_kit_bootstrap_aborts_cleanly_when_venv_missing(tmp_path: Path):
    """
    T012 [TEST:BUGFIX] (RCA-02) — Verifica que se python3 -m venv falhar,
    kit-bootstrap.sh aborta com código != 0 ANTES de criar target_dir e exibe
    instrução diagnóstica sobre python3-venv no stderr.
    """
    fake_home = tmp_path / "home"
    fake_home.mkdir(parents=True)
    fake_bin = tmp_path / "fake_bin"
    fake_bin.mkdir(parents=True)

    # Create a fake python3 wrapper that fails when invoked with `-m venv`
    real_python = subprocess.check_output(["which", "python3"], text=True).strip()
    fake_python = fake_bin / "python3"
    fake_python.write_text(
        f"""#!/usr/bin/env bash
if [[ "$1" == "-m" && "$2" == "venv" ]]; then
    echo "The virtual environment was not created successfully because ensurepip is not available." >&2
    exit 1
fi
exec "{real_python}" "$@"
""",
        encoding="utf-8",
    )
    fake_python.chmod(fake_python.stat().st_mode | stat.S_IEXEC)

    target_kit_dir = fake_home / ".vitalia-broken-kit"
    bootstrap_script = REPO_ROOT / "kit-bootstrap.sh"

    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    env["PATH"] = f"{fake_bin}:{env.get('PATH', '')}"

    proc = subprocess.run(
        [str(bootstrap_script), "--target-dir", str(target_kit_dir), "--non-interactive"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0, "kit-bootstrap.sh must fail when python3 -m venv is unavailable"
    assert not target_kit_dir.exists(), (
        f"kit-bootstrap.sh created partial directory {target_kit_dir} before validating python3 -m venv!"
    )
    combined_err = (proc.stderr + proc.stdout).lower()
    assert "venv" in combined_err, "Diagnostic message must mention venv / python3-venv"


def test_install_project_skills_directory_purity(tmp_path: Path):
    """
    T014 [TEST:BUGFIX] (RCA-04a) — Executa install-project duas vezes sobre um projeto
    hospedeiro contendo skills customizadas e skills vitalia pré-existentes e verifica:
    1. Zero arquivos/pastas ocultas (.trash, .vitalia-manifest) dentro de .agents/skills/;
    2. Exatamente as 16 skills vitalia-* + a skill customizada do usuário intacta;
    3. Substituição completa do placeholder {{VITALIA_KIT_DIR}} em todas as SKILL.md.
    """
    fake_home = tmp_path / "home"
    fake_home.mkdir(parents=True)
    kit_dir = fake_home / ".vitalia-spec-kit"

    env = os.environ.copy()
    env["HOME"] = str(fake_home)

    # First bootstrap the kit
    boot = subprocess.run(
        [str(REPO_ROOT / "kit-bootstrap.sh"), "--target-dir", str(kit_dir), "--non-interactive"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert boot.returncode == 0, f"Bootstrap failed: {boot.stderr}"

    # Create a host project with a custom skill and an old vitalia skill
    project_dir = tmp_path / "host_project"
    custom_skill_dir = project_dir / ".agents" / "skills" / "my-custom-skill"
    custom_skill_dir.mkdir(parents=True)
    (custom_skill_dir / "SKILL.md").write_text("# Custom User Skill\n", encoding="utf-8")

    old_vitalia_skill = project_dir / ".agents" / "skills" / "vitalia-old-obsolete"
    old_vitalia_skill.mkdir(parents=True)
    (old_vitalia_skill / "SKILL.md").write_text("# Old Obsolete Skill\n", encoding="utf-8")

    env["VITALIA_KIT_DIR"] = str(kit_dir)
    install_bin = kit_dir / "bin" / "install-project"

    # Run install-project twice to trigger backup/cleanup logic
    for run_idx in range(2):
        res = subprocess.run(
            [str(install_bin), "--non-interactive"],
            cwd=str(project_dir),
            env=env,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"install-project run {run_idx + 1} failed:\n{res.stdout}\n{res.stderr}"

    skills_dir = project_dir / ".agents" / "skills"
    entries = list(skills_dir.iterdir())
    hidden_entries = [p.name for p in entries if p.name.startswith(".")]
    assert hidden_entries == [], f"Consumer contract violated! Hidden files in .agents/skills/: {hidden_entries}"

    # Custom skill must be preserved
    assert (custom_skill_dir / "SKILL.md").is_file()
    # Old vitalia skill must be moved to .vitalia/backups/, not left in .agents/skills/
    assert not old_vitalia_skill.exists(), "Obsolete vitalia-* skill was not cleaned from .agents/skills/"

    # Exactly 16 vitalia-* skills must exist and have {{VITALIA_KIT_DIR}} resolved
    vitalia_skills = sorted(p for p in entries if p.is_dir() and p.name.startswith("vitalia-"))
    assert len(vitalia_skills) == 16, f"Expected 16 vitalia-* skills, found {len(vitalia_skills)}: {[p.name for p in vitalia_skills]}"

    for skill_folder in vitalia_skills:
        skill_md = skill_folder / "SKILL.md"
        assert skill_md.is_file(), f"Missing SKILL.md in {skill_folder}"
        content = skill_md.read_text(encoding="utf-8")
        assert "{{VITALIA_KIT_DIR}}" not in content, f"Unresolved {{{{VITALIA_KIT_DIR}}}} in {skill_md}"
        assert str(kit_dir) in content, f"Kit path {kit_dir} not injected into {skill_md}"


def test_git_storage_manager_remote_clone_and_local_init_fallback(tmp_path: Path):
    """
    T015 [TEST:MIGRATION] (RCA-04b) — Verifica que install-project / git_storage_manager.sh:
    1. Clona um repositório Git remoto (bare repo com commit real) via git clone --depth=1;
    2. Inicializa com git init -b main quando nenhuma URL remota é fornecida.
    """
    fake_home = tmp_path / "home"
    fake_home.mkdir(parents=True)
    kit_dir = fake_home / ".vitalia-spec-kit"

    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    env["VITALIA_KIT_DIR"] = str(kit_dir)

    boot = subprocess.run(
        [str(REPO_ROOT / "kit-bootstrap.sh"), "--target-dir", str(kit_dir), "--non-interactive"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert boot.returncode == 0, f"Bootstrap failed: {boot.stderr}"

    # Create a bare git repository with an initial commit to simulate a remote session repo
    bare_remote = tmp_path / "remote_session.git"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(bare_remote)], check=True, capture_output=True)

    seed_work = tmp_path / "seed_work"
    subprocess.run(["git", "clone", str(bare_remote), str(seed_work)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(seed_work), "config", "user.email", "test@vitalia.local"], check=True)
    subprocess.run(["git", "-C", str(seed_work), "config", "user.name", "Vitalia Test"], check=True)
    (seed_work / "REMOTE_MARKER.md").write_text("Cloned from remote!\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(seed_work), "add", "REMOTE_MARKER.md"], check=True)
    subprocess.run(["git", "-C", str(seed_work), "commit", "-m", "initial remote commit"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(seed_work), "push", "origin", "main"], check=True, capture_output=True)

    # Install project with --session-repo pointing to bare_remote and no --data-repo (local init fallback)
    project_dir = tmp_path / "project_with_remote"
    project_dir.mkdir(parents=True)

    res = subprocess.run(
        [
            str(kit_dir / "bin" / "install-project"),
            "--session-repo",
            str(bare_remote),
            "--non-interactive",
        ],
        cwd=str(project_dir),
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"install-project failed:\n{res.stdout}\n{res.stderr}"

    # Verify session repo was cloned from remote (contains REMOTE_MARKER.md)
    session_marker = project_dir / ".vitalia" / "memory" / "session" / "REMOTE_MARKER.md"
    assert session_marker.is_file(), "git_storage_manager.sh did not clone existing remote repository!"
    assert session_marker.read_text(encoding="utf-8") == "Cloned from remote!\n"

    # Verify data_storage fell back to local git init
    data_git = project_dir / ".vitalia" / "memory" / "data_storage" / ".git"
    assert data_git.is_dir(), "git_storage_manager.sh did not initialize local git repo when remote URL was omitted!"

