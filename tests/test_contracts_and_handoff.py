# test_contracts_and_handoff.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:11(GMT-04:00)
"""
Suíte de testes comportamentais para US5 (Handoff Determinístico, Contratos OpenAPI 3.0 e CLI --help P10):
- T030 [TEST:MIGRATION]:
  1. test_vitalia_handoff_create_pending_consume_from_subdir
  2. test_openapi30_purity_and_yaml_catalog_validation
  3. test_all_cli_entrypoints_support_help_flag
"""

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "source"
SOURCE_SRC = SOURCE_DIR / "src"


def test_vitalia_handoff_create_pending_consume_from_subdir(tmp_path: Path):
    """
    Exercita o ciclo completo create -> latest -> validate -> consume do vitalia_handoff.py
    executado a partir de um subdiretório aninhado do projeto hospedeiro.
    """
    project_root = tmp_path / "host_project"
    (project_root / ".vitalia" / "memory" / "data_storage" / "handoffs").mkdir(parents=True)
    (project_root / ".vitalia" / "feature.json").write_text(
        '{"feature_directory": "specs/002-universal-bootstrap-runtime"}',
        encoding="utf-8",
    )

    nested_subdir = project_root / "src" / "deep" / "module"
    nested_subdir.mkdir(parents=True)

    handoff_cli = SOURCE_SRC / "vitalia_handoff.py"

    # 1. Create handoff from nested subdir without --project-root (must auto-discover project_root)
    create_proc = subprocess.run(
        [
            sys.executable,
            str(handoff_cli),
            "create",
            "--source",
            "architect",
            "--target",
            "spec-specify",
            "--intent",
            "sdd_pipeline_advance",
            "--input",
            "Consolidar Spec 002",
            "--summary",
            "Regência arquitetural aprovada",
            "--direction",
            "forward",
            "--feature",
            "specs/002-universal-bootstrap-runtime",
        ],
        cwd=str(nested_subdir),
        capture_output=True,
        text=True,
    )
    assert create_proc.returncode == 0, f"handoff create failed:\n{create_proc.stdout}\n{create_proc.stderr}"
    create_out = json.loads(create_proc.stdout)
    assert create_out["status"] == "created"
    handoff_file = Path(create_out["file"])
    assert handoff_file.is_file()
    assert str(project_root) in str(handoff_file)

    # 2. Latest pending handoff from nested subdir
    latest_proc = subprocess.run(
        [sys.executable, str(handoff_cli), "latest", "--target", "vitalia-spec-specify"],
        cwd=str(nested_subdir),
        capture_output=True,
        text=True,
    )
    assert latest_proc.returncode == 0
    assert Path(latest_proc.stdout.strip()) == handoff_file.resolve()

    # 3. Validate handoff file
    val_proc = subprocess.run(
        [sys.executable, str(handoff_cli), "validate", "--file", str(handoff_file)],
        cwd=str(nested_subdir),
        capture_output=True,
        text=True,
    )
    assert val_proc.returncode == 0
    assert json.loads(val_proc.stdout)["status"] == "valid"

    # 4. Consume handoff file
    con_proc = subprocess.run(
        [sys.executable, str(handoff_cli), "consume", "--file", str(handoff_file)],
        cwd=str(nested_subdir),
        capture_output=True,
        text=True,
    )
    assert con_proc.returncode == 0
    assert json.loads(con_proc.stdout)["status"] == "consumed"

    # 5. After consumption, latest pending must return empty
    latest_after = subprocess.run(
        [sys.executable, str(handoff_cli), "latest", "--target", "spec-specify"],
        cwd=str(nested_subdir),
        capture_output=True,
        text=True,
    )
    assert latest_after.returncode == 0
    assert latest_after.stdout.strip() == ""


def test_openapi30_purity_and_yaml_catalog_validation():
    """
    Verifica que:
    1. Nenhum schema em source/src/schemas/*.json contém $schema, title na raiz ou additionalProperties: false;
    2. Todos os 6 catálogos YAML + 14 lentes gp_*.yaml validam contra seus respectivos schemas.
    """
    schemas_dir = SOURCE_SRC / "schemas"
    schema_files = list(schemas_dir.glob("*.json"))
    assert len(schema_files) >= 9

    for sf in schema_files:
        raw_text = sf.read_text(encoding="utf-8")
        data = json.loads(raw_text)
        assert "$schema" not in data, f"Forbidden $schema in {sf.name}"
        assert "title" not in data, f"Forbidden top-level title in {sf.name}"
        assert '"additionalProperties": false' not in raw_text, f"Forbidden additionalProperties: false in {sf.name}"

    pairs = [
        ("constitution.yaml", "constitution.schema.json"),
        ("grounding_domains.yaml", "grounding_domains.schema.json"),
        ("dynamic_questioning.yaml", "dynamic_questioning.schema.json"),
        ("brainstorming_intents.yaml", "brainstorming_intents.schema.json"),
        ("agents_catalog.yaml", "agents_catalog.schema.json"),
        ("routing_table.yaml", "routing_table.schema.json"),
    ]
    for gp in sorted((SOURCE_DIR / "profiles").glob("gp_*.yaml")):
        pairs.append((gp.name, "guardian_profile.schema.json"))

    assert len(pairs) == 20, f"Expected 6 catalogs + 14 lenses = 20 YAML files, got {len(pairs)}"

    for yaml_name, schema_name in pairs:
        y_data = yaml.safe_load((SOURCE_DIR / "profiles" / yaml_name).read_text(encoding="utf-8"))
        s_data = json.loads((schemas_dir / schema_name).read_text(encoding="utf-8"))
        jsonschema.validate(instance=y_data, schema=s_data)


def test_all_cli_entrypoints_support_help_flag():
    """
    Verifica a conformidade com P10: todos os entrypoints CLI Python e Bash respondem a --help com exit code 0.
    """
    python_clis = [
        SOURCE_SRC / "kit_env_bootstrap.py",
        SOURCE_SRC / "vitalia_hook_runner.py",
        SOURCE_SRC / "vitalia_context_engine.py",
        SOURCE_SRC / "vitalia_handoff.py",
        SOURCE_SRC / "hooks" / "scan_environment.py",
        SOURCE_SRC / "hooks" / "guardian_context.py",
        SOURCE_SRC / "rendering" / "constitution_renderer.py",
    ]
    for script in python_clis:
        res = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
        assert res.returncode == 0, f"{script.name} --help failed: {res.stderr}"
        assert "usage:" in res.stdout.lower()

    bash_clis = [
        REPO_ROOT / "kit-bootstrap.sh",
        SOURCE_DIR / "bin" / "install-project",
    ]
    for bscript in bash_clis:
        res = subprocess.run([str(bscript), "--help"], capture_output=True, text=True)
        assert res.returncode == 0, f"{bscript.name} --help failed: {res.stderr}"
        assert "uso:" in res.stdout.lower()
