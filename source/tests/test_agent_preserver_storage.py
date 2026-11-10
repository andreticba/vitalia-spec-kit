# test_agent_preserver_storage.py | Vitalia SDD v0.6.0 | 10-11-2026 16:40(GMT-04:00)
import subprocess
from pathlib import Path
import pytest

script_path = Path(__file__).resolve().parent.parent / "bin" / "lib" / "agent_preserver.sh"


def test_agent_preserver_persists_strictly_in_data_storage_layer(tmp_path):
    """
    [TEST:MIGRATION] Cenário de Falsificação:
    Falha se agent_preserver.sh criar manifesto na raiz de .vitalia/
    ou gravar backups fora de .vitalia/memory/data_storage/.
    """
    assert script_path.exists(), f"{script_path} deve existir"

    proj_dir = tmp_path / "mock_project"
    proj_dir.mkdir()
    vitalia_dir = proj_dir / ".vitalia"
    vitalia_dir.mkdir()
    skills_dir = proj_dir / ".agents" / "skills"
    skills_dir.mkdir(parents=True)

    # Executar script chamando update_skill
    cmd = f"""
    source "{script_path}"
    update_skill "demo-skill" "---\\nname: demo-skill\\ndescription: Teste\\n---\\n# Content" "{skills_dir}" "{vitalia_dir}"
    """

    res = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
    assert res.returncode == 0, f"Falha na execução do script: {res.stderr}"

    # Asserções de pureza arquitetural da Camada 4
    polluted_manifest = vitalia_dir / ".vitalia-manifest"
    assert not polluted_manifest.exists(), "Manifesto não deve residir na raiz de .vitalia/"

    polluted_backups = vitalia_dir / "backups"
    assert not polluted_backups.exists(), "Backups não devem residir na raiz de .vitalia/"

    # Verificar caminhos canônicos da Camada 4
    canonical_manifest = vitalia_dir / "memory" / "data_storage" / "manifests" / ".vitalia-manifest"
    assert canonical_manifest.exists(), f"Manifesto canônico deve existir em {canonical_manifest}"

