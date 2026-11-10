#!/usr/bin/env python3
# kit_env_bootstrap.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:00(GMT-04:00)
"""
Módulo Central de Bootstrap de Ambiente — Vitalia SPEC Kit v0.0.1

Responsabilidades:
1. Auto-descoberta do diretório raiz do projeto (workspace) subindo a árvore de pastas.
2. Parser nativo de .env (stdlib-only, sem exigência de python-dotenv no Python global).
3. Resolução determinística de VITALIA_KIT_DIR (env -> .env -> ~/.vitalia-spec-kit).
4. Injeção dinâmica do site-packages do .venv do kit (e opcionalmente do projeto) em sys.path.
5. Diagnóstico de saúde de ambiente 100% livre de containers locais (sem Redis/Docker).
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

_KIT_SCRIPTS_DIR = str(Path(__file__).parent.resolve())
if _KIT_SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _KIT_SCRIPTS_DIR)


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """Localiza a raiz do projeto subindo na hierarquia a partir de start_path ou cwd."""
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    current = start_path if start_path.is_dir() else start_path.parent
    indicators = [".vitalia", ".env", ".git", "pyproject.toml", "setup.py"]

    for _ in range(12):
        if any((current / ind).exists() for ind in indicators):
            return current
        if current.parent == current:
            break
        current = current.parent

    return start_path if start_path.is_dir() else start_path.parent


def load_dotenv_native(env_path: Path, override: bool = False) -> Dict[str, str]:
    """Parser nativo de arquivos .env (stdlib puro)."""
    loaded: Dict[str, str] = {}
    if not env_path.exists() or not env_path.is_file():
        return loaded

    try:
        content = env_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return loaded

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()

        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        elif "#" in val:
            val = val.split("#", 1)[0].strip()

        loaded[key] = val
        if override or key not in os.environ or not os.environ[key].strip():
            os.environ[key] = val

    return loaded


def resolve_kit_dir(project_root: Optional[Path] = None) -> Path:
    """
    Descobre o diretório de instalação do Vitalia SPEC Kit na ordem de precedência defensiva:
    1. Variável de ambiente VITALIA_KIT_DIR (se existir fisicamente em disco)
    2. Chave VITALIA_KIT_DIR no arquivo .env do projeto (se existir fisicamente em disco)
    3. script_kit_root onde este módulo está instalado (se contiver profiles/constitution.yaml)
    4. Padrão universal: ~/.vitalia-spec-kit (se existir em disco)
    5. Fallback final: script_kit_root
    """
    script_kit_root = Path(__file__).resolve().parent.parent

    env_val = os.environ.get("VITALIA_KIT_DIR", "").strip()
    if env_val:
        candidate = Path(os.path.expanduser(env_val)).resolve()
        if candidate.exists():
            return candidate

    if project_root is not None:
        env_file = project_root / ".env"
        if env_file.exists():
            dotenv_vars = load_dotenv_native(env_file, override=False)
            raw_kit_dir = dotenv_vars.get("VITALIA_KIT_DIR", "").strip()
            if raw_kit_dir:
                candidate = Path(os.path.expanduser(raw_kit_dir)).resolve()
                if candidate.exists():
                    return candidate

    if (script_kit_root / "profiles" / "constitution.yaml").exists():
        return script_kit_root

    default_global = (Path.home() / ".vitalia-spec-kit").resolve()
    if default_global.exists():
        return default_global

    return script_kit_root


def inject_venv(base_dir: Path) -> Tuple[bool, Optional[str]]:
    """
    Detecta pasta .venv ou venv em base_dir, localiza site-packages e injeta no sys.path.
    """
    for vname in (".venv", "venv"):
        venv_dir = base_dir / vname
        if not venv_dir.exists() or not venv_dir.is_dir():
            continue

        lib_dir = venv_dir / "lib"
        if lib_dir.exists():
            for py_dir in lib_dir.glob("python*"):
                sp = py_dir / "site-packages"
                if sp.exists() and sp.is_dir():
                    sp_str = str(sp.resolve())
                    if sp_str not in sys.path:
                        sys.path.insert(0, sp_str)
                    return True, sp_str

        sp_win = venv_dir / "Lib" / "site-packages"
        if sp_win.exists() and sp_win.is_dir():
            sp_str = str(sp_win.resolve())
            if sp_str not in sys.path:
                sys.path.insert(0, sp_str)
            return True, sp_str

    return False, None


def check_environment_health(project_root: Path) -> Dict[str, Any]:
    """
    Diagnostica a saúde do ambiente do projeto sem exigir containers locais (Redis/Postgres)
    nem .venv obrigatório no projeto hospedeiro (pois o kit possui seu próprio .venv isolado).
    """
    if isinstance(project_root, str):
        project_root = Path(project_root)

    env_file = project_root / ".env"
    has_env = env_file.exists() and env_file.is_file()

    kit_dir = resolve_kit_dir(project_root)
    kit_venv_ok, kit_venv_path = inject_venv(kit_dir)
    proj_venv_ok, proj_venv_path = inject_venv(project_root)

    venv_ok = kit_venv_ok or proj_venv_ok
    venv_path = kit_venv_path or proj_venv_path

    issues = []
    if not has_env:
        issues.append("Arquivo .env ausente na raiz do projeto")

    status = "HEALTHY" if not issues else "DEGRADED"

    return {
        "status": status,
        "project_root": str(project_root),
        "kit_dir": str(kit_dir),
        "has_env": has_env,
        "venv_ok": venv_ok,
        "venv_path": venv_path,
        "issues": issues,
    }


def init(start_path: Optional[Path] = None, auto_load_env: bool = True) -> Dict[str, Any]:
    """Ponto de entrada padrão para qualquer script/hook do Vitalia SPEC Kit."""
    root = find_project_root(start_path)

    if auto_load_env:
        env_file = root / ".env"
        if env_file.exists():
            load_dotenv_native(env_file, override=False)

    kit_dir = resolve_kit_dir(root)
    inject_venv(kit_dir)
    inject_venv(root)
    return check_environment_health(root)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bootstrap Central de Ambiente — Vitalia SPEC Kit v0.0.1")
    parser.add_argument("--cwd", default=None, help="Diretório de início para busca da raiz do projeto")
    args = parser.parse_args()

    start = Path(args.cwd) if args.cwd else None
    health_info = init(start)
    print(f"[kit_env_bootstrap] Project Root: {health_info['project_root']}")
    print(f"[kit_env_bootstrap] Kit Dir: {health_info['kit_dir']}")
    print(f"[kit_env_bootstrap] Status: {health_info['status']}")

