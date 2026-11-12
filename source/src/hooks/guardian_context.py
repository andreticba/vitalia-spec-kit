#!/usr/bin/env python3
# guardian_context.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:01(GMT-04:00)
"""
Guardião de Contexto Constitucional e Compilador Sem Poda — Vitalia SPEC Kit v0.0.1

Política Incondicional de Zero Poda (FR-005 / ADR-0001):
- Todos os workflows operam com 100% da Constituição integral sem poda e dos catálogos solicitados,
  sem qualquer algoritmo ou adaptador de poda de tokens (token_budget = 0).
- Valida a janela temporal (valid_until) de grounding_domains.yaml e dynamic_questioning.yaml,
  marcando entradas expiradas como TEMPORAL_REFRESH_REQUIRED.
- Grava qualquer exportação direta exclusivamente em .vitalia/memory/data_storage/context/<machine_id>/.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap

health = kit_env_bootstrap.init()
from core.utils import get_machine_identity, get_timestamp
from hooks.domain_detector import verify_temporal_status

try:
    import yaml
except ImportError:
    yaml = None


class GuardianContextV2:
    """Compilador de Context Engineering 100% Sem Poda para os workflows do Vitalia SPEC Kit."""

    def __init__(
        self,
        workflow_name: str,
        guardian_config: Optional[Dict[str, Any]] = None,
        session_dir: Optional[Path] = None,
        cwd: Optional[Path] = None,
        user_args: str = "",
    ):
        self.workflow_name = workflow_name
        self.guardian_config = guardian_config or {}
        self.cwd = (cwd or Path.cwd()).resolve()
        self.session_dir = session_dir or (self.cwd / ".vitalia" / "memory" / "session")
        self.kit_root = kit_env_bootstrap.resolve_kit_dir(self.cwd)
        self.profiles_dir = self.kit_root / "profiles"
        self.advisory: Optional[str] = None
        self.user_args = user_args

    def _estimate_tokens(self, obj: Any) -> int:
        text = json.dumps(obj, ensure_ascii=False)
        return int(len(text.split()) * 1.3)

    def load_yaml(self, name: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Carrega um arquivo YAML de profiles/ sem poda."""
        if not yaml:
            return None, "yaml_module_missing"

        candidates = [
            self.profiles_dir / f"{name}.yaml",
            self.cwd / "source" / "profiles" / f"{name}.yaml",
            self.cwd / "profiles" / f"{name}.yaml",
        ]

        for target_path in candidates:
            if target_path.exists() and target_path.is_file():
                data = yaml.safe_load(target_path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
                schema_type = data.get("schema_type", name)
                return data, schema_type

        print(f"[Guardian] WARNING: {name}.yaml não encontrado em profiles/ ({self.profiles_dir})", file=sys.stderr)
        return None, "file_not_found"

    def resolve_profile(self) -> Dict[str, Any]:
        profile_name = self.guardian_config.get("guardian_profile")
        if profile_name:
            p_data, _ = self.load_yaml(profile_name)
            if p_data:
                return p_data

        p_data, _ = self.load_yaml(f"gp_{self.workflow_name}")
        if p_data:
            return p_data

        self.advisory = (
            f"[GUARDIAN ADVISORY: Workflow '{self.workflow_name}' sem guardian_profile dedicado "
            f"— usando constituição integral sem poda.]"
        )
        return {
            "schema_type": "guardian_profile",
            "schema_version": "0.0.1",
            "workflow": self.workflow_name,
            "hardware_profile": "frontier",
            "tokens": {"total_budget": 0, "source_weights": {"constitution": 1.0}},
            "constitution": {
                "no_prune": True,
                "domains": [],
                "severity_filter": ["BLOCKING", "WARNING", "INFO"],
                "principles_include": [],
            },
        }

    def load_session_context(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        sess_cfg = profile.get("session_context", {})
        session_ctx: Dict[str, Any] = {}

        if sess_cfg.get("include_p0", True):
            st_file = self.session_dir / "SESSION_STATE.md"
            if st_file.exists():
                lines = st_file.read_text(encoding="utf-8").splitlines()
                p0_lines = [l for l in lines if "P0" in l or "Próximo Passo" in l or "Next Step" in l]
                session_ctx["p0"] = p0_lines[0].strip() if p0_lines else "Dar continuidade à implementação planejada."
            else:
                session_ctx["p0"] = "Inicialização de sessão."

        feat_file = self.cwd / ".vitalia" / "feature.json"
        if sess_cfg.get("include_active_feature", True) and feat_file.exists():
            try:
                f_data = json.loads(feat_file.read_text(encoding="utf-8"))
                session_ctx["active_feature"] = (
                    f_data.get("feature_directory") or f_data.get("active_feature") or "Geral"
                )
            except Exception:
                session_ctx["active_feature"] = "Geral"

        handoff_storage = self.cwd / ".vitalia" / "memory" / "data_storage" / "handoffs"
        try:
            import importlib.util

            vh_path = self.kit_root / "src" / "vitalia_handoff.py"
            if not vh_path.exists():
                vh_path = self.cwd / "source" / "src" / "vitalia_handoff.py"
            if vh_path.exists():
                spec = importlib.util.spec_from_file_location("vitalia_handoff", str(vh_path))
                if spec and spec.loader:
                    vh_mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(vh_mod)
                    handoff_data = vh_mod.latest_handoff(
                        target_workflow=self.workflow_name, storage_dir=handoff_storage
                    )
                    if handoff_data:
                        session_ctx["handoff"] = handoff_data
        except Exception:
            pass

        return session_ctx

    def _load_historical_context(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"context_decisions": [], "context_learnings": []}
        for key, filename in [("context_decisions", "decisions.jsonl"), ("context_learnings", "learnings.jsonl")]:
            for base_dir in [self.session_dir / "data", self.cwd / ".vitalia" / "data"]:
                jsonl_path = base_dir / filename
                if jsonl_path.exists():
                    try:
                        lines = jsonl_path.read_text(encoding="utf-8").splitlines()
                        entries = []
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                entries.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
                        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                        result[key] = entries
                    except Exception:
                        pass
                    break
        return result

    def _load_env_summary(self) -> Dict[str, Any]:
        try:
            return kit_env_bootstrap.check_environment_health(self.cwd)
        except Exception:
            return {}

    def build_payload(self) -> Dict[str, Any]:
        profile = self.resolve_profile()
        yaml_sources = list(self.guardian_config.get("yaml_sources", ["constitution"]))
        if "constitution" not in yaml_sources:
            yaml_sources.insert(0, "constitution")

        payload_sources: Dict[str, Any] = {}
        temporal_alerts = []

        for src_name in yaml_sources:
            raw_data, _ = self.load_yaml(src_name)
            if not raw_data:
                continue

            # Verificar expiração temporal em grounding_domains e dynamic_questioning
            if src_name in ("grounding_domains", "dynamic_questioning"):
                domains_container = raw_data.get("domains")
                expired = verify_temporal_status(domains_container)
                if expired:
                    temporal_alerts.extend(expired)

            # Política Incondicional de Zero Poda: repassa 100% da fonte integralmente
            payload_sources[src_name] = raw_data

        session_ctx = self.load_session_context(profile)
        if self.user_args:
            session_ctx["user_input"] = self.user_args

        env_summary = self._load_env_summary()
        historical = self._load_historical_context()

        result_payload: Dict[str, Any] = {
            "schema_version": "0.0.1",
            "workflow": self.workflow_name,
            "timestamp": get_timestamp(),
            "sources": payload_sources,
            "phase_guardrails": profile.get("phase_guardrails", {}),
            "phase_profiles": profile.get("phase_profiles", {}),
            "session_context": session_ctx,
            "env_summary": env_summary,
            "context_decisions": historical["context_decisions"],
            "context_learnings": historical["context_learnings"],
        }

        if temporal_alerts:
            result_payload["temporal_refresh_required"] = temporal_alerts

        if self.advisory:
            result_payload["guardian_advisory"] = self.advisory

        result_payload["estimated_tokens"] = self._estimate_tokens(result_payload)
        result_payload["token_budget"] = 0

        return result_payload

    def export_and_publish(self) -> Path:
        payload = self.build_payload()
        _, machine_id = get_machine_identity()
        out_dir = self.cwd / ".vitalia" / "memory" / "data_storage" / "context" / machine_id
        out_dir.mkdir(parents=True, exist_ok=True)
        pid_hash = hashlib.sha256(f"{os.getpid()}_{self.workflow_name}".encode()).hexdigest()[:12]
        out_file = out_dir / f"guardian_{self.workflow_name}_{pid_hash}.json"
        out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return out_file


def main():
    parser = argparse.ArgumentParser(
        description="Guardião de Contexto Constitucional Sem Poda — Vitalia SPEC Kit (v0.0.1)"
    )
    parser.add_argument("--workflow", default="default", help="Nome do workflow ativo")
    parser.add_argument("--guardian-json", default="{}", help="Configuração JSON da seção [guardian] do TOML")
    parser.add_argument("--session-dir", default=None, help="Caminho do diretório de sessão")
    parser.add_argument("--cwd", default=None, help="Caminho da raiz do projeto")
    parser.add_argument("--args", default="", help="Argumentos do usuário")

    for idx in range(len(sys.argv) - 1):
        if sys.argv[idx] == "--args" and sys.argv[idx + 1].startswith("-"):
            sys.argv[idx] = f"--args={sys.argv.pop(idx + 1)}"
            break

    args = parser.parse_args()

    g_config = {}
    if args.guardian_json and args.guardian_json != "{}":
        try:
            g_config = json.loads(args.guardian_json)
        except Exception:
            pass

    cwd_path = Path(args.cwd) if args.cwd else Path.cwd()
    sess_path = Path(args.session_dir) if args.session_dir else (cwd_path / ".vitalia" / "memory" / "session")

    guardian = GuardianContextV2(
        workflow_name=args.workflow,
        guardian_config=g_config,
        session_dir=sess_path,
        cwd=cwd_path,
        user_args=args.args,
    )

    out_file = guardian.export_and_publish()
    print(f"✅ Guardian exportado para {out_file}")


if __name__ == "__main__":
    main()

