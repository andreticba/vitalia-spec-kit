# test_sensor_contract_dbc.py | Vitalia SDD v0.6.0 | 10-11-2026 16:35(GMT-04:00)
import subprocess
import sys
from pathlib import Path
import pytest

sensors_dir = Path(__file__).resolve().parent.parent / "src" / "sensors"
dbc_script = sensors_dir / "sensor_contract_dbc.py"


def test_sensor_contract_dbc_validates_workflow_contracts(tmp_path):
    """
    [TEST:NEW] Cenário de Falsificação:
    Falha se o sensor aprovar uma extensão TOML de workflow
    que omita blocos mandatórios de contrato DbC (meta, tools, context, transport, guardian).
    """
    assert dbc_script.exists(), f"Sensor {dbc_script} deve existir"

    ext_dir = tmp_path / "mock_extensions"
    ext_dir.mkdir()

    # 1. Caso Válido: workflow completo com DbC
    valid_toml = (
        'description = "Workflow demo"\n\n'
        '[meta]\nversion = "0.0.1"\nhardware_profile = "frontier"\n\n'
        '[tools]\nrequired = ["read_file", "write_file"]\n\n'
        '[context]\nreads = ["specs/*"]\nwrites = ["specs/*"]\n\n'
        '[transport]\npreferred = "filesystem"\n\n'
        '[guardian]\nyaml_sources = ["constitution"]\nguardian_profile = "gp_test"\nprompt = "Missao"\n'
    )
    (ext_dir / "valid.toml").write_text(valid_toml, encoding="utf-8")

    res_valid = subprocess.run(
        [sys.executable, str(dbc_script), "--extensions-dir", str(ext_dir)],
        capture_output=True,
        text=True,
    )
    assert res_valid.returncode == 0, f"Deveria passar com contrato completo: {res_valid.stderr}"

    # 2. Injeção de Anomalia: workflow quebrado sem bloco [tools] e [guardian]
    invalid_toml = 'description = "Broken workflow"\n[meta]\nversion = "0.0.1"\n'
    (ext_dir / "invalid.toml").write_text(invalid_toml, encoding="utf-8")

    res_invalid = subprocess.run(
        [sys.executable, str(dbc_script), "--extensions-dir", str(ext_dir)],
        capture_output=True,
        text=True,
    )
    assert res_invalid.returncode != 0, "Sensor deve falhar com workflow incompleto"
    assert "invalid.toml" in res_invalid.stdout

