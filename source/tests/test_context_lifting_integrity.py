# test_context_lifting_integrity.py | Vitalia SDD v0.6.0 | 10-11-2026 16:05(GMT-04:00)
import json
import subprocess
import sys
from pathlib import Path
import pytest

src_dir = Path(__file__).resolve().parent.parent / "src"
ext_dir = Path(__file__).resolve().parent.parent / "extensions"
schema_path = src_dir / "schemas" / "context_payload.json"


def test_context_lifting_schema_and_constitution_integral(tmp_path):
    """
    [TEST:MIGRATION] Cenário de Falsificação:
    Falha se o arquivo de contexto transitório gerado em data_storage/context/
    violar o schema OpenAPI 3.0 limpo (sem $schema, sem title raiz)
    ou se omitir princípios invioláveis da Constituição (P00 a P17).
    """
    assert schema_path.exists(), f"Schema {schema_path} não encontrado"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    # Validar pureza OpenAPI 3.0 do próprio schema
    assert "$schema" not in schema
    assert "title" not in schema
    assert schema.get("additionalProperties") is not False

    # Executar hook runner para gerar contexto
    hook_runner = src_dir / "vitalia_hook_runner.py"
    toml_file = ext_dir / "spec-specify.toml"

    res = subprocess.run(
        [sys.executable, str(hook_runner), str(toml_file), "--phase", "none"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Hook runner falhou: {res.stderr}"

    stub = json.loads(res.stdout)
    context_file = Path(stub["workflow_context_file"])
    assert context_file.exists()

    payload = json.loads(context_file.read_text(encoding="utf-8"))

    # Validar campos requeridos pelo schema
    for req_field in schema.get("required", []):
        assert req_field in payload, f"Campo mandatório ausente no payload: {req_field}"

    # Validar presença integral dos princípios constitucionais (Sem Poda)
    guardian_json = payload["guardian_json"]
    principles = guardian_json.get("sources", {}).get("constitution", {}).get("principles", {})
    assert len(principles) >= 14, f"Constituição foi podada indevidamente: {len(principles)} princípios"

    # Verificar princípios fundamentais
    for p in ["P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P11"]:
        assert p in principles, f"Princípio mandatório {p} ausente do payload Guardian!"

