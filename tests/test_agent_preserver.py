# test_agent_preserver.py | Vitalia SPEC Kit v0.0.1 | 11-11-2026 22:00(GMT-04:00)
"""
Testes de idempotência e preservação não-destrutiva de AGENTS.md (T002 / FR-002.5).
Cenário de Falsificação (P05): Falha se invocar a atualização de AGENTS.md sobre um arquivo
com blocos repetidos, marcadores órfãos ou execuções repetidas não resultar em exatamente 1
único bloco delimitado por START_MARKER e END_MARKER, preservando regras do usuário.
"""

from pathlib import Path
import subprocess
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PRESERVER_SCRIPT = REPO_ROOT / "source" / "bin" / "lib" / "agent_preserver.sh"

START_MARKER = "<!-- VITALIA:KIT:START -->"
END_MARKER = "<!-- VITALIA:KIT:END -->"


def run_update_agents_md(target_file: Path, kit_content: str, backups_dir: Path) -> subprocess.CompletedProcess:
    bash_code = f"""
    source "{PRESERVER_SCRIPT}"
    update_agents_md "{target_file}" "{kit_content}" "{backups_dir}"
    """
    return subprocess.run(
        ["bash", "-c", bash_code],
        capture_output=True,
        text=True,
        check=False
    )


def test_idempotent_single_block_when_clean(tmp_path):
    """
    Atualizar um arquivo novo deve criar exatamente um bloco.
    """
    target = tmp_path / "AGENTS.md"
    backups = tmp_path / "backups"
    kit_content = "# Bloco Vitalia Inicial\nRegra 1"

    res = run_update_agents_md(target, kit_content, backups)
    assert res.returncode == 0
    content = target.read_text(encoding="utf-8")

    assert content.count(START_MARKER) == 1
    assert content.count(END_MARKER) == 1
    assert "Regra 1" in content


def test_deduplication_of_repeated_blocks(tmp_path):
    """
    FR-002.5: Se o arquivo alvo contiver blocos duplicados ou repetidos
    (como ocorreu na anomalia de 107 linhas), a atualização deve expurgar
    as repetições e manter estritamente 1 único bloco do Kit.
    """
    target = tmp_path / "AGENTS.md"
    backups = tmp_path / "backups"

    # Simula arquivo corrompido com blocos duplicados e regra do usuário
    duplicated_content = f"""# Regras do Projeto Usuário (Topo)

{START_MARKER}
Bloco 1 Duplicado Antigo
{END_MARKER}

{START_MARKER}
Bloco 2 Duplicado Antigo
{END_MARKER}

# Regras Customizadas do Usuário (Rodapé)
- Sempre responder em português.
"""
    target.write_text(duplicated_content, encoding="utf-8")

    new_kit_content = "Bloco Vitalia Novo Sanitizado"
    res = run_update_agents_md(target, new_kit_content, backups)
    assert res.returncode == 0

    result_content = target.read_text(encoding="utf-8")

    # Cenário de Falsificação: Falha se houver mais de 1 bloco de marcadores
    assert result_content.count(START_MARKER) == 1, (
        f"Cenário de Falsificação atingido: encontrado {result_content.count(START_MARKER)} START_MARKER (esperado 1)."
    )
    assert result_content.count(END_MARKER) == 1, (
        f"Cenário de Falsificação atingido: encontrado {result_content.count(END_MARKER)} END_MARKER (esperado 1)."
    )
    assert "Bloco Vitalia Novo Sanitizado" in result_content
    assert "Bloco 1 Duplicado Antigo" not in result_content
    assert "Bloco 2 Duplicado Antigo" not in result_content
    assert "Sempre responder em português." in result_content


def test_sequential_updates_are_strictly_idempotent(tmp_path):
    """
    Invocar update_agents_md 3 vezes sucessivas com conteúdos diferentes
    deve atualizar o bloco sem nunca duplicar ou acumular marcadores.
    """
    target = tmp_path / "AGENTS.md"
    backups = tmp_path / "backups"
    target.write_text("# Custom User Rule\n", encoding="utf-8")

    for i in range(1, 4):
        kit_content = f"Versao Kit {i}"
        res = run_update_agents_md(target, kit_content, backups)
        assert res.returncode == 0

        content = target.read_text(encoding="utf-8")
        assert content.count(START_MARKER) == 1
        assert content.count(END_MARKER) == 1
        assert f"Versao Kit {i}" in content
        assert "Custom User Rule" in content

