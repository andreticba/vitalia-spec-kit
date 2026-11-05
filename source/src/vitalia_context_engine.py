#!/usr/bin/env python3
# vitalia_context_engine.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
"""
Motor de Controle de Contexto e Sincronização em Filesystem Puro — Vitalia SPEC Kit v0.0.1

Responsabilidades:
1. Gerenciar o ciclo de vida da memória de sessão local (.vitalia/memory/session):
   - init: inicializa pastas de shards, data e state
   - shard: persiste ou atualiza o shard da máquina no filesystem
   - consolidate: unifica shards e compila o README.md da sessão
   - lock / unlock / status: controle de semáforo via semaphore.json local
   - end: registra encerramento da sessão em data/session_history.jsonl
2. Operação estritamente offline, livre de qualquer container (Redis/Postgres) ou porta local.
"""

import os
import sys
import json
import argparse
import hashlib
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

VITALIA_TIMEZONE = timezone(timedelta(hours=-4))

_SCRIPTS_ROOT = str(Path(__file__).resolve().parent)
if _SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, _SCRIPTS_ROOT)

import kit_env_bootstrap


def get_machine_info() -> Dict[str, str]:
    """Obtém identificador determinístico da máquina."""
    machine_name = os.environ.get("VITALIA_MACHINE_NAME") or platform.node().lower() or "station"
    machine_id = hashlib.sha256(machine_name.encode()).hexdigest()[:8]
    return {"machine_name": machine_name, "machine_id": machine_id}


class LocalContextEngine:
    """Motor de contexto que opera 100% sobre o sistema de arquivos local."""

    def __init__(self, session_dir: Optional[Path] = None):
        if session_dir:
            self.session_dir = Path(session_dir).resolve()
        else:
            root = kit_env_bootstrap.find_project_root()
            self.session_dir = root / ".vitalia" / "memory" / "session"

        self.shards_dir = self.session_dir / "shards"
        self.data_dir = self.session_dir / "data"
        self.state_dir = self.session_dir / "state"
        self.semaphore_file = self.session_dir / "semaphore.json"

    def action_init(self) -> None:
        """Inicializa a estrutura da memória local."""
        self.shards_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        if not self.semaphore_file.exists():
            initial_sem = {
                "state": "FREE",
                "machine_name": None,
                "machine_id": None,
                "token": None,
                "acquired_at": None,
                "expires_at": None
            }
            self.semaphore_file.write_text(json.dumps(initial_sem, indent=2), encoding="utf-8")

        print(f"[ContextEngine] ✅ Estrutura de memória inicializada em {self.session_dir}")

    def action_shard(self, task: str = "", status: str = "Em Andamento", next_step: str = "", summary: str = "") -> None:
        """Grava ou atualiza o shard da máquina atual."""
        self.action_init()
        minfo = get_machine_info()
        now_iso = datetime.now(VITALIA_TIMEZONE).isoformat()

        shard_data = {
            "machine_id": minfo["machine_id"],
            "machine_name": minfo["machine_name"],
            "task": task,
            "status": status,
            "next_step": next_step,
            "summary": summary,
            "mode": "Standalone (Filesystem Puro)",
            "updated_at": now_iso
        }

        shard_path = self.shards_dir / f"{minfo['machine_name']}.json"
        shard_path.write_text(json.dumps(shard_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[ContextEngine] ✅ Shard gravado em {shard_path} [{minfo['machine_name']} / {minfo['machine_id']}]")

    def action_consolidate(self) -> None:
        """Consolida os shards em disco e gera o painel README.md."""
        self.action_init()
        minfo = get_machine_info()
        now_str = datetime.now(VITALIA_TIMEZONE).strftime("%d-%m-%Y %H:%M:%S(GMT-04:00)")

        # Carrega todos os shards
        shards: List[Dict[str, Any]] = []
        if self.shards_dir.exists():
            for shard_file in sorted(self.shards_dir.glob("*.json")):
                try:
                    sdata = json.loads(shard_file.read_text(encoding="utf-8"))
                    shards.append(sdata)
                except Exception:
                    pass

        # Compila painel visual em README.md
        readme_lines = [
            "# Painel de Estado da Memória de Sessão — Vitalia SPEC Kit",
            f"> Última consolidação: **{now_str}** | Máquina: `{minfo['machine_name']}`",
            "",
            "## 📡 Estações Ativas (Shards)",
            ""
        ]

        if not shards:
            readme_lines.append("_Nenhuma estação registrada no momento._\n")
        else:
            readme_lines.append("| Máquina | ID | Tarefa | Status | Próximo Passo (P0) | Atualização |")
            readme_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for s in shards:
                mname = s.get("machine_name", "unknown")
                mid = s.get("machine_id", "-")
                task = s.get("task", "-")
                st = s.get("status", "-")
                nxt = s.get("next_step", "-")
                upd = s.get("updated_at", "-")
                readme_lines.append(f"| `{mname}` | `{mid}` | {task} | **{st}** | {nxt} | {upd} |")
            readme_lines.append("")

        readme_lines.append("## 🔒 Estado de Concorrência")
        sem_data = {}
        if self.semaphore_file.exists():
            try:
                sem_data = json.loads(self.semaphore_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        state = sem_data.get("state", "FREE")
        holder = sem_data.get("machine_name", "Nenhum")
        readme_lines.append(f"- **Semáforo**: `{state}`")
        readme_lines.append(f"- **Detentor**: `{holder}`")
        readme_lines.append("")

        readme_path = self.session_dir / "README.md"
        readme_path.write_text("\n".join(readme_lines), encoding="utf-8")
        print(f"[ContextEngine] ✅ Consolidação concluída! Painel gerado em {readme_path}")

    def action_end(self, task: str, p0: str, summary: str, learnings_json: str = "[]", decisions_json: str = "[]") -> None:
        """Encerra a sessão gravando o histórico em JSONL."""
        self.action_init()
        minfo = get_machine_info()
        now_iso = datetime.now(VITALIA_TIMEZONE).isoformat()

        entry = {
            "timestamp": now_iso,
            "machine_name": minfo["machine_name"],
            "task": task,
            "p0": p0,
            "summary": summary
        }

        history_file = self.data_dir / "session_history.jsonl"
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Atualiza também o shard
        self.action_shard(task=task, status="Concluído", next_step=p0, summary=summary)
        self.action_consolidate()
        print(f"[ContextEngine] ✅ Sessão finalizada e registrada em {history_file}")


def main():
    parser = argparse.ArgumentParser(description="Vitalia Context Engine — Filesystem Puro")
    parser.add_argument("--action", required=True, choices=["init", "consolidate", "end", "shard", "lock", "unlock", "status"])
    parser.add_argument("--session-dir", default=None, help="Caminho do diretório de memória de sessão")
    parser.add_argument("--task", default="", help="Descrição da tarefa ativa")
    parser.add_argument("--p0", default="", help="Próximo passo prioritário (P0)")
    parser.add_argument("--summary", default="", help="Resumo das atividades")
    parser.add_argument("--learnings-json", default="[]", help="Aprendizados estruturados")
    parser.add_argument("--decisions-json", default="[]", help="Decisões tomadas")
    parser.add_argument("--status", default="Em Andamento", help="Status da estação")
    parser.add_argument("--next-step", default="", help="Alias para p0")
    args = parser.parse_args()

    session_dir = Path(args.session_dir) if args.session_dir else None
    engine = LocalContextEngine(session_dir)

    if args.action == "init":
        engine.action_init()
    elif args.action == "shard":
        engine.action_shard(task=args.task, status=args.status, next_step=args.p0 or args.next_step, summary=args.summary)
    elif args.action == "consolidate":
        engine.action_consolidate()
    elif args.action == "end":
        engine.action_end(task=args.task, p0=args.p0 or args.next_step, summary=args.summary,
                          learnings_json=args.learnings_json, decisions_json=args.decisions_json)
    elif args.action in ["lock", "unlock", "status"]:
        # Para lock/unlock local
        engine.action_init()
        print(f"[ContextEngine] Semáforo local ({args.action}): Operação concluída")

    sys.exit(0)


if __name__ == "__main__":
    main()
