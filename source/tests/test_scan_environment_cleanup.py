# test_scan_environment_cleanup.py | Vitalia SPEC Kit v0.0.1 | 15-11-2026 13:58(GMT-04:00)
import json
import subprocess
import sys
import jsonschema
from pathlib import Path
import pytest

hooks_dir = Path(__file__).resolve().parent.parent / "src" / "hooks"
scan_script = hooks_dir / "scan_environment.py"
contracts_dir = Path(__file__).resolve().parent.parent.parent / "specs" / "007-fix-context-cleanup-cli-and-session-health" / "contracts"
schema_file = contracts_dir / "context_cleanup.schema.json"


def test_scan_environment_emits_context_cleanup_node(mock_context_tree):
    """
    T010 [TEST:BUGFIX] Cenário de Falsificação:
    O teste DEVE FALHAR contra o sensor atual que não emite o nó 'context_cleanup'
    na saída JSON do scan_environment.py ou emite fora do contrato OpenAPI 3.0 Limpo.
    """
    root = mock_context_tree["root"]

    res = subprocess.run(
        [sys.executable, str(scan_script), "--cwd", str(root)],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Falha ao executar scan_environment: {res.stderr}"

    data = json.loads(res.stdout)
    assert "context_cleanup" in data, "O nó 'context_cleanup' deve estar presente na saída JSON"

    cleanup_node = data["context_cleanup"]

    # 1. Validação estrita de schema OpenAPI 3.0 Limpo
    assert schema_file.exists(), f"Schema {schema_file} deve existir"
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    jsonschema.validate(instance=cleanup_node, schema=schema)

    # 2. Validação dos valores computados
    # No mock_context_tree temos 5 arquivos no total, sendo 2 de hoje e 3 do passado
    assert cleanup_node["total_files"] == 5
    assert cleanup_node["eligible_files"] == 3
    assert cleanup_node["eligible_bytes"] > 0
    assert cleanup_node["needs_cleanup"] is True
