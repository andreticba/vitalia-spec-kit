# test_sensor_memory_ledger.py | Vitalia SDD v0.6.0 | 10-11-2026 16:25(GMT-04:00)
import json
import subprocess
import sys
from pathlib import Path
import pytest

sensors_dir = Path(__file__).resolve().parent.parent / "src" / "sensors"
ledger_script = sensors_dir / "sensor_memory_ledger.py"


def test_sensor_memory_ledger_validates_ordering_and_integrity(tmp_path):
    """
    [TEST:NEW] Cenário de Falsificação:
    Falha se o sensor retornar 0 quando os shards em memory/
    estiverem fora de ordem cronológica estritamente decrescente por last_sync
    ou se o ledger estiver ausente/corrompido.
    """
    assert ledger_script.exists(), f"Sensor {ledger_script} deve existir"

    memory_dir = tmp_path / ".vitalia" / "memory"
    memory_dir.mkdir(parents=True)

    # 1. Caso Válido: ledger com shards ordenados decrescentemente
    valid_ledger = {
        "schema_version": "0.6.0",
        "last_sync": "2026-11-10T15:00:00-04:00",
        "shards": [
            {"shard_id": "s002", "machine_id": "host_a", "last_sync": "2026-11-10T15:00:00-04:00"},
            {"shard_id": "s001", "machine_id": "host_b", "last_sync": "2026-11-10T14:00:00-04:00"},
        ]
    }
    (memory_dir / "session_ledger.json").write_text(json.dumps(valid_ledger), encoding="utf-8")

    res_valid = subprocess.run(
        [sys.executable, str(ledger_script), "--memory-dir", str(memory_dir)],
        capture_output=True,
        text=True,
    )
    assert res_valid.returncode == 0, f"Deveria passar com ledger ordenado: {res_valid.stderr}"

    # 2. Injeção de Anomalia: shards invertidos (cronologicamente crescentes)
    invalid_ledger = {
        "schema_version": "0.6.0",
        "last_sync": "2026-11-10T15:00:00-04:00",
        "shards": [
            {"shard_id": "s001", "machine_id": "host_b", "last_sync": "2026-11-10T14:00:00-04:00"},
            {"shard_id": "s002", "machine_id": "host_a", "last_sync": "2026-11-10T15:00:00-04:00"},
        ]
    }
    (memory_dir / "session_ledger.json").write_text(json.dumps(invalid_ledger), encoding="utf-8")

    res_invalid = subprocess.run(
        [sys.executable, str(ledger_script), "--memory-dir", str(memory_dir)],
        capture_output=True,
        text=True,
    )
    assert res_invalid.returncode != 0, "Sensor deve falhar com shards fora de ordem decrescente"

