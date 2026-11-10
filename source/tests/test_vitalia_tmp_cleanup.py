# test_vitalia_tmp_cleanup.py | Vitalia SDD v0.6.0 | 10-11-2026 15:58(GMT-04:00)
import subprocess
import sys
from pathlib import Path
import pytest

src_dir = Path(__file__).resolve().parent.parent / "src"
cleanup_script = src_dir / "vitalia_tmp_cleanup.py"


def test_vitalia_tmp_cleanup_cli_behavior(tmp_path):
    """
    [TEST:NEW] Cenário de Falsificação:
    Falha se o script não existir, não tiver flag --help didática,
    não suportar --dry-run ou não limpar arquivos temporários expirados quando invocado.
    """
    assert cleanup_script.exists(), f"Script {cleanup_script} deve existir"

    # 1. Teste da flag didática --help (P10)
    res_help = subprocess.run(
        [sys.executable, str(cleanup_script), "--help"],
        capture_output=True,
        text=True,
    )
    assert res_help.returncode == 0
    assert "Exemplos" in res_help.stdout or "uso" in res_help.stdout.lower()

    # 2. Criar mock de arquivos temporários em tmp_path
    context_dir = tmp_path / ".vitalia" / "memory" / "data_storage" / "context"
    context_dir.mkdir(parents=True)
    temp_file = context_dir / "old_context_123.json"
    temp_file.write_text("{}", encoding="utf-8")

    # 3. Teste em modo --dry-run
    res_dry = subprocess.run(
        [sys.executable, str(cleanup_script), "--target-dir", str(tmp_path), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert res_dry.returncode == 0
    assert temp_file.exists(), "Dry-run não deve deletar arquivos físicos"

    # 4. Teste em modo de execução real (--force)
    res_clean = subprocess.run(
        [sys.executable, str(cleanup_script), "--target-dir", str(tmp_path), "--force"],
        capture_output=True,
        text=True,
    )
    assert res_clean.returncode == 0
    assert not temp_file.exists(), "Execução real deve remover arquivos temporários limpos"

