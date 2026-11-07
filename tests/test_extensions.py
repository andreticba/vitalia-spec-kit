# test_extensions.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import os
import pytest
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
EXT_DIR = REPO_ROOT / "source" / "extensions"

EXPECTED_EXTENSIONS = [
    "analyze.toml",
    "architect.toml",
    "brainstorming.toml",
    "converge.toml",
    "judge.toml",
    "route.toml",
    "session-consolidate.toml",
    "session-end.toml",
    "session-start.toml",
    "spec-implement.toml",
    "spec-plan.toml",
    "spec-specify.toml",
    "spec-tasks.toml",
]

def test_all_13_canonical_extensions_exist():
    """Valida se todas as 13 extensões canônicas estão presentes."""
    present = [f.name for f in EXT_DIR.glob("*.toml")]
    for expected in EXPECTED_EXTENSIONS:
        assert expected in present, f"Extensão canônica faltante: {expected}"
    assert len(present) == 13, f"Devem existir exatamente 13 extensões, mas foram encontradas {len(present)}"

def test_all_extensions_parse_and_conform():
    """Valida sintaxe TOML e regras de governança da Spec 002."""
    for toml_path in EXT_DIR.glob("*.toml"):
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)

        assert "meta" in data, f"{toml_path.name} deve ter seção [meta]"
        assert data["meta"].get("version") == "0.0.1", f"{toml_path.name} deve declarar version = '0.0.1'"
        assert "hardware_profile" not in data["meta"], f"{toml_path.name} não deve ter hardware_profile"

        # Se houver seção transport
        if "transport" in data:
            assert data["transport"].get("preferred") != "redis", f"{toml_path.name} não deve usar preferred = 'redis'"
            assert "redis_key" not in data["transport"], f"{toml_path.name} não deve declarar redis_key"
