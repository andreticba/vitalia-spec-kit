# test_sensor_path_hygiene.py | Vitalia SDD v0.6.0 | 10-11-2026 16:20(GMT-04:00)
import subprocess
import sys
from pathlib import Path
import pytest

sensors_dir = Path(__file__).resolve().parent.parent / "src" / "sensors"
hygiene_script = sensors_dir / "sensor_path_hygiene.py"


def test_sensor_path_hygiene_detects_hardcoded_paths(tmp_path):
    """
    [TEST:NEW] Cenário de Falsificação:
    Falha se o sensor retornar 0 quando houver arquivos de código ou scripts
    contendo strings hardcoded como '/home/andre/.vitalia' ou 'source/' fora de comentários permitidos.
    """
    assert hygiene_script.exists(), f"Sensor {hygiene_script} deve existir"

    scan_dir = tmp_path / "mock_source"
    scan_dir.mkdir()

    # 1. Arquivo limpo: usa VITALIA_KIT_DIR e resolve_kit_dir
    clean_file = scan_dir / "clean_code.py"
    clean_file.write_text("import os\nkit_dir = os.environ.get('VITALIA_KIT_DIR')\n", encoding="utf-8")

    res_clean = subprocess.run(
        [sys.executable, str(hygiene_script), "--scan-dir", str(scan_dir)],
        capture_output=True,
        text=True,
    )
    assert res_clean.returncode == 0, f"Deveria passar com código limpo: {res_clean.stderr}"

    # 2. Injeção de Anomalia: caminho hardcoded
    dirty_file = scan_dir / "dirty_code.py"
    dirty_file.write_text("kit_path = '/home/andre/.vitalia/extensions'\n", encoding="utf-8")

    res_dirty = subprocess.run(
        [sys.executable, str(hygiene_script), "--scan-dir", str(scan_dir)],
        capture_output=True,
        text=True,
    )
    assert res_dirty.returncode != 0, "Sensor deve falhar ao detectar caminho hardcoded local"
    assert "dirty_code.py" in res_dirty.stdout

