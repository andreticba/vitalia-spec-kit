#!/usr/bin/env python3
# scan_environment.py | Vitalia SPEC Kit v0.0.1 | 15-11-2026 13:58(GMT-04:00)
"""
Executa a varredura do ambiente (via kit_env_bootstrap) e retorna o status em JSON,
incluindo a métrica ultraleve de observabilidade context_cleanup (FR-005.2 / OpenAPI 3.0 Limpo).

Exit codes:
  0 — ambiente HEALTHY
  1 — ambiente sem .env na raiz do projeto
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap

CUIABA_TZ = datetime.timezone(datetime.timedelta(hours=-4))
FILENAME_DATE_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+_(\d{4})(\d{2})(\d{2})_\d{6}_[a-zA-Z0-9]+\.json$")


def scan_context_cleanup(project_root: Path) -> Dict[str, Any]:
    """
    Sonda ultraleve (< 50ms) de arquivos transitórios de contexto em
    .vitalia/memory/data_storage/context/.
    Gera contrato OpenAPI 3.0 Limpo para observabilidade e health checks.
    """
    context_root = project_root / ".vitalia" / "memory" / "data_storage" / "context"
    total_files = 0
    eligible_files = 0
    eligible_bytes = 0

    if not context_root.exists() or not context_root.is_dir():
        return {
            "total_files": 0,
            "eligible_files": 0,
            "eligible_bytes": 0,
            "needs_cleanup": False,
        }

    today = datetime.datetime.now(CUIABA_TZ).date()

    try:
        # Itera pelas máquinas/subdiretórios com os.scandir (alta performance)
        for machine_entry in os.scandir(context_root):
            if machine_entry.is_dir(follow_symlinks=False):
                try:
                    for f_entry in os.scandir(machine_entry.path):
                        if f_entry.is_file(follow_symlinks=False) and f_entry.name.endswith(".json"):
                            total_files += 1
                            match = FILENAME_DATE_REGEX.match(f_entry.name)
                            is_today = False
                            if match:
                                y, m, d = map(int, match.groups())
                                try:
                                    f_date = datetime.date(y, m, d)
                                    is_today = (f_date == today)
                                except ValueError:
                                    pass
                            else:
                                try:
                                    mtime = f_entry.stat().st_mtime
                                    f_date = datetime.datetime.fromtimestamp(mtime, tz=CUIABA_TZ).date()
                                    is_today = (f_date == today)
                                except OSError:
                                    pass

                            if not is_today:
                                eligible_files += 1
                                try:
                                    eligible_bytes += f_entry.stat().st_size
                                except OSError:
                                    pass
                except OSError:
                    continue
            elif machine_entry.is_file(follow_symlinks=False) and machine_entry.name.endswith(".json"):
                total_files += 1
                match = FILENAME_DATE_REGEX.match(machine_entry.name)
                is_today = False
                if match:
                    y, m, d = map(int, match.groups())
                    try:
                        f_date = datetime.date(y, m, d)
                        is_today = (f_date == today)
                    except ValueError:
                        pass
                else:
                    try:
                        mtime = machine_entry.stat().st_mtime
                        f_date = datetime.datetime.fromtimestamp(mtime, tz=CUIABA_TZ).date()
                        is_today = (f_date == today)
                    except OSError:
                        pass

                if not is_today:
                    eligible_files += 1
                    try:
                        eligible_bytes += machine_entry.stat().st_size
                    except OSError:
                        pass
    except OSError:
        pass

    return {
        "total_files": total_files,
        "eligible_files": eligible_files,
        "eligible_bytes": eligible_bytes,
        "needs_cleanup": (eligible_files > 0),
    }


def check_environment_health(cwd: str | Path | None = None) -> dict:
    start = Path(cwd) if cwd else None
    health = kit_env_bootstrap.init(start)
    root = Path(health.get("project_root", cwd or "."))
    health["context_cleanup"] = scan_context_cleanup(root)
    return health


def main():
    parser = argparse.ArgumentParser(
        description="Varredura de Ambiente e Diagnóstico — Vitalia SPEC Kit (v0.0.1)"
    )
    parser.add_argument("--cwd", type=str, default=None, help="Diretório de trabalho alvo para varredura do ambiente.")
    args = parser.parse_args()

    start = Path(args.cwd) if args.cwd else None
    health = kit_env_bootstrap.init(start)
    root = Path(health.get("project_root", args.cwd or "."))
    health["context_cleanup"] = scan_context_cleanup(root)

    print(json.dumps(health, indent=2, ensure_ascii=False))

    if not health.get("has_env", False):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
