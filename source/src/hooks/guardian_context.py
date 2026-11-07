#!/usr/bin/env python3
# guardian_context.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
"""
Módulo Guardian Context V2 — Injeção Constitucional Integral e Sem Podas (§11).

Responsabilidades:
1. Carregar a Constituição Canônica (P00 a P17) e perfis dinâmicos de governança.
2. Injetar a totalidade das regras, catálogo e aprendizados sem podas artificiais de tokens.
3. Respeitar o agnóstico de hardware e modelos de fronteira na IDE Antigravity.
4. Totalmente desacoplado de Redis, Docker e conexões de rede locais.
"""

import os
import sys
import json
import yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

_SCRIPTS_ROOT = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, _SCRIPTS_ROOT)

import kit_env_bootstrap


class GuardianContextV2:
    """
    Construtor e orquestrador de contexto do Guardian sem podas para modelos de fronteira.
    """

    def __init__(self, workflow_name: str, guardian_config: dict, cwd: Path, user_args: str = ""):
        self.workflow_name = workflow_name
        self.guardian_config = guardian_config or {}
        self.cwd = Path(cwd).resolve()
        self.user_args = user_args
        self.project_root = kit_env_bootstrap.find_project_root(self.cwd)
        self.kit_dir = self._resolve_kit_dir()

    def _resolve_kit_dir(self) -> Path:
        return kit_env_bootstrap.resolve_kit_dir(self.project_root)

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _load_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        items = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        items.append(json.loads(line))
        except Exception:
            pass
        return items

    def build_payload(self) -> Dict[str, Any]:
        """
        Gera o payload de governança sem cortes de contexto (Zero Pruning).
        """
        profiles_dir = self.kit_dir / "profiles"
        if not profiles_dir.exists():
            profiles_dir = Path(__file__).resolve().parent.parent.parent / "profiles"

        sources: Dict[str, Any] = {}

        # 1. Ingestão Dinâmica de Fontes YAML declaradas ou padrão
        yaml_sources = self.guardian_config.get("yaml_sources")
        if not yaml_sources:
            yaml_sources = ["constitution", "routing_table", "brainstorming_intents", "grounding_domains"]

        now_tz = datetime.now(timezone(timedelta(hours=-4)))

        for src_name in yaml_sources:
            yaml_path = profiles_dir / f"{src_name}.yaml"
            if yaml_path.exists():
                loaded = self._load_yaml(yaml_path)
                # Verificação de status temporal para grounding_domains
                if src_name == "grounding_domains" and "domains" in loaded:
                    for d in loaded.get("domains", []):
                        v_until = d.get("valid_until", "")
                        if v_until:
                            try:
                                clean_dt = v_until.split("(")[0].strip()
                                dt_exp = datetime.strptime(clean_dt, "%d-%m-%Y %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=-4)))
                                if now_tz > dt_exp:
                                    d["status"] = "STALE"
                                else:
                                    d["status"] = "ACTIVE"
                            except Exception:
                                pass
                sources[src_name] = loaded

        # 2. Ingestão de Memória de Sessão (Learnings & Decisions)
        session_data_dir = self.project_root / ".vitalia" / "memory" / "session" / "data"
        sources["context_learnings"] = self._load_jsonl(session_data_dir / "learnings.jsonl")
        sources["context_decisions"] = self._load_jsonl(session_data_dir / "decisions.jsonl")

        # Estimativa simples de tokens (1 token ~ 4 caracteres)
        raw_text = json.dumps(sources, ensure_ascii=False)
        estimated_tokens = len(raw_text) // 4

        return {
            "schema_version": "1.0",
            "workflow": self.workflow_name,
            "pruning_applied": False,
            "estimated_tokens": estimated_tokens,
            "sources": sources,
            "session_context": {
                "user_input": self.user_args,
                "cwd": str(self.cwd),
                "project_root": str(self.project_root)
            }
        }
