# test_vitalia_tmp_cleanup.py | Vitalia SPEC Kit v0.0.1 | 15-11-2026 13:57(GMT-04:00)
import subprocess
import sys
from pathlib import Path
import pytest

src_dir = Path(__file__).resolve().parent.parent / "src"
cleanup_script = src_dir / "vitalia_tmp_cleanup.py"


def test_cleanup_preserves_today_by_default(mock_context_tree):
    """
    T003 [TEST:BUGFIX] Cenário de Falsificação:
    O teste DEVE FALHAR contra a implementação legada que apaga arquivos de hoje
    indiscriminadamente quando invocado com --force ou no modo default [a].
    """
    root = mock_context_tree["root"]
    today_files = mock_context_tree["today_files"]
    past_files = mock_context_tree["past_files"]

    # Invoca com --force (equivalente à opção [a] não-interativa)
    res = subprocess.run(
        [sys.executable, str(cleanup_script), "--target-dir", str(root), "--force"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Falha na execução: {res.stderr}"

    # Invariante Constitucional P00/P05: Os arquivos de hoje DEVEM permanecer intactos!
    for tf in today_files:
        assert tf.exists(), f"VIOLAÇÃO CRÍTICA: Arquivo de hoje foi apagado indevidamente: {tf}"

    # Os arquivos passados devem ter sido removidos
    for pf in past_files:
        assert not pf.exists(), f"Arquivo do passado deveria ter sido removido: {pf}"


def test_cleanup_dry_run_leaves_all_files_intact(mock_context_tree):
    """
    T004 [TEST:BUGFIX] Cenário de Falsificação:
    O teste DEVE FALHAR se --dry-run remover qualquer arquivo ou não listar
    a data de hoje como preservada no output didático.
    """
    root = mock_context_tree["root"]
    today_files = mock_context_tree["today_files"]
    past_files = mock_context_tree["past_files"]

    res = subprocess.run(
        [sys.executable, str(cleanup_script), "--target-dir", str(root), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Falha no dry-run: {res.stderr}"
    assert "DRY-RUN" in res.stdout or "simulação" in res.stdout.lower()
    assert "hoje" in res.stdout.lower() or "preservada" in res.stdout.lower()

    # Nenhum arquivo pode ter sido deletado
    for f in today_files + past_files:
        assert f.exists(), f"Dry-run apagou arquivo indevidamente: {f}"


def test_cleanup_interactive_menu_options(mock_context_tree):
    """
    T005 [TEST:BUGFIX] Cenário de Falsificação:
    O teste DEVE FALHAR contra o código legado que não possui o menu interativo [a/d/n/t],
    não formata a saída com '📅 hoje', ou não suporta o cancelamento padrão no Enter [n].
    """
    root = mock_context_tree["root"]
    today_files = mock_context_tree["today_files"]
    past_files = mock_context_tree["past_files"]

    # Testa opção 'n' (ou Enter vazio): cancela e preserva tudo
    res_cancel = subprocess.run(
        [sys.executable, str(cleanup_script), "--target-dir", str(root)],
        input="\n",  # Enter direto (default n)
        capture_output=True,
        text=True,
    )
    assert res_cancel.returncode == 0
    assert "cancelada" in res_cancel.stdout.lower() or "nenhum" in res_cancel.stdout.lower()
    for f in today_files + past_files:
        assert f.exists(), f"Cancelamento apagou arquivo indevidamente: {f}"

    # Testa a presença do menu com formatação de hoje
    assert "📅 hoje" in res_cancel.stdout or "sessão ativa" in res_cancel.stdout


def test_cleanup_purge_all_with_affirmative_pattern(mock_context_tree):
    """
    T005b [TEST:BUGFIX] Cenário de Falsificação:
    O teste DEVE FALHAR se a flag --purge-all não exigir confirmação afirmativa
    ou se apagar os arquivos com confirmação 'n'.
    """
    root = mock_context_tree["root"]
    today_files = mock_context_tree["today_files"]
    past_files = mock_context_tree["past_files"]

    # 1. Purge all com recusa 'n' -> NÃO deve apagar nada
    res_refused = subprocess.run(
        [sys.executable, str(cleanup_script), "--target-dir", str(root), "--purge-all"],
        input="n\n",
        capture_output=True,
        text=True,
    )
    assert res_refused.returncode == 0
    for f in today_files + past_files:
        assert f.exists()

    # 2. Purge all com aceite 's' -> DEVE apagar tudo inclusive hoje
    res_accepted = subprocess.run(
        [sys.executable, str(cleanup_script), "--target-dir", str(root), "--purge-all"],
        input="s\n",
        capture_output=True,
        text=True,
    )
    assert res_accepted.returncode == 0
    for f in today_files + past_files:
        assert not f.exists()


def test_cleanup_interactive_date_selection_range(mock_context_tree):
    """
    T008 [TEST:BUGFIX] Testa a seleção de datas específicas [d] com sintaxe de faixas.
    """
    root = mock_context_tree["root"]
    today_files = mock_context_tree["today_files"]
    files = mock_context_tree["files"]

    # No mock_context_tree temos:
    # Ontem (2 arquivos: yesterday_1, yesterday_2) -> índice 1
    # Anteontem (1 arquivo: two_days_ago_1) -> índice 2
    # Selecionamos apenas índice 2 (anteontem)
    res_select = subprocess.run(
        [sys.executable, str(cleanup_script), "--target-dir", str(root)],
        input="d\n2\n",
        capture_output=True,
        text=True,
    )
    assert res_select.returncode == 0
    # Arquivo de anteontem deve ter sido removido
    assert not files["two_days_ago_1"].exists()
    # Arquivos de ontem devem permanecer intactos
    assert files["yesterday_1"].exists()
    assert files["yesterday_2"].exists()
    # Arquivos de hoje devem permanecer intactos
    for tf in today_files:
        assert tf.exists()
