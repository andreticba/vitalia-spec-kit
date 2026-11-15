# conftest.py | Vitalia SPEC Kit v0.0.1 | 15-11-2026 13:55(GMT-04:00)
import datetime
from pathlib import Path
import pytest

CUIABA_TZ = datetime.timezone(datetime.timedelta(hours=-4))


@pytest.fixture
def mock_context_tree(tmp_path: Path):
    """
    Cria uma árvore realista de arquivos de contexto em:
    .vitalia/memory/data_storage/context/mock_machine_id/
    com arquivos de hoje (GMT-04:00) e datas anteriores.
    """
    now = datetime.datetime.now(CUIABA_TZ)
    today_str = now.strftime("%Y%m%d")
    yesterday_str = (now - datetime.timedelta(days=1)).strftime("%Y%m%d")
    two_days_ago_str = (now - datetime.timedelta(days=2)).strftime("%Y%m%d")

    context_dir = tmp_path / ".vitalia" / "memory" / "data_storage" / "context" / "mock_machine"
    context_dir.mkdir(parents=True, exist_ok=True)

    # Cria .env mínimo para teste de ambiente
    (tmp_path / ".env").write_text("VITALIA_ENVIRONMENT=test\n", encoding="utf-8")

    files = {
        "today_1": context_dir / f"session-start_{today_str}_100000_abc1.json",
        "today_2": context_dir / f"clarify_{today_str}_110000_abc2.json",
        "yesterday_1": context_dir / f"spec-plan_{yesterday_str}_150000_def1.json",
        "yesterday_2": context_dir / f"spec-tasks_{yesterday_str}_160000_def2.json",
        "two_days_ago_1": context_dir / f"brainstorming_{two_days_ago_str}_090000_ghi1.json",
    }

    for name, path in files.items():
        path.write_text('{"mock": true}', encoding="utf-8")

    return {
        "root": tmp_path,
        "context_dir": context_dir,
        "files": files,
        "today_files": [files["today_1"], files["today_2"]],
        "past_files": [files["yesterday_1"], files["yesterday_2"], files["two_days_ago_1"]],
        "today_str": now.strftime("%d-%m-%Y"),
        "yesterday_str": (now - datetime.timedelta(days=1)).strftime("%d-%m-%Y"),
        "two_days_ago_str": (now - datetime.timedelta(days=2)).strftime("%d-%m-%Y"),
    }
