#!/usr/bin/env python3
# sensor_purity.py | Vitalia SDD v0.6.0 | 10-11-2026 16:15(GMT-04:00)
"""
Vitalia Runtime Sensor Suite (VRSS) — Sensor de Pureza de Diretórios.
Audita a árvore de skills (.agents/skills/) assegurando cumprimento estrito
do contrato de Progressive Disclosure da IDE Antigravity.

Exemplos de Uso Didático:
  python3 sensor_purity.py --target-dir .agents/skills
  python3 sensor_purity.py --target-dir /caminho/do/projeto/.agents/skills
"""

import argparse
import sys
from pathlib import Path


def audit_skills_purity(target_dir: Path) -> int:
    if not target_dir.exists() or not target_dir.is_dir():
        print(f"[Sensor Pureza] ❌ Diretório não encontrado: {target_dir}", file=sys.stderr)
        return 1

    errors = []
    inspected_skills = 0

    for item in target_dir.iterdir():
        # Violação 1: Arquivos soltos na raiz de skills
        if item.is_file():
            errors.append(f"Arquivo solto proibido encontrado: {item.name}")
            continue

        # Violação 2: Pastas ocultas (.trash, .backup, etc.)
        if item.name.startswith("."):
            errors.append(f"Diretório oculto proibido encontrado: {item.name}")
            continue

        # Violação 3: Subpasta deve conter um SKILL.md válido
        skill_file = item / "SKILL.md"
        if not skill_file.exists() or not skill_file.is_file():
            errors.append(f"Subdiretório sem SKILL.md: {item.name}")
            continue

        # Validar YAML frontmatter básico
        content = skill_file.read_text(encoding="utf-8", errors="ignore")
        if not (content.startswith("---") and "name:" in content and "description:" in content):
            errors.append(f"SKILL.md em {item.name} não possui frontmatter YAML válido (name e description)")
            continue

        inspected_skills += 1

    if errors:
        print(f"[Sensor Pureza] ❌ FALHA: {len(errors)} violações de pureza detectadas em {target_dir}:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"[Sensor Pureza] ✅ SUCESSO: {inspected_skills} skills auditadas com 100% de pureza.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="VRSS Sensor de Pureza de Árvore de Skills (.agents/skills/)",
        epilog="Exemplo:\n  python3 sensor_purity.py --target-dir .agents/skills",
    )
    parser.add_argument(
        "--target-dir",
        type=str,
        default=".agents/skills",
        help="Caminho para o diretório de skills a auditar (padrão: .agents/skills).",
    )
    args = parser.parse_args()
    target = Path(args.target_dir).resolve()
    sys.exit(audit_skills_purity(target))


if __name__ == "__main__":
    main()

