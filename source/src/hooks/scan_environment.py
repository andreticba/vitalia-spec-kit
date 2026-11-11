#!/usr/bin/env python3
# scan_environment.py | Vitalia SPEC Kit v0.0.1 | 11-11-2026 10:29(GMT-04:00)
"""
Executa a varredura do ambiente (via kit_env_bootstrap) e retorna o status em JSON.

Exit codes:
  0 — ambiente HEALTHY (sem exigência de Redis ou .venv no projeto hospedeiro)
  1 — ambiente sem .env na raiz do projeto
"""

import argparse
import json
import sys
from pathlib import Path

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap


def check_environment_health(cwd: str | Path | None = None) -> dict:
    start = Path(cwd) if cwd else None
    return kit_env_bootstrap.init(start)


def main():
    parser = argparse.ArgumentParser(
        description="Varredura de Ambiente e Diagnóstico — Vitalia SPEC Kit (v0.0.1)"
    )
    parser.add_argument("--cwd", type=str, default=None, help="Diretório de trabalho alvo para varredura do ambiente.")
    args = parser.parse_args()

    start = Path(args.cwd) if args.cwd else None
    health = kit_env_bootstrap.init(start)
    print(json.dumps(health, indent=2, ensure_ascii=False))

    if not health.get("has_env", False):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

