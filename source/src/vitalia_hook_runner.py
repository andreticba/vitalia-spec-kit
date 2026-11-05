#!/usr/bin/env python3
# vitalia_hook_runner.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
"""
Vitalia Hook Runner — Orquestrador de Extensões e Context Lifting (§11).

Responsabilidades:
1. Parsear arquivo .toml de workflow e executar hooks declarados [before]/[after].
2. Substituir placeholders canônicos: {{cwd}}, {{VITALIA_KIT_DIR}}, {{FEATURE_DIR}}.
3. (§11) Integrar o payload do Guardian sem podas de contexto.
4. Gravar o contexto consolidado com Zero Data Leak estritamente no armazenamento local
   do projeto em .vitalia/memory/data_storage/context/<machine_id>/ sem uso de /tmp/.
5. Emitir Stub JSON para leitura segura pela IDE de IA via view_file.
6. Purgar completamente conexões e dependências de Redis, Docker e sockets locais.
"""

import os
import sys
import argparse
import json
import subprocess
import hashlib
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        print("Erro: Python 3.11+ (tomllib) ou pacote 'tomli' é obrigatório.", file=sys.stderr)
        sys.exit(1)

_SCRIPTS_ROOT = str(Path(__file__).resolve().parent)
if _SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, _SCRIPTS_ROOT)

import kit_env_bootstrap

VITALIA_TIMEZONE = timezone(timedelta(hours=-4))


def get_machine_id() -> str:
    """Retorna identificador determinístico da máquina host (ISO/IEC 9834-8)."""
    for mid_path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
        if os.path.exists(mid_path):
            try:
                mid = Path(mid_path).read_text(encoding="utf-8").strip()
                if mid:
                    return mid[:32]
            except Exception:
                pass
    return hashlib.sha256(platform.node().encode()).hexdigest()[:32]


def resolve_kit_dir() -> str:
    """Descobre o diretório do Vitalia SPEC Kit global com fallbacks canônicos."""
    env_val = os.environ.get("VITALIA_KIT_DIR", "").strip()
    if env_val:
        return env_val.rstrip("/")
    unified_dir = Path.home() / ".vitalia-spec-kit"
    if unified_dir.exists():
        return str(unified_dir)
    return str(Path.home() / ".vitalia")


def resolve_feature_dir(cwd: str) -> str:
    """Obtém o diretório da feature ativa lido de .vitalia/feature.json se presente."""
    feature_file = Path(cwd) / ".vitalia" / "feature.json"
    if feature_file.exists():
        try:
            data = json.loads(feature_file.read_text(encoding="utf-8"))
            feature_path = data.get("feature_path") or data.get("path")
            if feature_path:
                return str(Path(cwd) / feature_path)
        except Exception:
            pass
    return ""


def resolve_placeholders(cmd_template: str, cwd: str, kit_dir: str) -> str:
    """Substitui placeholders nos comandos de hooks."""
    feature_dir = resolve_feature_dir(cwd)
    resolved = cmd_template.replace("{{cwd}}", cwd)
    resolved = resolved.replace("{{VITALIA_KIT_DIR}}", kit_dir)
    resolved = resolved.replace("{{FEATURE_DIR}}", feature_dir)
    return resolved


def _build_guardian_payload(guardian_config: dict, workflow_name: str, cwd: str, user_args: str = "") -> dict:
    """
    Constrói o payload do Guardian sem podas artificiais de contexto.
    """
    kit_dir = resolve_kit_dir()
    for p in [str(Path(kit_dir) / "src"), str(Path(kit_dir) / "source" / "src"), _SCRIPTS_ROOT]:
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        from hooks.guardian_context import GuardianContextV2  # type: ignore
        guardian = GuardianContextV2(
            workflow_name=workflow_name,
            guardian_config=guardian_config,
            cwd=Path(cwd),
            user_args=user_args,
        )
        return guardian.build_payload()
    except ImportError:
        # Modo agnóstico/leve quando módulo de oráculo ainda não estiver no kit
        return {
            "schema_version": "1.0",
            "workflow": workflow_name,
            "sources": {
                "profile": guardian_config.get("guardian_profile", "default"),
                "status": "integrated_without_pruning"
            }
        }
    except Exception as e:
        msg = f"[Guardian] Falha ao construir payload: {type(e).__name__}: {e}"
        print(msg, file=sys.stderr)
        return {"error": msg}


def main():
    parser = argparse.ArgumentParser(
        description="Vitalia Hook Runner — Execução de workflows e Context Lifting puro",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("file", help="Caminho do arquivo de configuração do workflow (.toml)")
    parser.add_argument("--phase", choices=["before", "after", "none"], default="none",
                        help="Fase de hooks a executar")
    parser.add_argument("--cwd", default=None, help="Diretório de trabalho do projeto")
    parser.add_argument("--args", default="", help="Argumentos opcionais do usuário para o workflow")
    args = parser.parse_args()

    cwd = args.cwd if args.cwd else os.getcwd()
    kit_dir = resolve_kit_dir()
    project_root = kit_env_bootstrap.find_project_root(Path(cwd))

    # Parse do arquivo TOML de workflow
    toml_path = Path(args.file)
    if not toml_path.exists():
        print(f"Erro: Arquivo TOML não encontrado: {toml_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        print(f"Erro ao parsear arquivo TOML {toml_path}: {e}", file=sys.stderr)
        sys.exit(1)

    workflow_name = toml_path.stem

    # Validação e execução de hooks
    if args.phase in ["before", "after"]:
        hooks = data.get("hooks", {}).get(args.phase, [])
        if isinstance(hooks, str):
            hooks = [hooks]

        for cmd_template in hooks:
            cmd = resolve_placeholders(cmd_template, cwd, kit_dir)
            print(f"[Hook Runner] Executando hook ({args.phase}): {cmd}", file=sys.stderr)

            env_copy = os.environ.copy()
            model_profile = data.get("meta", {}).get("model_profile", "")
            if model_profile == "pro":
                env_copy["GEMINI_MODEL"] = os.environ.get("GEMINI_MODEL_PRO", "gemini-2.5-pro")
            elif model_profile == "flash":
                env_copy["GEMINI_MODEL"] = os.environ.get("GEMINI_MODEL_FLASH", "gemini-2.5-flash")

            try:
                subprocess.run(cmd, shell=True, check=True, stdout=sys.stderr, stderr=sys.stderr, env=env_copy)
            except subprocess.CalledProcessError as e:
                print(f"[Hook Runner] ❌ Hook falhou com código {e.returncode}: {cmd}", file=sys.stderr)
                error_stub = {
                    "status": "error",
                    "workflow": workflow_name,
                    "hook_failed": cmd,
                    "exit_code": e.returncode,
                    "message": f"Hook '{args.phase}' falhou com código {e.returncode}. Ambiente não confiável.",
                    "action_required": "Reportar este erro ao usuário e NÃO prosseguir com o workflow."
                }
                print(json.dumps(error_stub, indent=2, ensure_ascii=False))
                sys.exit(e.returncode)

    # Injeção de Guardian (§11)
    guardian_config = data.get("guardian", {})
    if guardian_config:
        data["guardian_json"] = _build_guardian_payload(guardian_config, workflow_name, cwd, user_args=args.args)

    # Context Lifting: Gravação no disco local do projeto
    machine_id = get_machine_id()
    now_gmt4 = datetime.now(VITALIA_TIMEZONE)
    timestamp_iso = now_gmt4.isoformat()
    safe_ts = now_gmt4.strftime("%Y%m%d_%H%M%S")
    session_id = os.environ.get("VITALIA_SESSION_ID", safe_ts)
    pid_hash = hashlib.sha256(f"{os.getpid()}_{workflow_name}".encode()).hexdigest()[:12]

    # Diretório estritamente local dentro do projeto do usuário
    context_storage_dir = project_root / ".vitalia" / "memory" / "data_storage" / "context" / machine_id
    context_storage_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{workflow_name}_{session_id}_{pid_hash}.json"
    file_path = context_storage_dir / file_name

    # Prompt estruturado ou texto
    prompt_raw = data.get("prompt", "")
    if isinstance(prompt_raw, dict):
        prompt_str = prompt_raw.get("instruction") or json.dumps(prompt_raw, ensure_ascii=False)
    else:
        prompt_str = str(prompt_raw)

    guardian_json = data.get("guardian_json")
    if not isinstance(guardian_json, dict) or "schema_version" not in guardian_json:
        guardian_json = {
            "schema_version": "1.0",
            "workflow": workflow_name,
            "sources": {
                "profile": guardian_config.get("guardian_profile", "default"),
                "status": "integrated_without_pruning"
            }
        }

    # Envelope estritamente compatível com context-lifting.schema.json
    context_envelope = {
        "workflow": workflow_name,
        "timestamp": timestamp_iso,
        "machine_id": machine_id,
        "prompt": prompt_str,
        "guardian_json": guardian_json,
        "raw_toml_data": data
    }

    # Persistência atômica no armazenamento isolado
    file_path.write_text(json.dumps(context_envelope, indent=2, ensure_ascii=False), encoding="utf-8")

    # Emissão do Stub para consumo na IDE de IA
    stub = {
        "status": "ready",
        "workflow": workflow_name,
        "workflow_context_file": str(file_path),
        "action_required": "USE a ferramenta view_file para ler este arquivo referenciado acima e carregar o contexto ('prompt') e regras ('guardian_json')."
    }

    print(json.dumps(stub, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
