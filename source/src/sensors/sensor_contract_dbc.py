#!/usr/bin/env python3
# sensor_contract_dbc.py | Vitalia SDD v0.6.0 | 10-11-2026 16:35(GMT-04:00)
"""
Vitalia Runtime Sensor Suite (VRSS) — Sensor de Contratos Design-by-Contract (DbC).
Audita os arquivos declarativos TOML de workflows em extensions/, garantindo a presença
de precondições, pós-condições, ferramentas e guardrails mandatórios.

Exemplos de Uso Didático:
  python3 sensor_contract_dbc.py --extensions-dir source/extensions/
"""

import argparse
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

MANDATORY_SECTIONS = ["meta", "tools", "context", "transport", "guardian"]


def audit_workflow_contracts(ext_dir: Path) -> int:
    if not ext_dir.exists():
        print(f"[Sensor DbC] ❌ Diretório não encontrado: {ext_dir}", file=sys.stderr)
        return 1

    toml_files = list(ext_dir.glob("*.toml"))
    if not toml_files:
        print(f"[Sensor DbC] ❌ Nenhuma extensão TOML encontrada em {ext_dir}", file=sys.stderr)
        return 1

    violations = []
    audited = 0

    for tf in toml_files:
        audited += 1
        try:
            if tomllib:
                with open(tf, "rb") as f:
                    data = tomllib.load(f)
            else:
                # Fallback simples baseado em texto
                content = tf.read_text(encoding="utf-8")
                data = {s: True for s in MANDATORY_SECTIONS if f"[{s}]" in content}
        except Exception as e:
            violations.append(f"{tf.name}: Falha de sintaxe TOML — {e}")
            continue

        for section in MANDATORY_SECTIONS:
            if section not in data:
                violations.append(f"{tf.name}: Seção DbC obrigatória ausente '[{section}]'")

    if violations:
        print(f"[Sensor DbC] ❌ FALHA: {len(violations)} violações de contrato DbC detectadas:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print(f"[Sensor DbC] ✅ SUCESSO: {audited} contratos de workflow auditados com conformidade DbC estrita.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="VRSS Sensor de Contratos Design-by-Contract (DbC) de Workflows",
        epilog="Exemplo:\n  python3 sensor_contract_dbc.py --extensions-dir source/extensions/",
    )
    parser.add_argument(
        "--extensions-dir",
        type=str,
        default="source/extensions",
        help="Caminho para o diretório de extensões TOML a auditar.",
    )
    args = parser.parse_args()
    target = Path(args.extensions_dir).resolve()
    sys.exit(audit_workflow_contracts(target))


if __name__ == "__main__":
    main()

