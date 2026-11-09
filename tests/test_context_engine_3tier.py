# test_context_engine_3tier.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:05(GMT-04:00)
"""
Suíte de testes comportamentais para US4 (Motor 3-Tier, Ordenação de Shards por last_sync e Dashboard Rico):
- T025 [TEST:BUGFIX]: test_shard_manager_orders_by_last_sync_descending (RCA-05)
- T026 [TEST:MIGRATION]: test_context_engine_full_cycle_and_rich_dashboard_rendering
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_SRC = REPO_ROOT / "source" / "src"


def test_shard_manager_orders_by_last_sync_descending(tmp_path: Path):
    """
    T025 [TEST:BUGFIX] (RCA-05) — Reproduz o bug de shard_manager.py:105 onde
    sorted(self.shards_dir.glob("*.yaml")) ordenava alfabeticamente por filename:
    - Cria 17a6f667.yaml (alfabeticamente primeiro, mas com last_sync ANTIGO: 03-11-2026 05:47:37(GMT-04:00))
    - Cria eb10269b.yaml (alfabeticamente posterior, mas com last_sync MAIS RECENTE: 07-11-2026 21:38:04(GMT-04:00))
    Verifica que:
    1. ShardManager.load_all_shards()[0] retorna eb10269b em vez de 17a6f667;
    2. vitalia_context_engine.py --action consolidate destaca a estação eb10269b (srv_master) como Estação Ativa
       em SESSION_STATE.md e README.md.
    """
    session_dir = tmp_path / ".vitalia" / "memory" / "session"
    shards_dir = session_dir / "shards"
    shards_dir.mkdir(parents=True)
    (session_dir / "data").mkdir(parents=True)
    (session_dir / "state").mkdir(parents=True)

    # 17a6f667 comes FIRST alphabetically, but is OLDER
    (shards_dir / "17a6f667.yaml").write_text(
        """schema_version: "0.0.1"
machine_name: "andrenote"
machine_id: "17a6f667"
mode: "Standalone"
current_task: "Old Stale Task From Nov 03"
status: "Concluído"
next_step: "Old Stale P0"
last_sync: "03-11-2026 05:47:37(GMT-04:00)"
steps_completed:
  - "Old step"
""",
        encoding="utf-8",
    )

    # eb10269b comes SECOND alphabetically, but is NEWER
    (shards_dir / "eb10269b.yaml").write_text(
        """schema_version: "0.0.1"
machine_name: "srv_master"
machine_id: "eb10269b"
mode: "Standalone"
current_task: "Fresh Active Task From Nov 07"
status: "Em Andamento"
next_step: "Fresh Active P0"
last_sync: "07-11-2026 21:38:04(GMT-04:00)"
steps_completed:
  - "Fresh step"
""",
        encoding="utf-8",
    )

    # Direct unit check of ShardManager.load_all_shards()
    if str(SOURCE_SRC) not in sys.path:
        sys.path.insert(0, str(SOURCE_SRC))
    from core.shard_manager import ShardManager

    mgr = ShardManager(session_dir)
    loaded_shards = mgr.load_all_shards()
    assert len(loaded_shards) == 2
    assert loaded_shards[0]["machine_id"] == "eb10269b", (
        f"ShardManager.load_all_shards()[0] returned stale shard {loaded_shards[0]['machine_id']} instead of eb10269b!"
    )

    engine_script = SOURCE_SRC / "vitalia_context_engine.py"
    proc = subprocess.run(
        [sys.executable, str(engine_script), "--action", "consolidate", "--session-dir", str(session_dir)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"vitalia_context_engine.py failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

    session_state = (session_dir / "SESSION_STATE.md").read_text(encoding="utf-8")
    assert "Fresh Active Task From Nov 07" in session_state, (
        f"Stale shard overwrote active session state! SESSION_STATE.md:\n{session_state}"
    )
    assert "Fresh Active P0" in session_state
    assert "srv_master" in session_state

    readme = (session_dir / "README.md").read_text(encoding="utf-8")
    assert "Estação Ativa:** `srv_master` (`eb10269b`)" in readme, (
        f"README.md did not highlight most recent shard eb10269b! README.md:\n{readme}"
    )


def test_context_engine_full_cycle_and_rich_dashboard_rendering(tmp_path: Path):
    """
    T026 [TEST:MIGRATION] — Verifica o ciclo completo init -> end -> consolidate do motor 3-Tier:
    1. --action init inicializa data/, shards/, state/semaphore.json e grounding-domains-local.yaml (10 domínios);
    2. --action end grava no ledger append-only data/decisions.jsonl, data/learnings.jsonl,
       data/session_history.jsonl com timestamps DD-MM-YYYY HH:MM:SS(GMT-04:00) (nunca ISO 8601 bruto);
    3. --action consolidate compila README.md rico (badges Shields.io, topologia Mermaid flowchart TD
       com labels entre aspas duplas P16, tabela HTML <table> de máquinas, seção 🎯 Sessão Ativa em Destaque,
       blocos <details> e os 10 domínios canônicos), SESSION_STATE.md, DECISIONS.md, LEARNINGS.md e SESSION_HISTORY.md.
    """
    project_dir = tmp_path / "project_3tier"
    project_dir.mkdir(parents=True)
    (project_dir / ".env").write_text("VITALIA_ENVIRONMENT=development\n", encoding="utf-8")
    session_dir = project_dir / ".vitalia" / "memory" / "session"

    engine_script = SOURCE_SRC / "vitalia_context_engine.py"
    env = os.environ.copy()
    env["VITALIA_MACHINE_NAME"] = "workstation-01"

    # 1. Init
    init_proc = subprocess.run(
        [sys.executable, str(engine_script), "--action", "init", "--session-dir", str(session_dir)],
        cwd=str(project_dir),
        env=env,
        capture_output=True,
        text=True,
    )
    assert init_proc.returncode == 0, f"init failed: {init_proc.stderr}"
    assert (session_dir / "state" / "semaphore.json").is_file()
    gd_local = (session_dir / "grounding-domains-local.yaml").read_text(encoding="utf-8")
    for dom in [
        "provedores_de_ia",
        "python_packages",
        "web_technologies",
        "external_apis",
        "security_practices",
        "regulations_compliance",
        "cloud_services",
        "scientific_claims",
        "clinical_safety",
        "software_architecture",
    ]:
        assert dom in gd_local, f"Missing canonical domain {dom} in grounding-domains-local.yaml"

    # 2. End via CLI flags (--decisions-json, --learnings-json)
    learnings_str = json.dumps(
        [
            {
                "category": "KIT",
                "learning": "[KIT] Ordenar shards por last_sync decrescente evita sobrescrita",
                "rationale": "Ordem alfabética por hash hexadecimal causava regressão de estado",
            }
        ],
        ensure_ascii=False,
    )
    decisions_str = json.dumps(
        [
            {
                "category": "ARQUITETURA",
                "decision": "Zero Poda incondicional nos 16 workflows",
                "rationale": "Preserva fidelidade integral dos 18 princípios P00-P17",
                "alternatives": ["Poda por budget de tokens"],
            }
        ],
        ensure_ascii=False,
    )

    end_proc = subprocess.run(
        [
            sys.executable,
            str(engine_script),
            "--action",
            "end",
            "--session-dir",
            str(session_dir),
            "--task",
            "Spec 002 Universal Bootstrap",
            "--p0",
            "Executar /vitalia-converge",
            "--summary",
            "Implementado motor 3-Tier e Guardian sem poda",
            "--learnings-json",
            learnings_str,
            "--decisions-json",
            decisions_str,
        ],
        cwd=str(project_dir),
        env=env,
        capture_output=True,
        text=True,
    )
    assert end_proc.returncode == 0, f"end failed:\nSTDOUT:\n{end_proc.stdout}\nSTDERR:\n{end_proc.stderr}"

    # Verify JSONL ledgers and GMT-04:00 timestamp format
    ts_pattern = re.compile(r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}\(GMT-04:00\)$")
    for jsonl_name in ("learnings.jsonl", "decisions.jsonl", "session_history.jsonl"):
        p = session_dir / "data" / jsonl_name
        assert p.is_file(), f"Missing {jsonl_name}"
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                assert ts_pattern.match(rec.get("timestamp", "")), f"Invalid timestamp in {jsonl_name}: {rec}"

    readme = (session_dir / "README.md").read_text(encoding="utf-8")
    assert "https://img.shields.io/badge/" in readme
    assert "```mermaid\nflowchart TD" in readme
    assert "<table>" in readme
    assert "🎯 Sessão Ativa em Destaque" in readme
    assert "<details>" in readme
    assert "Spec 002 Universal Bootstrap" in readme
    assert "Zero Poda incondicional nos 16 workflows" in readme
    assert "provedores_de_ia" in readme
    assert "software_architecture" in readme

    learnings_md = (session_dir / "LEARNINGS.md").read_text(encoding="utf-8")
    assert "Ordenar shards por last_sync decrescente" in learnings_md

    decisions_md = (session_dir / "DECISIONS.md").read_text(encoding="utf-8")
    assert "Zero Poda incondicional nos 16 workflows" in decisions_md
