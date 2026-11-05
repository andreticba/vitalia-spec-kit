# test_hook_runner.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
import os
import sys
import json
import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_RUNNER_SCRIPT = REPO_ROOT / "source" / "src" / "vitalia_hook_runner.py"
SAMPLE_TOML = REPO_ROOT / "source" / "extensions" / "brainstorming.toml"

def test_hook_runner_script_exists():
    """Valida se o script vitalia_hook_runner.py existe na topologia source/src/."""
    assert HOOK_RUNNER_SCRIPT.exists(), "source/src/vitalia_hook_runner.py deve existir"

def test_hook_runner_purged_redis_calls():
    """Valida que chamadas e imports a Redis e portas 6379 foram purgados."""
    content = HOOK_RUNNER_SCRIPT.read_text(encoding="utf-8")
    assert "redis.from_url" not in content, "Chamadas a cliente redis devem ser purgadas"
    assert "6379" not in content, "Porta 6379 (Redis) deve ser purgada de vitalia_hook_runner"
    assert "xadd" not in content, "Telemetria Redis Streams (xadd) deve ser purgada"

def test_hook_runner_context_lifting_saves_in_local_project_storage(tmp_path):
    """
    Valida que o Context Lifting persiste o arquivo de contexto estritamente em
    <project_root>/.vitalia/memory/data_storage/context/ e NÃO em /tmp/ global.
    """
    test_project = tmp_path / "app_project"
    test_project.mkdir()
    (test_project / ".vitalia").mkdir()
    (test_project / ".vitalia" / "memory").mkdir()

    # Cria um toml de teste mínimo
    dummy_toml = test_project / "test_workflow.toml"
    dummy_toml.write_text("""
[meta]
title = "Workflow de Teste"

[prompt]
instruction = "Instrução de teste para a IA"
""", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(HOOK_RUNNER_SCRIPT), str(dummy_toml), "--phase", "none"],
        cwd=str(test_project),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"Hook runner falhou: {result.stderr}\nStdout: {result.stdout}"

    stub = json.loads(result.stdout)
    assert stub.get("status") == "ready"
    assert "workflow_context_file" in stub

    context_file_path = Path(stub["workflow_context_file"])
    assert context_file_path.exists(), f"Arquivo de contexto referenciado {context_file_path} deve existir"

    # Validação de Zero Data Leak: deve estar dentro de .vitalia/memory/data_storage/context/
    expected_storage_dir = test_project / ".vitalia" / "memory" / "data_storage" / "context"
    assert str(expected_storage_dir) in str(context_file_path), (
        f"Contexto deve ser salvo dentro de {expected_storage_dir}, mas foi em {context_file_path}"
    )

    # Valida estrutura do arquivo gerado
    context_data = json.loads(context_file_path.read_text(encoding="utf-8"))
    assert "workflow" in context_data
    assert "timestamp" in context_data
    assert "machine_id" in context_data
    assert "prompt" in context_data
    # Valida partição determinística de pasta por machine_id
    assert context_file_path.parent.name == context_data["machine_id"]
