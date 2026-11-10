# test_hook_runner_clean.py | Vitalia SDD v0.6.0 | 10-11-2026 15:55(GMT-04:00)
import json
import subprocess
import sys
from pathlib import Path
import pytest

src_dir = Path(__file__).resolve().parent.parent / "src"
ext_dir = Path(__file__).resolve().parent.parent / "extensions"


def test_hook_runner_no_tmp_cleanup_matrix_in_context(tmp_path):
    """
    [TEST:BUGFIX] Cenário de Falsificação:
    Falha se vitalia_hook_runner.py injetar a chave 'tmp_cleanup_matrix'
    ou prompts interativos de expurgo no payload guardian_json.
    """
    toml_path = ext_dir / "spec-specify.toml"
    assert toml_path.exists(), f"Arquivo {toml_path} não encontrado"

    hook_runner_path = src_dir / "vitalia_hook_runner.py"

    # Executar hook runner
    res = subprocess.run(
        [sys.executable, str(hook_runner_path), str(toml_path), "--phase", "none"],
        capture_output=True,
        text=True,
        cwd=str(Path.cwd()),
    )
    assert res.returncode == 0, f"Falha na execução do hook runner: {res.stderr}"

    stub = json.loads(res.stdout)
    assert stub["status"] == "ready"
    context_file = Path(stub["workflow_context_file"])
    assert context_file.exists()

    payload = json.loads(context_file.read_text(encoding="utf-8"))
    guardian_json = payload.get("guardian_json", {})

    # Asserções anti-sequestro de atenção (P00/P12)
    assert "tmp_cleanup_matrix" not in guardian_json, "tmp_cleanup_matrix NÃO deve constar em guardian_json"
    assert "tmp_cleanup_matrix" not in payload, "tmp_cleanup_matrix NÃO deve constar no envelope"

    raw_text = context_file.read_text(encoding="utf-8")
    assert "[a/d/n/t]" not in raw_text, "Menu interativo temporário [a/d/n/t] não deve poluir o contexto"

