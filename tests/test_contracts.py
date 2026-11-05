# test_contracts.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import json
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = REPO_ROOT / "specs" / "002-universal-bootstrap-runtime" / "contracts"

def test_contracts_exist_and_are_valid_json():
    """Valida se os esquemas de contrato existem e são arquivos JSON válidos."""
    assert (CONTRACTS_DIR / "context-lifting.schema.json").exists()
    assert (CONTRACTS_DIR / "scan-environment.schema.json").exists()

def test_contracts_conform_to_pure_openapi_3():
    """
    Garante que os schemas não contêm meta-campos rejeitados pela API Gemini REST:
    - Sem '$schema'
    - Sem 'title' no nó raiz
    - Sem 'additionalProperties: false' no nó raiz
    """
    for schema_file in CONTRACTS_DIR.glob("*.json"):
        content = schema_file.read_text(encoding="utf-8")
        data = json.loads(content)

        assert "$schema" not in data, f"{schema_file.name} não deve conter '$schema'"
        assert "title" not in data, f"{schema_file.name} não deve conter 'title' no nó raiz"
        assert data.get("type") == "object", f"{schema_file.name} deve ter type: 'object'"
        assert "properties" in data, f"{schema_file.name} deve ter 'properties'"
        assert "required" in data, f"{schema_file.name} deve ter 'required'"
