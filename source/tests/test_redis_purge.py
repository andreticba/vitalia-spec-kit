# test_redis_purge.py | Vitalia SDD v0.6.0 | 10-11-2026 15:50(GMT-04:00)
import socket
import sys
from pathlib import Path
import pytest

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import kit_env_bootstrap
from hooks import scan_environment


def test_redis_clean_purge_and_zero_network_probes(monkeypatch, tmp_path):
    """
    [TEST:MIGRATION] Cenário de Falsificação:
    Falha se kit_env_bootstrap ou scan_environment tentarem abrir socket
    na porta 6379 (Redis) ou reportarem status DEGRADED por ausência de Redis.
    """
    # Criar raiz simulada de projeto com .env
    proj_root = tmp_path / "mock_project"
    proj_root.mkdir()
    (proj_root / ".env").write_text("VITALIA_MACHINE_NAME=test_host\n", encoding="utf-8")

    # Monitor de conexões de socket: bloquear e falhar se tentar conectar na 6379
    original_connect = socket.socket.connect

    def guarded_connect(self, address):
        host, port = address[0], address[1]
        if port == 6379:
            pytest.fail("VIOLAÇÃO: Tentativa de conexão probe na porta 6379 do Redis detectada!")
        return original_connect(self, address)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)

    # Executar diagnóstico
    health = kit_env_bootstrap.init(proj_root)

    # Asserções de caixa-preta
    assert health["status"] == "HEALTHY", f"Status não saudável: {health}"
    assert "redis" not in sys.modules, "Módulo redis não deve ser importado pelo kit em filesystem puro"
    assert "redis" not in [issue.lower() for issue in health.get("issues", [])]

