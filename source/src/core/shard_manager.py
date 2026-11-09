#!/usr/bin/env python3
# shard_manager.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:06(GMT-04:00)
"""
Gerenciador de Shards Multi-Máquina, Deduplicação e Ordenação Cronológica — Vitalia SPEC Kit (Domínio CORE)
"""

import sys
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap

health = kit_env_bootstrap.init()
from core.utils import (
    append_jsonl,
    get_current_datetime,
    get_timestamp,
    parse_sync_time,
)


class ShardManager:
    """
    CRUD seguro de shards YAML, deduplicação por machine_name e ordenação estrita por last_sync decrescente.
    """

    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.shards_dir = session_dir / "shards"
        self.shards_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = session_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.machines_file = self.data_dir / "machines.jsonl"

    def read_shard(self, shard_path: Path) -> Optional[Dict[str, Any]]:
        """Lê um shard YAML de forma tolerante e retorna um dicionário estruturado."""
        if not shard_path.exists():
            return None

        try:
            content = shard_path.read_text(encoding="utf-8")
            data: Dict[str, Any] = {}
            for line in content.splitlines():
                line_str = line.strip()
                if not line_str or line_str.startswith("#"):
                    continue
                if ":" in line_str and not line_str.startswith("-"):
                    k, v = line_str.split(":", 1)
                    key = k.strip()
                    val = v.strip().strip('"').strip("'")
                    data[key] = val
            return data
        except Exception as e:
            print(f"⚠️ [ShardManager] Erro ao ler shard {shard_path.name}: {e}", file=sys.stderr)
            return None

    def write_shard(
        self,
        machine_id: str,
        machine_name: str,
        task: str,
        status: str,
        next_step: str,
        steps: List[str],
        mode: str = "Standalone",
    ) -> Path:
        """Grava ou atualiza o shard da máquina local no schema canônico v0.0.1."""
        shard_path = self.shards_dir / f"{machine_id}.yaml"
        steps_yaml = "\n".join(f'  - "{s}"' for s in steps) if steps else '  - "Sessão iniciada"'
        ts = get_timestamp()

        payload_yaml = f"""# {machine_id}.yaml | Vitalia SPEC Kit v0.0.1 | {ts}
schema_version: "0.0.1"
machine_name: "{machine_name}"
machine_id: "{machine_id}"
mode: "{mode}"
current_task: "{task}"
status: "{status}"
next_step: "{next_step}"
last_sync: "{ts}"
steps_completed:
{steps_yaml}
"""
        shard_path.write_text(payload_yaml, encoding="utf-8")
        self.upsert_machines_jsonl(
            {
                "machine_id": machine_id,
                "machine_name": machine_name,
                "mode": mode,
                "last_sync": ts,
                "last_task": task,
            }
        )
        return shard_path

    def load_all_shards(self) -> List[Dict[str, Any]]:
        """
        Lê todos os shards presentes no diretório shards/, deduplica por machine_name
        e ordena estritamente por last_sync decrescente (mais recente primeiro — RCA-05).
        """
        shards = []
        for yaml_file in sorted(self.shards_dir.glob("*.yaml")):
            s = self.read_shard(yaml_file)
            if s:
                shards.append(s)
        deduped = self.filter_shards_by_machine(shards)
        deduped.sort(key=lambda item: parse_sync_time(item.get("last_sync", "")), reverse=True)
        return deduped

    def filter_shards_by_machine(self, shards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplica múltiplos shards com o mesmo 'machine_name', preservando estritamente
        aquele com o 'last_sync' mais recente, e retorna ordenado por last_sync decrescente.
        """
        by_machine: Dict[str, Dict[str, Any]] = {}

        for shard in shards:
            name = shard.get("machine_name", shard.get("machine_id", "unknown"))
            shard_time = parse_sync_time(shard.get("last_sync", ""))

            if name not in by_machine:
                by_machine[name] = shard
            else:
                existing_time = parse_sync_time(by_machine[name].get("last_sync", ""))
                if shard_time > existing_time:
                    by_machine[name] = shard

        result = list(by_machine.values())
        result.sort(key=lambda item: parse_sync_time(item.get("last_sync", "")), reverse=True)
        return result

    def check_staleness(self, last_sync_str: str) -> bool:
        """Retorna True se a última sincronização ocorreu há mais de 24 horas."""
        if not last_sync_str:
            return True
        try:
            sync_dt = parse_sync_time(last_sync_str)
            return (get_current_datetime() - sync_dt) > timedelta(hours=24)
        except Exception:
            return False

    def upsert_machines_jsonl(self, machine_record: Dict[str, Any]) -> None:
        """Registra no log append-only machines.jsonl."""
        record = {
            "timestamp": get_timestamp(),
            "machine_id": machine_record.get("machine_id", ""),
            "machine_name": machine_record.get("machine_name", ""),
            "mode": machine_record.get("mode", "Standalone"),
            "last_task": machine_record.get("last_task", ""),
        }
        append_jsonl(self.machines_file, record)

