# test_sensor_tokens_leak.py | Vitalia SDD v0.6.0 | 10-11-2026 16:30(GMT-04:00)
import json
import subprocess
import sys
from pathlib import Path
import pytest

sensors_dir = Path(__file__).resolve().parent.parent / "src" / "sensors"
tokens_script = sensors_dir / "sensor_tokens_leak.py"


def test_sensor_tokens_leak_detects_credentials_and_leaks(tmp_path):
    """
    [TEST:NEW] Cenário de Falsificação:
    Falha se o sensor retornar 0 quando houver arquivos de contexto
    contendo chaves privadas, tokens de API ou credenciais em texto puro.
    """
    assert tokens_script.exists(), f"Sensor {tokens_script} deve existir"

    context_dir = tmp_path / "mock_context"
    context_dir.mkdir()

    # 1. Caso Limpo: sem segredos
    clean_file = context_dir / "clean_context.json"
    clean_file.write_text(json.dumps({"token_budget": 0, "status": "HEALTHY"}), encoding="utf-8")

    res_clean = subprocess.run(
        [sys.executable, str(tokens_script), "--context-dir", str(context_dir)],
        capture_output=True,
        text=True,
    )
    assert res_clean.returncode == 0, f"Deveria passar com contexto limpo: {res_clean.stderr}"

    # 2. Injeção de Anomalia: chave de API exposta
    dirty_file = context_dir / "dirty_context.json"
    dirty_file.write_text(json.dumps({"api_key": "sk_live_1234567890abcdef"}), encoding="utf-8")

    res_dirty = subprocess.run(
        [sys.executable, str(tokens_script), "--context-dir", str(context_dir)],
        capture_output=True,
        text=True,
    )
    assert res_dirty.returncode != 0, "Sensor deve falhar ao detectar credencial exposta"
    assert "sk_live_" in res_dirty.stdout or "segredo" in res_dirty.stdout.lower()

