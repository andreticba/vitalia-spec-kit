#!/usr/bin/env python3
# kit_env_bootstrap.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
"""
Módulo de Bootstrap e Diagnóstico de Ambiente — Vitalia SPEC Kit v0.0.1

Responsabilidades:
1. Auto-descoberta determinística do diretório raiz do projeto (workspace).
2. Parser nativo de .env (stdlib puro, sem dependências externas).
3. Diagnóstico de saúde do ambiente desacoplado de infraestrutura local:
   - Presença de .env no projeto
   - Verificação da integridade do runtime isolado (VITALIA_KIT_DIR/.venv)
   - Purga total de dependências de sockets TCP locais (Redis 6379, Postgres 5432, Docker).
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any

# Garante inclusão do diretório do kit em sys.path
_SRC_DIR = str(Path(__file__).parent.resolve())
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    Localiza a raiz do projeto subindo na hierarquia a partir de start_path ou cwd.
    Critérios de parada: presença de .vitalia, .git, .env, pyproject.toml ou setup.py.
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    current = start_path if start_path.is_dir() else start_path.parent
    indicators = [".vitalia", ".git", ".env", "pyproject.toml", "setup.py"]

    for _ in range(12):
        if any((current / ind).exists() for ind in indicators):
            return current
        if current.parent == current:
            break
        current = current.parent

    return start_path if start_path.is_dir() else start_path.parent


def load_dotenv_native(env_path: Path, override: bool = False) -> Dict[str, str]:
    """
    Parser nativo de arquivos .env (stdlib puro).
    """
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
        else:
            if "#" in val:
                val = val.split("#", 1)[0].strip()

        loaded[key] = val
        if override or key not in os.environ:
            os.environ[key] = val

    return loaded


def resolve_kit_dir(project_root: Optional[Path] = None) -> Path:
    """
    Resolve o diretório do kit global estritamente em tempo de execução:
    1. os.environ['VITALIA_KIT_DIR']
    2. Leitura nativa de .env do projeto hospedeiro
    3. Diretório pai do script se estiver rodando dentro do kit instalado
    Zero caminhos hardcoded. Lança RuntimeError se não for possível resolver.
    """
    # 1. os.environ
    env_val = os.environ.get("VITALIA_KIT_DIR")
    if env_val:
        p = Path(env_val).expanduser().resolve()
        if p.exists() and p.is_dir():
            return p

    # 2. .env do projeto hospedeiro
    root = project_root or find_project_root()
    env_file = root / ".env"
    if env_file.exists():
        parsed = load_dotenv_native(env_file)
        if "VITALIA_KIT_DIR" in parsed and parsed["VITALIA_KIT_DIR"]:
            p = Path(parsed["VITALIA_KIT_DIR"]).expanduser().resolve()
            if p.exists() and p.is_dir():
                return p

    # 3. Diretório pai do script se executado a partir do kit global
    script_parent = Path(__file__).resolve().parent.parent
    if (script_parent / "extensions").is_dir() and (script_parent / "bin").is_dir():
        return script_parent

    raise RuntimeError(
        "VITALIA_KIT_DIR não definido no ambiente nem no .env do projeto. "
        "Defina VITALIA_KIT_DIR ou instale o kit via kit-bootstrap.sh."
    )


def check_environment_health(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Diagnostica a integridade do ambiente do projeto conforme o contrato
    specs/002-universal-bootstrap-runtime/contracts/scan-environment.schema.json.
    Desacoplado de qualquer sonda de rede ou serviço externo.
    """
    if project_root is None:
        project_root = find_project_root()
    else:
        project_root = Path(project_root).resolve()

    env_file = project_root / ".env"
    has_env = env_file.exists() and env_file.is_file()

    # Validação do runtime isolado global do kit via resolução dinâmica
    kit_dir: Optional[Path] = None
    issues: List[str] = []

    try:
        kit_dir = resolve_kit_dir(project_root)
        venv_python = kit_dir / ".venv" / "bin" / "python3"
        runtime_isolated_ok = venv_python.exists() and os.access(venv_python, os.X_OK)
    except RuntimeError as err:
        runtime_isolated_ok = False
        issues.append(str(err))

    if not has_env:
        issues.append("Arquivo .env ausente na raiz do projeto")
    if kit_dir and not runtime_isolated_ok:
        issues.append(f"Runtime isolado inoperante em {kit_dir / '.venv' / 'bin' / 'python3'}")

    if not issues:
        status = "HEALTHY"
    elif not has_env or not runtime_isolated_ok:
        status = "DEGRADED"
    else:
        status = "CRITICAL"

    return {
        "status": status,
        "project_root": str(project_root),
        "has_env": has_env,
        "runtime_isolated_ok": bool(runtime_isolated_ok),
        "issues": issues,
    }


def init(cwd: Optional[str] = None) -> Dict[str, Any]:
    """Inicialização rápida e varredura do projeto."""
    root = find_project_root(Path(cwd) if cwd else None)
    env_file = root / ".env"
    if env_file.exists():
        load_dotenv_native(env_file)
    return check_environment_health(root)
