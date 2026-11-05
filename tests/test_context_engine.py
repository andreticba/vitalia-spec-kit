# test_context_engine.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import os
import sys
import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / "source" / "src" / "vitalia_context_engine.py"

def test_context_engine_script_exists():
    """Valida se o script vitalia_context_engine.py existe em source/src/."""
    assert ENGINE_SCRIPT.exists(), "source/src/vitalia_context_engine.py deve existir"

def test_context_engine_purged_redis():
    """Valida que menções a Redis ou portas locais 6379 foram purgadas."""
    content = ENGINE_SCRIPT.read_text(encoding="utf-8")
    assert "redis.from_url" not in content
    assert "6379" not in content

def test_context_engine_filesystem_lifecycle(tmp_path):
    """Valida o ciclo de vida init -> shard -> consolidate em filesystem puro."""
    test_session = tmp_path / "memory_session"
    
    # 1. Action init
    res_init = subprocess.run(
        [sys.executable, str(ENGINE_SCRIPT), "--action", "init", "--session-dir", str(test_session)],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_init.returncode == 0, f"init falhou: {res_init.stderr}"
    assert (test_session / "shards").exists()
    assert (test_session / "data").exists()

    # 2. Action shard
    res_shard = subprocess.run(
        [
            sys.executable, str(ENGINE_SCRIPT),
            "--action", "shard",
            "--session-dir", str(test_session),
            "--task", "Feature 002",
            "--status", "Em Andamento",
            "--p0", "Executar TDD"
        ],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_shard.returncode == 0, f"shard falhou: {res_shard.stderr}"
    
    # Verifica que o shard foi gravado no filesystem
    shard_files = list((test_session / "shards").glob("*.json"))
    assert len(shard_files) > 0, "Pelo menos um shard deve ter sido gravado"

    # 3. Action consolidate
    res_cons = subprocess.run(
        [sys.executable, str(ENGINE_SCRIPT), "--action", "consolidate", "--session-dir", str(test_session)],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert res_cons.returncode == 0, f"consolidate falhou: {res_cons.stderr}"
    assert (test_session / "README.md").exists(), "README.md compilado deve existir"
