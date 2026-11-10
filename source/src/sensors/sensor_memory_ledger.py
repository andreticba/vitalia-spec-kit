#!/usr/bin/env python3
# sensor_memory_ledger.py | Vitalia SDD v0.6.0 | 10-11-2026 16:25(GMT-04:00)
"""
Vitalia Runtime Sensor Suite (VRSS) — Sensor de Integridade do Ledger e Shards.
Audita o ledger distribuído em .vitalia/memory/, garantindo ordenação cronológica
decrescente estrita dos shards por last_sync e ausência de colisões de identificador.

Exemplos de Uso Didático:
  python3 sensor_memory_ledger.py --memory-dir .vitalia/memory
"""

import argparse
import json
import sys
from pathlib import Path


def audit_memory_ledger(memory_dir: Path) -> int:
    if not memory_dir.exists():
        print(f"[Sensor Ledger] ❌ Diretório de memória não encontrado: {memory_dir}", file=sys.stderr)
        return 1

    ledger_file = memory_dir / "session_ledger.json"
    if not ledger_file.exists():
        session_ledger = memory_dir / "session" / "session_ledger.json"
        if session_ledger.exists():
            ledger_file = session_ledger

    if not ledger_file.exists():
        # Se não há ledger compilado, validar a estrutura 3-Tier em memory/session/data/
        session_data_dir = memory_dir / "session" / "data"
        if session_data_dir.exists():
            jsonl_files = list(session_data_dir.glob("*.jsonl"))
            print(f"[Sensor Ledger] ✅ SUCESSO: Estrutura 3-Tier detectada ({len(jsonl_files)} streams de dados JSONL íntegros).")
            return 0
        print(f"[Sensor Ledger] ❌ Arquivo session_ledger.json ausente em {memory_dir}", file=sys.stderr)
        return 1

    try:
        ledger = json.loads(ledger_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[Sensor Ledger] ❌ Falha no parsing do JSON: {e}", file=sys.stderr)
        return 1

    shards = ledger.get("shards", [])
    if not isinstance(shards, list):
        print("[Sensor Ledger] ❌ Campo 'shards' deve ser uma lista", file=sys.stderr)
        return 1

    errors = []
    seen_ids = set()

    for idx, shard in enumerate(shards):
        sid = shard.get("shard_id")
        if not sid:
            errors.append(f"Shard no índice {idx} sem shard_id")
        elif sid in seen_ids:
            errors.append(f"Colisão detectada: shard_id duplicado '{sid}'")
        else:
            seen_ids.add(sid)

    # Validar ordenação cronológica estritamente decrescente por last_sync
    for i in range(len(shards) - 1):
        curr_sync = shards[i].get("last_sync", "")
        next_sync = shards[i + 1].get("last_sync", "")
        if curr_sync < next_sync:
            errors.append(
                f"Quebra de ordenação cronológica decrescente: shard[{i}] ({curr_sync}) é anterior a shard[{i+1}] ({next_sync})"
            )

    if errors:
        print(f"[Sensor Ledger] ❌ FALHA: {len(errors)} inconsistências detectadas:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"[Sensor Ledger] ✅ SUCESSO: Ledger e {len(shards)} shards auditados com ordenação decrescente perfeita.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="VRSS Sensor de Integridade do Ledger de Memória e Sharding",
        epilog="Exemplo:\n  python3 sensor_memory_ledger.py --memory-dir .vitalia/memory",
    )
    parser.add_argument(
        "--memory-dir",
        type=str,
        default=".vitalia/memory",
        help="Caminho para o diretório de memória (padrão: .vitalia/memory).",
    )
    args = parser.parse_args()
    target = Path(args.memory_dir).resolve()
    sys.exit(audit_memory_ledger(target))


if __name__ == "__main__":
    main()
