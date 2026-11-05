# test_guardian.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import os
import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUARDIAN_SCRIPT = REPO_ROOT / "source" / "src" / "hooks" / "guardian_context.py"

def test_guardian_script_exists():
    """Valida se guardian_context.py existe em source/src/hooks/."""
    assert GUARDIAN_SCRIPT.exists(), "source/src/hooks/guardian_context.py deve existir"

def test_guardian_purged_redis():
    """Valida que o Guardian não tenta se conectar ao Redis nem porta 6379."""
    content = GUARDIAN_SCRIPT.read_text(encoding="utf-8")
    assert "redis.from_url" not in content, "Chamadas a cliente redis devem ser purgadas"
    assert "6379" not in content, "Porta 6379 deve ser purgada"

def test_guardian_injects_full_constitution_without_pruning(tmp_path):
    """
    Valida que GuardianContextV2 injeta a constituição de forma integral (P00 a P17)
    sem aplicar cortes ou podas de tokens.
    """
    sys.path.insert(0, str(REPO_ROOT / "source" / "src"))
    from hooks.guardian_context import GuardianContextV2  # type: ignore

    guardian = GuardianContextV2(
        workflow_name="test_workflow",
        guardian_config={"guardian_profile": "gp_sdd-judge"},
        cwd=REPO_ROOT
    )
    payload = guardian.build_payload()

    assert "sources" in payload
    sources = payload["sources"]
    assert "constitution" in sources, "Constituição deve ser injetada"

    const_data = sources["constitution"]
    principles = const_data.get("principles", {})
    # Deve conter todos os 18 princípios (P00 a P17)
    for i in range(18):
        p_id = f"P{i:02d}"
        assert p_id in principles, f"Princípio {p_id} deve estar presente integralmente sem podas"

    assert payload.get("pruning_applied") is False
