# test_kit_env_bootstrap.py | Vitalia SDD v0.6.0 | 10-11-2026 15:45(GMT-04:00)
import os
import sys
from pathlib import Path
import pytest

# Adicionar source/src ao path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import kit_env_bootstrap


def test_resolve_kit_dir_fallback_on_nonexistent_path(monkeypatch, tmp_path):
    """
    [TEST:BUGFIX] Cenário de Falsificação:
    Configurar VITALIA_KIT_DIR para um caminho inexistente em disco.
    O teste DEVE FALHAR se resolve_kit_dir retornar o caminho inexistente
    ou lançar exceção ao invés de realizar fallback defensivo para um diretório
    que comprovadamente exista fisicamente em disco.
    """
    fake_dir = tmp_path / "diretorio_inexistente_12345"
    assert not fake_dir.exists()

    monkeypatch.setenv("VITALIA_KIT_DIR", str(fake_dir))

    resolved = kit_env_bootstrap.resolve_kit_dir(project_root=tmp_path)

    # Asserção comportamental de caixa-preta:
    # O diretório retornado DEVE existir fisicamente em disco
    assert resolved.exists(), f"Diretório resolvido não existe em disco: {resolved}"
    assert resolved != fake_dir, f"resolve_kit_dir adotou caminho inexistente {fake_dir} sem fallback defensivo"

