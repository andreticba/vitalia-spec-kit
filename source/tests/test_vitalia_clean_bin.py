# test_vitalia_clean_bin.py | Vitalia SPEC Kit v0.0.1 | 15-11-2026 13:59(GMT-04:00)
import os
import subprocess
from pathlib import Path
import pytest

bin_dir = Path(__file__).resolve().parent.parent / "bin"
clean_bin = bin_dir / "vitalia-clean"


def test_vitalia_clean_shim_execution(mock_context_tree):
    """
    T015 [TEST:NEW] Cenário de Falsificação:
    O teste falha se o script shim não for executável, não existir, ou não
    repassar argumentos corretamente para o utilitário Python subjacente.
    """
    assert clean_bin.exists(), f"Binário {clean_bin} deve existir"
    assert os.access(clean_bin, os.X_OK), f"Binário {clean_bin} deve ter permissão de execução (+x)"

    # 1. Teste de repasse de argumentos (--help)
    res_help = subprocess.run(
        [str(clean_bin), "--help"],
        capture_output=True,
        text=True,
    )
    assert res_help.returncode == 0
    assert "Exemplos" in res_help.stdout or "uso" in res_help.stdout.lower()

    # 2. Teste de execução com --dry-run e --target-dir
    root = mock_context_tree["root"]
    res_dry = subprocess.run(
        [str(clean_bin), "--target-dir", str(root), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert res_dry.returncode == 0
    assert "DRY-RUN" in res_dry.stdout or "simulação" in res_dry.stdout.lower()
    assert "preservada" in res_dry.stdout.lower() or "hoje" in res_dry.stdout.lower()
