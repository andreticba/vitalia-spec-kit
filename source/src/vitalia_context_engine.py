#!/usr/bin/env python3
# vitalia_context_engine.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:07(GMT-04:00)
"""
Entrypoint CLI de Controle de Contexto 3-Tier — Vitalia SPEC Kit v0.0.1

Exemplos de uso:
  python3 vitalia_context_engine.py --action init
  python3 vitalia_context_engine.py --action end --task "Feature 002" --p0 "Testes" --summary "Resumo"
  python3 vitalia_context_engine.py --action end --payload-file .vitalia/end_payload.json
  python3 vitalia_context_engine.py --action consolidate
"""

import argparse
import json
import sys
from pathlib import Path

_scripts_root = str(Path(__file__).resolve().parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap

health = kit_env_bootstrap.init()
from core.context_engine import ContextEngine
from core.utils import get_machine_identity


def main():
    parser = argparse.ArgumentParser(
        description="Motor de Controle de Contexto e Sincronização 3-Tier — Vitalia SPEC Kit (v0.0.1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["init", "consolidate", "end", "shard", "lock", "unlock", "status"],
        help="Ação a ser executada",
    )
    parser.add_argument("--session-dir", default=None, help="Caminho customizado de .vitalia/memory/session")
    parser.add_argument("--payload-file", default=None, help="Arquivo JSON opcional contendo task, p0, summary, learnings, decisions")
    parser.add_argument("--task", default="", help="Descrição da tarefa ativa")
    parser.add_argument("--p0", default="", help="Próximo passo prioritário (P0)")
    parser.add_argument("--summary", default="", help="Resumo das atividades da sessão")
    parser.add_argument("--learnings-json", default="[]", help="Array JSON de aprendizados estruturados")
    parser.add_argument("--decisions-json", default="[]", help="Array JSON de decisões de arquitetura")
    parser.add_argument("--status", default="Em Andamento", help="Status da estação (ex: Concluído)")
    parser.add_argument("--next-step", default="", help="Alias para P0")
    parser.add_argument("--mode", default="Standalone", help="Modo de operação (Standalone)")

    args = parser.parse_args()

    session_path = Path(args.session_dir) if args.session_dir else None
    engine = ContextEngine(session_path)

    if args.action == "init":
        engine.action_init()
    elif args.action == "consolidate":
        engine.action_consolidate()
    elif args.action == "end":
        task = args.task
        p0 = args.p0 or args.next_step
        summary = args.summary
        learnings_data = args.learnings_json
        decisions_data = args.decisions_json

        if args.payload_file:
            p_path = Path(args.payload_file)
            if p_path.exists():
                payload = json.loads(p_path.read_text(encoding="utf-8"))
                task = payload.get("task", task)
                p0 = payload.get("p0", payload.get("next_step", p0))
                summary = payload.get("summary", summary)
                learnings_data = payload.get("learnings", learnings_data)
                decisions_data = payload.get("decisions", decisions_data)

        engine.action_end(
            task=task,
            p0=p0,
            summary=summary,
            learnings_json=learnings_data,
            decisions_json=decisions_data,
        )
    elif args.action == "shard":
        mname, mid = get_machine_identity()
        engine.shard_mgr.write_shard(
            machine_id=mid,
            machine_name=mname,
            task=args.task,
            status=args.status,
            next_step=args.next_step or args.p0,
            steps=[args.summary] if args.summary else [],
            mode="Standalone",
        )
        print(f"✅ Shard atualizado com sucesso! [{mname} / {mid}]")
    elif args.action == "lock":
        mname, mid = get_machine_identity()
        ok, token = engine.semaphore_mgr.acquire(mname, mid, reason="Lock manual via CLI")
        print(f"{'✅ Lock adquirido! Token: ' + token if ok else '❌ Falha ao adquirir lock: ' + token}")
    elif args.action == "unlock":
        engine.semaphore_mgr.release("", force=True)
        print("✅ Semáforo liberado com sucesso!")
    elif args.action == "status":
        sem = engine.semaphore_mgr.read_semaphore()
        print(
            f"Semáforo: {sem.get('state')} | Detentor: {sem.get('machine_name')} | Expira em: {sem.get('expires_at')}"
        )


if __name__ == "__main__":
    main()

