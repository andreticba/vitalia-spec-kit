#!/usr/bin/env python3
# sensor_path_hygiene.py | Vitalia SDD v0.6.0 | 10-11-2026 16:20(GMT-04:00)
"""
Vitalia Runtime Sensor Suite (VRSS) — Sensor de Higiene de Caminhos.
Varre arquivos de código, scripts, schemas e prompts em busca de ocorrências
proibidas de caminhos físicos absolutos ou nomes de máquinas hardcoded.

Exemplos de Uso Didático:
  python3 sensor_path_hygiene.py --scan-dir source/
  python3 sensor_path_hygiene.py --scan-dir .
"""

import argparse
import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    (re.compile(r"/home/[a-zA-Z0-9_-]+/\.vitalia"), "Caminho hardcoded de diretório legado home"),
    (re.compile(r"/home/[a-zA-Z0-9_-]+/projetos"), "Caminho absoluto local de workspace"),
]

ALLOWED_EXTENSIONS = {".py", ".sh", ".toml", ".json", ".yaml", ".yml"}


def audit_path_hygiene(scan_dir: Path) -> int:
    if not scan_dir.exists():
        print(f"[Sensor Higiene de Caminhos] ❌ Diretório não encontrado: {scan_dir}", file=sys.stderr)
        return 1

    violations = []
    files_checked = 0

    for item in scan_dir.rglob("*"):
        if not item.is_file():
            continue
        if item.suffix not in ALLOWED_EXTENSIONS:
            continue
        # Pular testes, arquivos de log, backups e ambientes virtuais
        parts = item.parts
        if any(p in parts for p in (".venv", "venv", "__pycache__", ".git", "backups", "tests")):
            continue

        try:
            content = item.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        files_checked += 1
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            line_str = line.strip()
            # Ignorar comentários puros de documentação que citam paths apenas como exemplo
            if line_str.startswith("#") or line_str.startswith("//") or line_str.startswith("<!--"):
                continue

            for pattern, reason in FORBIDDEN_PATTERNS:
                match = pattern.search(line)
                if match:
                    violations.append(f"{item.relative_to(scan_dir)}:{idx} — {reason}: '{match.group(0)}'")

    if violations:
        print(f"[Sensor Higiene de Caminhos] ❌ FALHA: {len(violations)} caminhos hardcoded detectados:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print(f"[Sensor Higiene de Caminhos] ✅ SUCESSO: {files_checked} arquivos auditados com 0 caminhos hardcoded.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="VRSS Sensor de Higiene de Caminhos e Zero Hardcode",
        epilog="Exemplo:\n  python3 sensor_path_hygiene.py --scan-dir source/",
    )
    parser.add_argument(
        "--scan-dir",
        type=str,
        default="source",
        help="Diretório a varrer (padrão: source).",
    )
    args = parser.parse_args()
    target = Path(args.scan_dir).resolve()
    sys.exit(audit_path_hygiene(target))


if __name__ == "__main__":
    main()

