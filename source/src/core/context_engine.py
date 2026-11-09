#!/usr/bin/env python3
# context_engine.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:06(GMT-04:00)
"""
Orquestrador Mestre de Controle de Contexto 3-Tier — Vitalia SPEC Kit (Domínio CORE)
"""

import json
import os
import re
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap

health = kit_env_bootstrap.init()
from core.shard_manager import ShardManager
from core.utils import (
    append_jsonl,
    generate_id,
    get_current_datetime,
    get_machine_identity,
    get_timestamp,
    parse_sync_time,
    read_jsonl,
)
from rendering.dashboard_renderer import DashboardRenderer
from rendering.grounding_renderer import GroundingRenderer
from rendering.view_renderer import ViewRenderer


class SemaphoreManager:
    """Controlador de concorrência em arquivo state/semaphore.json com auto-expiração por TTL (sem Redis)."""

    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.state_dir = session_dir / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore_file = self.state_dir / "semaphore.json"
        self.ttl_minutes = 5

    def _write_file(self, payload: Dict[str, Any]) -> None:
        temp_file = self.semaphore_file.with_suffix(".json.tmp")
        temp_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temp_file, self.semaphore_file)

    def read_semaphore(self) -> Dict[str, Any]:
        default_state = {
            "state": "FREE",
            "locked_by": "",
            "machine_id": "",
            "machine_name": "",
            "locked_at": "",
            "expires_at": "",
            "lease_token": "",
            "lock_reason": "",
        }
        if not self.semaphore_file.exists():
            self._write_file(default_state)
            return default_state

        try:
            raw = json.loads(self.semaphore_file.read_text(encoding="utf-8"))
            state_val = raw.get("state") or raw.get("status") or "FREE"
            if state_val in ("LIVRE", "FREE", "free", "livre"):
                state_val = "FREE"
            elif state_val in ("LOCKED", "locked", "BLOQUEADO"):
                state_val = "LOCKED"

            data = {
                "state": state_val,
                "locked_by": raw.get("locked_by") or raw.get("machine_id") or "",
                "machine_id": raw.get("machine_id") or raw.get("locked_by") or "",
                "machine_name": raw.get("machine_name") or "unknown",
                "locked_at": raw.get("locked_at") or raw.get("updated_at") or "",
                "expires_at": raw.get("expires_at") or "",
                "lease_token": raw.get("lease_token") or "",
                "lock_reason": raw.get("lock_reason") or "",
            }

            if data.get("state") == "LOCKED":
                expires_str = data.get("expires_at", "")
                if expires_str:
                    expires_dt = parse_sync_time(expires_str)
                    if get_current_datetime() > expires_dt:
                        self.release(data.get("lease_token", ""), force=True)
                        return default_state
            return data
        except Exception:
            return default_state

    def acquire(self, machine_name: str, machine_id: str, reason: str = "Consolidação de sessão") -> Tuple[bool, str]:
        current = self.read_semaphore()
        if current.get("state") == "LOCKED" and current.get("machine_id") != machine_id:
            return (
                False,
                f"Bloqueado por {current.get('machine_name')} ({current.get('machine_id')}) até {current.get('expires_at')}",
            )

        now = get_current_datetime()
        expires_dt = now + timedelta(minutes=self.ttl_minutes)
        lease_token = generate_id(f"{machine_id}_{now.isoformat()}_{os.getpid()}", length=16)

        payload = {
            "state": "LOCKED",
            "locked_by": machine_id,
            "machine_id": machine_id,
            "machine_name": machine_name,
            "locked_at": get_timestamp(now),
            "expires_at": get_timestamp(expires_dt),
            "lease_token": lease_token,
            "lock_reason": reason,
        }
        try:
            self._write_file(payload)
            return True, lease_token
        except Exception as e:
            return False, f"Falha de I/O ao gravar semáforo: {e}"

    def release(self, lease_token: str, force: bool = False) -> bool:
        current = self.read_semaphore()
        if not force and current.get("lease_token") != lease_token and current.get("state") == "LOCKED":
            return False

        free_payload = {
            "state": "FREE",
            "locked_by": "",
            "machine_id": "",
            "machine_name": "",
            "locked_at": "",
            "expires_at": "",
            "lease_token": "",
            "lock_reason": "",
        }
        try:
            self._write_file(free_payload)
            return True
        except Exception:
            return False


class ContextEngine:
    """Orquestrador central de estado, concorrência e renderização de memória 3-Tier."""

    def __init__(self, session_dir: Optional[Path] = None):
        self.project_root = kit_env_bootstrap.find_project_root()
        self.session_dir = session_dir or (self.project_root / ".vitalia" / "memory" / "session")
        self.semaphore_mgr = SemaphoreManager(self.session_dir)
        self.shard_mgr = ShardManager(self.session_dir)
        self.dashboard_renderer = DashboardRenderer(self.session_dir)
        self.view_renderer = ViewRenderer(self.session_dir)
        self.grounding_renderer = GroundingRenderer(self.session_dir)

    def _normalize_jsonl_ledgers(self) -> None:
        data_dir = self.session_dir / "data"
        learnings_file = data_dir / "learnings.jsonl"
        if learnings_file.exists():
            records = read_jsonl(learnings_file)
            changed = False
            for rec in records:
                if not rec.get("id"):
                    rec["id"] = generate_id(str(rec.get("timestamp", "")) + str(rec.get("learning", "")))
                    changed = True
                if not rec.get("category"):
                    rec["category"] = "PROJETO"
                    changed = True
                if not rec.get("rationale"):
                    rec["rationale"] = "Registro defasado"
                    changed = True
                if not rec.get("timestamp"):
                    rec["timestamp"] = get_timestamp()
                    changed = True
            if changed:
                tmp = learnings_file.with_suffix(".jsonl.tmp")
                tmp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
                os.replace(tmp, learnings_file)

        decisions_file = data_dir / "decisions.jsonl"
        if decisions_file.exists():
            records = read_jsonl(decisions_file)
            changed = False
            for rec in records:
                if not rec.get("id"):
                    rec["id"] = generate_id(str(rec.get("timestamp", "")) + str(rec.get("decision", "")))
                    changed = True
                if not rec.get("category"):
                    rec["category"] = "ARQUITETURA"
                    changed = True
                if not rec.get("rationale"):
                    rec["rationale"] = "Registro defasado"
                    changed = True
                if not rec.get("timestamp"):
                    rec["timestamp"] = get_timestamp()
                    changed = True
            if changed:
                tmp = decisions_file.with_suffix(".jsonl.tmp")
                tmp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
                os.replace(tmp, decisions_file)

    def action_init(self) -> None:
        """Inicializa repositório de memória de contexto em novo projeto."""
        print(f"[ContextEngine] Inicializando estrutura em: {self.session_dir}")
        (self.session_dir / "data").mkdir(parents=True, exist_ok=True)
        (self.session_dir / "shards").mkdir(parents=True, exist_ok=True)
        (self.session_dir / "state").mkdir(parents=True, exist_ok=True)

        self.semaphore_mgr.read_semaphore()
        self.grounding_renderer.compile()
        print("[ContextEngine] ✅ Estrutura inicial criada com sucesso!")

    def action_consolidate(self) -> None:
        """Executa a consolidação de memória completa, normalização e renderização das views."""
        print(f"[ContextEngine] 🔄 Iniciando consolidação em: {self.session_dir}")
        self._normalize_jsonl_ledgers()

        sem_data = self.semaphore_mgr.read_semaphore()
        shards = self.shard_mgr.load_all_shards()
        history = read_jsonl(self.session_dir / "data" / "session_history.jsonl")
        decisions = read_jsonl(self.session_dir / "data" / "decisions.jsonl")
        learnings = read_jsonl(self.session_dir / "data" / "learnings.jsonl")

        readme_content = self.dashboard_renderer.render(sem_data, shards, history, decisions)
        (self.session_dir / "README.md").write_text(readme_content, encoding="utf-8")

        active_shard = shards[0] if shards else None
        state_content = self.view_renderer.render_session_state(active_shard, sem_data)
        (self.session_dir / "SESSION_STATE.md").write_text(state_content, encoding="utf-8")

        decisions_content = self.view_renderer.render_decisions(decisions)
        (self.session_dir / "DECISIONS.md").write_text(decisions_content, encoding="utf-8")

        learnings_content = self.view_renderer.render_learnings(learnings)
        (self.session_dir / "LEARNINGS.md").write_text(learnings_content, encoding="utf-8")

        history_content = self.view_renderer.render_session_history(history)
        (self.session_dir / "SESSION_HISTORY.md").write_text(history_content, encoding="utf-8")

        self.grounding_renderer.compile()

        append_jsonl(
            self.session_dir / "data" / "events.jsonl",
            {
                "timestamp": get_timestamp(),
                "event_type": "CONTEXT_CONSOLIDATED",
                "payload": {
                    "shards_count": len(shards),
                    "learnings_count": len(learnings),
                    "decisions_count": len(decisions),
                },
            },
        )
        print(
            f"[ContextEngine] ✅ Consolidação concluída: {len(shards)} estações | README.md e Pure Views compiladas!"
        )

    def action_end(
        self,
        task: str,
        p0: str,
        summary: str,
        learnings_json: str | List[Dict[str, Any]] = "[]",
        decisions_json: str | List[Dict[str, Any]] = "[]",
    ) -> None:
        """Executa o encerramento estruturado de sessão (Fase 2 do session-end)."""
        machine_name, default_mid = get_machine_identity()
        machine_id = os.environ.get("VITALIA_MACHINE_ID", default_mid)
        mode = "Standalone"

        print(f"[ContextEngine] 🏁 Encerrando sessão para máquina '{machine_name}' ({machine_id})...")

        try:
            learnings = json.loads(learnings_json) if isinstance(learnings_json, str) else learnings_json
        except Exception:
            learnings = []

        try:
            decisions = json.loads(decisions_json) if isinstance(decisions_json, str) else decisions_json
        except Exception:
            decisions = []

        learnings_file = self.session_dir / "data" / "learnings.jsonl"
        for item in learnings:
            rec = {
                "id": generate_id(str(item.get("learning", "")) + get_timestamp()),
                "type": "learning",
                "timestamp": get_timestamp(),
                "machine_id": machine_id,
                "source_origin": machine_name,
                "category": item.get("category", "PROJETO"),
                "learning": item.get("learning", ""),
                "rationale": item.get("rationale", "Registro defasado"),
                "trigger_event": item.get("trigger_event", "session-end"),
            }
            append_jsonl(learnings_file, rec)

        decisions_file = self.session_dir / "data" / "decisions.jsonl"
        for item in decisions:
            rec = {
                "id": generate_id(str(item.get("decision", "")) + get_timestamp()),
                "type": "decision",
                "timestamp": get_timestamp(),
                "machine_id": machine_id,
                "category": item.get("category", "ARQUITETURA"),
                "decision": item.get("decision", ""),
                "rationale": item.get("rationale", "Registro defasado"),
                "alternatives": item.get("alternatives", []),
            }
            append_jsonl(decisions_file, rec)

        history_file = self.session_dir / "data" / "session_history.jsonl"
        append_jsonl(
            history_file,
            {
                "timestamp": get_timestamp(),
                "last_sync": get_timestamp(),
                "machine_id": machine_id,
                "machine_name": machine_name,
                "task": task,
                "summary": summary,
                "steps": [summary] if summary else [],
                "next_step": p0,
                "status": "Concluído",
                "mode": mode,
            },
        )

        self.shard_mgr.write_shard(
            machine_id=machine_id,
            machine_name=machine_name,
            task=task,
            status="Concluído",
            next_step=p0,
            steps=[summary] if summary else [],
            mode=mode,
        )

        self.action_consolidate()
        print("[ContextEngine] ✅ Sessão encerrada com sucesso e dados estruturados persistidos!")

