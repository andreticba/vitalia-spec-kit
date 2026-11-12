# test_runtime_and_guardian.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 19:59(GMT-04:00)
"""
Suíte de testes comportamentais para US3 (Context Lifting Isolado e Governança 100% Sem Poda):
- T020 [TEST:BUGFIX]: test_scan_environment_and_kit_bootstrap_healthy_without_redis
- T021 [TEST:MIGRATION]: test_all_16_workflows_execute_with_zero_pruning_and_isolated_context
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_SRC = REPO_ROOT / "source" / "src"

CANONICAL_16_WORKFLOWS = [
    "analyze",
    "architect",
    "brainstorming",
    "clarify",
    "converge",
    "judge",
    "research",
    "route",
    "session-consolidate",
    "session-end",
    "session-start",
    "spec-implement",
    "spec-plan",
    "spec-specify",
    "spec-tasks",
    "task-verifier",
]


def test_scan_environment_and_kit_bootstrap_healthy_without_redis(tmp_path: Path):
    """
    T020 [TEST:BUGFIX] — Verifica que:
    1. scan_environment.py reporta status HEALTHY / OK em projeto hospedeiro sem Redis (6379) e sem .venv local;
    2. kit_env_bootstrap.py resolve VITALIA_KIT_DIR na precedência:
       env var -> .env -> ~/.vitalia-spec-kit (nunca ~/.vitalia).
    """
    project_dir = tmp_path / "host_project"
    project_dir.mkdir(parents=True)
    fake_kit_dir = tmp_path / "custom_kit"
    fake_kit_dir.mkdir(parents=True)

    (project_dir / ".env").write_text(
        f"VITALIA_ENVIRONMENT=development\nVITALIA_KIT_DIR={fake_kit_dir}\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env.pop("VITALIA_KIT_DIR", None)
    env.pop("REDIS_URL", None)

    scan_script = SOURCE_SRC / "hooks" / "scan_environment.py"
    proc = subprocess.run(
        [sys.executable, str(scan_script), "--cwd", str(project_dir)],
        cwd=str(project_dir),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"scan_environment.py failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

    report = json.loads(proc.stdout)
    assert report.get("status") in ("HEALTHY", "OK"), f"Expected HEALTHY/OK without Redis/.venv, got: {report}"
    assert report.get("has_env") is True
    assert report.get("kit_dir") == str(fake_kit_dir)
    assert "redis_port_open" not in report, "Legacy Redis port probe must be purged from health report"


def test_all_16_workflows_execute_with_zero_pruning_and_isolated_context(tmp_path: Path):
    """
    T021 [TEST:MIGRATION] — Executa vitalia_hook_runner.py para TODOS os 16 workflows (.toml)
    em um projeto hospedeiro isolado e valida:
    1. Código de retorno 0 para cada um dos 16 workflows;
    2. Nenhum erro de Redis e nenhum warning de gp_*.yaml ausente no stderr;
    3. Stub stdout aponta exclusivamente para .vitalia/memory/data_storage/context/<machine_id>/<wf>_*.json;
    4. Zero arquivos criados em tmp/ global;
    5. Envelope JSON válido segundo context-lifting-envelope.schema.json;
    6. Ausência de tmp_cleanup_matrix;
    7. guardian_json.token_budget == 0;
    8. guardian_json.sources.constitution.principles contém todos os 18 princípios (P00–P17) sem poda;
    9. Detecção de expiração temporal (valid_until no passado -> TEMPORAL_REFRESH_REQUIRED).
    """
    fake_home = tmp_path / "home"
    fake_home.mkdir(parents=True)
    kit_dir = fake_home / ".vitalia-spec-kit"

    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    env["VITALIA_KIT_DIR"] = str(kit_dir)
    env["VITALIA_MACHINE_NAME"] = "test-machine-wsl2"

    # Bootstrap kit and install project
    boot = subprocess.run(
        [str(REPO_ROOT / "kit-bootstrap.sh"), "--target-dir", str(kit_dir), "--non-interactive"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert boot.returncode == 0, f"Bootstrap failed: {boot.stderr}"

    project_dir = tmp_path / "clean_project"
    project_dir.mkdir(parents=True)
    inst = subprocess.run(
        [str(kit_dir / "bin" / "install-project"), "--non-interactive"],
        cwd=str(project_dir),
        env=env,
        capture_output=True,
        text=True,
    )
    assert inst.returncode == 0, f"install-project failed: {inst.stderr}"

    hook_runner = kit_dir / "src" / "vitalia_hook_runner.py"
    venv_python = kit_dir / ".venv" / "bin" / "python3"

    import jsonschema

    envelope_schema = json.loads(
        (kit_dir / "src" / "schemas" / "context-lifting-envelope.schema.json").read_text(encoding="utf-8")
    )

    raw_constitution = yaml.safe_load((kit_dir / "profiles" / "constitution.yaml").read_text(encoding="utf-8"))
    expected_principles = set(raw_constitution["principles"].keys())

    for wf in CANONICAL_16_WORKFLOWS:
        toml_path = kit_dir / "extensions" / f"{wf}.toml"
        assert toml_path.is_file(), f"Missing {toml_path}"

        res = subprocess.run(
            [
                str(venv_python),
                str(hook_runner),
                str(toml_path),
                "--phase",
                "before",
                "--args",
                f"test input for {wf}",
            ],
            cwd=str(project_dir),
            env=env,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"Workflow {wf} failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        assert "redis" not in res.stderr.lower(), f"Redis mention in stderr for {wf}: {res.stderr}"
        assert "warning" not in res.stderr.lower(), f"Unexpected warning in stderr for {wf}: {res.stderr}"

        stub = json.loads(res.stdout)
        assert stub["status"] == "ready"
        assert stub["workflow"] == wf

        ctx_file = Path(stub["workflow_context_file"])
        assert ctx_file.is_file(), f"Context file {ctx_file} does not exist"
        assert ".vitalia/memory/data_storage/context/" in str(ctx_file), (
            f"Context file must be inside .vitalia/memory/data_storage/context/<machine_id>/, got: {ctx_file}"
        )
        assert not (kit_dir / "tmp").exists(), "Global kit_dir/tmp directory must never be created!"

        envelope = json.loads(ctx_file.read_text(encoding="utf-8"))
        jsonschema.validate(instance=envelope, schema=envelope_schema)

        g_json = envelope["guardian_json"]
        assert "tmp_cleanup_matrix" not in g_json, f"tmp_cleanup_matrix leaked in {wf}"
        assert g_json["token_budget"] == 0, f"Expected token_budget == 0 in {wf}, got {g_json['token_budget']}"
        assert "guardian_advisory" not in g_json, f"Missing dedicated profile caused advisory in {wf}: {g_json.get('guardian_advisory')}"

        principles = g_json["sources"]["constitution"]["principles"]
        assert set(principles.keys()) == expected_principles, (
            f"Workflow {wf} pruned constitution! Expected {len(expected_principles)} principles, got {len(principles)}: {list(principles.keys())}"
        )

    # Verify temporal expiration check on grounding_domains.yaml (valid_until in the past -> TEMPORAL_REFRESH_REQUIRED)
    gd_path = kit_dir / "profiles" / "grounding_domains.yaml"
    gd_text = gd_path.read_text(encoding="utf-8")
    expired_gd = gd_text.replace("05-02-2027", "01-01-2020", 1)
    gd_path.write_text(expired_gd, encoding="utf-8")

    res_exp = subprocess.run(
        [
            str(venv_python),
            str(hook_runner),
            str(kit_dir / "extensions" / "spec-plan.toml"),
            "--phase",
            "before",
        ],
        cwd=str(project_dir),
        env=env,
        capture_output=True,
        text=True,
    )
    assert res_exp.returncode == 0
    stub_exp = json.loads(res_exp.stdout)
    env_exp = json.loads(Path(stub_exp["workflow_context_file"]).read_text(encoding="utf-8"))
    domains = env_exp["guardian_json"]["sources"]["grounding_domains"]["domains"]
    statuses = [d.get("status") for d in domains]
    assert "TEMPORAL_REFRESH_REQUIRED" in statuses, (
        f"Guardian did not mark expired domain with TEMPORAL_REFRESH_REQUIRED! Statuses: {statuses}"
    )

