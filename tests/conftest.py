# conftest.py | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:07(GMT-04:00)
"""
Fixtures globais para a suíte de testes do Vitalia SPEC Kit.
Inclui suporte à simulação de restrição de sandbox da IDE Antigravity (T002).
"""

import os
from pathlib import Path
import pytest


@pytest.fixture
def mock_antigravity_sandbox(monkeypatch, tmp_path):
    """
    Simula o ambiente de sandbox restrito da IDE Antigravity.
    Quando ativo, comandos que tentam resolver interpretadores fora do workspace
    sem elevação (BypassSandbox: true) simulam comportamento hostil ou erro de permissão.
    """
    workspace = tmp_path / "sandbox_workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ANTIGRAVITY_SANDBOX", "strict")
    monkeypatch.setenv("WORKSPACE_DIR", str(workspace))
    return workspace

