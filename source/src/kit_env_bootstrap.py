#!/usr/bin/env python3
# kit_env_bootstrap.py | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:08(GMT-04:00)
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
    3. Padrão universal: ~/.vitalia-spec-kit (se existir em disco)
    4. Fallback defensivo: script_kit_root (se contiver profiles/constitution.yaml)
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

    default_global = (Path.home() / ".vitalia-spec-kit").resolve()
    if default_global.exists():
        return default_global

    if (script_kit_root / "profiles" / "constitution.yaml").exists():
        return script_kit_root

    return script_kit_root


def resolve_kit_python(kit_dir: Path) -> Path:
    """
    Localiza o binário do interpretador Python isolado do kit (${VITALIA_KIT_DIR}/.venv).
    Suporta convenções POSIX (bin/python3, bin/python) e Windows (Scripts/python.exe, Scripts/python3.exe).
    Retorna o caminho absoluto sem seguir symlinks para preservar o sys.prefix de PEP 405.
    Fallback defensivo para sys.executable.
    """
    venv_dir = kit_dir / ".venv"
    candidates = [
        venv_dir / "bin" / "python3",
        venv_dir / "bin" / "python",
        venv_dir / "Scripts" / "python.exe",
        venv_dir / "Scripts" / "python3.exe",
    ]
    for c in candidates:
        if c.exists() and (os.access(c, os.X_OK) or os.name == "nt"):
            return Path(os.path.abspath(c))
    return Path(os.path.abspath(sys.executable))


def _resolve_venv_python_bin(venv_dir: Path) -> Optional[Path]:
    """Helper interno para localizar o executável python dentro de uma pasta venv."""
    candidates = [
        venv_dir / "bin" / "python3",
        venv_dir / "bin" / "python",
        venv_dir / "Scripts" / "python.exe",
        venv_dir / "Scripts" / "python3.exe",
    ]
    for c in candidates:
        if c.exists() and (os.access(c, os.X_OK) or os.name == "nt"):
            return Path(os.path.abspath(c))
    return None


def find_project_python_details(project_root: Optional[Path] = None) -> Tuple[bool, Optional[str], str]:
    """
    Algoritmo de descoberta em 4 níveis do ambiente virtual do projeto (FR-001.2 / cli-contracts.md):
    1. $VIRTUAL_ENV ativo no ambiente -> ("shell_env")
    2. Chave PROJECT_VENV_PATH no .env da raiz do projeto -> ("dotenv_config")
    3. Varredura por pastas canônicas (.venv, venv, env, .env_py) na raiz do projeto -> ("canonical_folder")
    4. Resolução determinística do executável POSIX ou Windows sem seguir symlinks.
    Retorna: (has_venv: bool, python_bin: Optional[str], source_detected: str)
    """
    # Nível 1: $VIRTUAL_ENV ativo no shell
    env_virtual_env = os.environ.get("VIRTUAL_ENV", "").strip()
    if env_virtual_env:
        vpath = Path(os.path.expanduser(env_virtual_env))
        py_bin = _resolve_venv_python_bin(vpath)
        if py_bin:
            return True, str(py_bin), "shell_env"

    if project_root is None:
        project_root = find_project_root()
    else:
        project_root = Path(project_root).resolve()

    # Nível 2: Chave PROJECT_VENV_PATH no .env do projeto
    env_file = project_root / ".env"
    if env_file.exists():
        dotenv_vars = load_dotenv_native(env_file, override=False)
        proj_venv_raw = dotenv_vars.get("PROJECT_VENV_PATH", "").strip()
        if proj_venv_raw:
            raw_path = Path(os.path.expanduser(proj_venv_raw))
            if not raw_path.is_absolute():
                candidate_venv = (project_root / raw_path).resolve()
            else:
                candidate_venv = raw_path.resolve()
            py_bin = _resolve_venv_python_bin(candidate_venv)
            if py_bin:
                return True, str(py_bin), "dotenv_config"

    # Nível 3 & 4: Varredura por diretórios canônicos locais na raiz do projeto
    canonical_names = [".venv", "venv", "env", ".env_py"]
    for cname in canonical_names:
        candidate_venv = project_root / cname
        if candidate_venv.exists() and candidate_venv.is_dir():
            py_bin = _resolve_venv_python_bin(candidate_venv)
            if py_bin:
                return True, str(py_bin), "canonical_folder"

    return False, None, "not_found"


def find_project_python(project_root: Optional[Path] = None) -> Optional[Path]:
    """Retorna a instância Path do executável python do projeto ou None se não encontrado."""
    has_venv, py_str, _ = find_project_python_details(project_root)
    if has_venv and py_str:
        return Path(py_str)
    return None


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
    Diagnostica a saúde do ambiente em formato estruturado OpenAPI 3.0 segregado (FR-001.3 / P15):
    - kit_runtime: saúde do interpretador do kit e integridade dos pacotes essenciais
    - project_runtime: descoberta em 4 níveis do ambiente virtual da aplicação hospedeira
    """
    if isinstance(project_root, str):
        project_root = Path(project_root)

    env_file = project_root / ".env"
    has_env = env_file.exists() and env_file.is_file()

    kit_dir = resolve_kit_dir(project_root)
    kit_py = resolve_kit_python(kit_dir)
    inject_venv(kit_dir)
    inject_venv(project_root)

    has_proj_venv, proj_py, source_detected = find_project_python_details(project_root)

    issues = []
    if not has_env:
        issues.append("Arquivo .env ausente na raiz do projeto")

    # Auditoria de integridade de pacotes do kit (FR-001.1)
    kit_status = "HEALTHY"
    try:
        import yaml, jinja2, jsonschema  # noqa: F401
    except ImportError as e:
        kit_status = "DEGRADED"
        issues.append(f"Pacotes essenciais do kit ausentes no interpretador {kit_py}: {e}")

    status = "HEALTHY" if not issues else "DEGRADED"

    return {
        "status": status,
        "project_root": str(project_root),
        "kit_dir": str(kit_dir),
        "kit_runtime": {
            "kit_dir": str(kit_dir),
            "python_bin": str(kit_py),
            "status": kit_status,
        },
        "project_runtime": {
            "project_root": str(project_root),
            "has_venv": has_proj_venv,
            "python_bin": proj_py,
            "source_detected": source_detected,
        },
        "has_env": has_env,
        "issues": issues,
    }

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

