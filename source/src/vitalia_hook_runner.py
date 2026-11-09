#!/usr/bin/env python3
# vitalia_hook_runner.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:01(GMT-04:00)
"""
Vitalia Hook Runner — Ponte entre o Vitalia SPEC Kit e a IDE Antigravity.

Responsabilidades:
1. Parsear um arquivo .toml de workflow.
2. Executar hooks [before]/[after] declarados no TOML.
3. Substituir placeholders em templates de comando: {{cwd}}, {{VITALIA_KIT_DIR}}, {{FEATURE_DIR}}.
4. (§11) Construir e injetar o payload integral (sem poda) do Guardian no campo 'guardian_json'.
5. Persistir o envelope exclusivamente em .vitalia/memory/data_storage/context/<machine_id>/ (Zero Data Leak).
"""

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Erro: Este script requer Python 3.11+ (tomllib) ou o pacote 'tomli'.", file=sys.stderr)
        sys.exit(1)

_SRC_DIR = str(Path(__file__).resolve().parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import kit_env_bootstrap


def resolve_kit_dir(cwd: Optional[str] = None) -> str:
    start = Path(cwd) if cwd else Path.cwd()
    return str(kit_env_bootstrap.resolve_kit_dir(start))


def _get_machine_id() -> str:
    mname = os.environ.get("VITALIA_MACHINE_NAME") or socket.gethostname().lower() or "unknown"
    return hashlib.sha256(mname.encode("utf-8")).hexdigest()[:8]


def _build_guardian_payload(guardian_config: dict, workflow_name: str, cwd: str, user_args: str = "") -> dict:
    kit_dir = resolve_kit_dir(cwd)
    kit_src = str(Path(kit_dir) / "src")
    if kit_src not in sys.path:
        sys.path.insert(0, kit_src)

    try:
        from hooks.guardian_context import GuardianContextV2

        guardian = GuardianContextV2(
            workflow_name=workflow_name,
            guardian_config=guardian_config,
            cwd=Path(cwd),
            user_args=user_args,
        )
        return guardian.build_payload()
    except Exception as e:
        msg = f"[Guardian] Falha ao construir payload: {type(e).__name__}: {e}"
        print(msg, file=sys.stderr)
        return {"error": msg}


def resolve_placeholders(cmd_template: str, cwd: str, kit_dir: str) -> str:
    cmd = cmd_template
    cmd = cmd.replace("{{cwd}}", cwd)
    cmd = cmd.replace("{{VITALIA_KIT_DIR}}", kit_dir)

    if "{{FEATURE_DIR}}" in cmd:
        feature_json = Path(cwd) / ".vitalia" / "feature.json"
        feature_dir = ""
        if feature_json.exists():
            try:
                with open(feature_json, encoding="utf-8") as f:
                    feature_data = json.load(f)
                feature_dir = feature_data.get("feature_directory", "")
            except (json.JSONDecodeError, OSError):
                pass
        cmd = cmd.replace("{{FEATURE_DIR}}", feature_dir)

    return cmd


def main():
    parser = argparse.ArgumentParser(description="Vitalia Hook Runner — Ponte Kit ↔ IDE (v0.0.1)")
    parser.add_argument("file", help="Caminho para o arquivo .toml do workflow")
    parser.add_argument(
        "--phase",
        choices=["before", "after", "none"],
        default="none",
        help="Fase dos hooks a executar.",
    )
    parser.add_argument(
        "--args",
        default="",
        help="Input textual do usuário injetado em guardian_json.session_context.user_input.",
    )

    for idx in range(len(sys.argv) - 1):
        if sys.argv[idx] == "--args" and sys.argv[idx + 1].startswith("-"):
            sys.argv[idx] = f"--args={sys.argv.pop(idx + 1)}"
            break

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Erro: Arquivo não encontrado: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.file, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        print(f"Erro ao fazer parse do TOML: {e}", file=sys.stderr)
        sys.exit(1)

    cwd = os.getcwd()
    kit_env_bootstrap.init(Path(cwd))
    kit_dir = resolve_kit_dir(cwd)
    workflow_name = Path(args.file).stem

    # Validação pré-hook de handoff local (se presente)
    if args.phase == "before":
        try:
            import importlib.util

            vh_path = Path(kit_dir) / "src" / "vitalia_handoff.py"
            if not vh_path.exists():
                vh_path = Path(cwd) / "source" / "src" / "vitalia_handoff.py"
            if vh_path.exists():
                spec = importlib.util.spec_from_file_location("vitalia_handoff", str(vh_path))
                if spec and spec.loader:
                    vh_mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(vh_mod)
                    handoff_storage = Path(cwd) / ".vitalia" / "memory" / "data_storage" / "handoffs"
                    pending_h = vh_mod.get_latest_pending_handoff(
                        storage_dir=handoff_storage, target_workflow=workflow_name
                    )
                    if pending_h:
                        payload = vh_mod.validate_handoff_file(pending_h)
                        direction = payload.get("envelope", {}).get("direction")
                        h_id = payload.get("envelope", {}).get("handoff_id", "")[:8]
                        if direction not in ("forward", "reverse", "fallback"):
                            raise ValueError(f"Handoff {pending_h.name} com direction inválida: {direction}")
                        print(
                            f"[Hook Runner] 📦 Handoff validado com sucesso (id={h_id}, direction={direction})",
                            file=sys.stderr,
                        )
        except Exception as e:
            print(f"[Hook Runner] INFO Handoff: {e}", file=sys.stderr)

    # Executar hooks da fase solicitada
    if args.phase in ["before", "after"]:
        hooks = data.get("hooks", {}).get(args.phase, [])
        if isinstance(hooks, str):
            hooks = [hooks]

        for cmd_template in hooks:
            cmd = resolve_placeholders(cmd_template, cwd, kit_dir)
            print(f"[Hook Runner] Executando hook ({args.phase}): {cmd}", file=sys.stderr)

            env_copia = os.environ.copy()
            env_copia["VITALIA_KIT_DIR"] = kit_dir
            model_profile = data.get("meta", {}).get("model_profile", "")
            if model_profile == "pro":
                gemini_model = os.environ.get("GEMINI_MODEL_PRO", "gemini-3.1-pro-preview")
                env_copia["GEMINI_MODEL"] = gemini_model
            elif model_profile == "flash":
                gemini_model = os.environ.get("GEMINI_MODEL_FLASH", "gemini-3.6-flash")
                env_copia["GEMINI_MODEL"] = gemini_model

            try:
                subprocess.run(cmd, shell=True, check=True, stdout=sys.stderr, stderr=sys.stderr, env=env_copia)
            except subprocess.CalledProcessError as e:
                print(f"[Hook Runner] ❌ Hook falhou com código {e.returncode}: {cmd}", file=sys.stderr)
                error_stub = {
                    "status": "error",
                    "workflow": workflow_name,
                    "hook_failed": cmd,
                    "exit_code": e.returncode,
                    "message": f"Hook '{args.phase}' falhou com código {e.returncode}. Ambiente não confiável.",
                    "action_required": "Reportar este erro ao usuário e NÃO prosseguir com o workflow.",
                }
                print(json.dumps(error_stub, indent=2, ensure_ascii=False))
                sys.exit(e.returncode)

    # §11 — Injetar guardian_json (100% sem poda, sem tmp_cleanup_matrix)
    guardian_config = data.get("guardian", {})
    if guardian_config:
        if "hardware_profile" not in guardian_config and "hardware_profile" in data.get("meta", {}):
            guardian_config["hardware_profile"] = data["meta"]["hardware_profile"]
        print(f"[Hook Runner] §11 — Construindo payload Guardian para '{workflow_name}'...", file=sys.stderr)
        guardian_payload = _build_guardian_payload(
            guardian_config,
            workflow_name,
            cwd,
            user_args=args.args,
        )
        data["guardian_json"] = guardian_payload
        tokens = guardian_payload.get("estimated_tokens", "?")
        print(f"[Hook Runner] §11 — Payload Guardian pronto (~{tokens} tokens).", file=sys.stderr)

    # Garantir prompt sincronizado no topo do envelope, em [guardian] e em [transport]
    prompt_val = data.get("prompt")
    if not prompt_val and isinstance(data.get("guardian"), dict):
        prompt_val = data["guardian"].get("prompt")
    if not prompt_val and isinstance(data.get("transport"), dict):
        prompt_val = data["transport"].get("prompt")
    if prompt_val:
        data["prompt"] = prompt_val
        if isinstance(data.get("guardian"), dict) and "prompt" not in data["guardian"]:
            data["guardian"]["prompt"] = prompt_val

    # Persistência isolada por projeto e máquina (Zero Data Leak — FR-004)
    vitalia_tz = timezone(timedelta(hours=-4))
    safe_ts = datetime.now(vitalia_tz).strftime("%Y%m%d_%H%M%S")
    session_id = os.environ.get("VITALIA_SESSION_ID", safe_ts)
    pid_hash = hashlib.sha256(f"{os.getpid()}_{workflow_name}_{safe_ts}".encode()).hexdigest()[:12]
    machine_id = _get_machine_id()

    context_dir = Path(cwd) / ".vitalia" / "memory" / "data_storage" / "context" / machine_id
    context_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{workflow_name}_{session_id}_{pid_hash}.json"
    file_path = context_dir / file_name
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    stub = {
        "status": "ready",
        "workflow": workflow_name,
        "workflow_context_file": str(file_path),
        "action_required": "USE a ferramenta view_file para ler este arquivo referenciado acima e carregar o contexto ('prompt') e regras ('guardian_json').",
    }
    print(json.dumps(stub, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
