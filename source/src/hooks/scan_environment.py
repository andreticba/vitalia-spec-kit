#!/usr/bin/env python3
# scan_environment.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
"""
Varredura de Diagnóstico de Ambiente — Vitalia SPEC Kit v0.0.1

Executa a inspeção do ambiente do projeto via kit_env_bootstrap e emite
o relatório estruturado em formato JSON conforme scan-environment.schema.json.

Exit codes:
  0 — Operação concluída com sucesso (status HEALTHY ou DEGRADED)
  1 — Erro fatal não tratado
"""

import sys
import json
import argparse
from pathlib import Path

# Adiciona a raiz de source/src ao sys.path
_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap


def main():
    parser = argparse.ArgumentParser(
        description="Varredura de Diagnóstico de Ambiente — Vitalia SPEC Kit v0.0.1\n\n"
                    "Inspeciona a raiz do projeto e o runtime isolado sem dependência de rede.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--cwd", type=str, default=None, help="Diretório de trabalho alvo para varredura do ambiente.")
    args = parser.parse_args()

    health = kit_env_bootstrap.init(cwd=args.cwd)
    print(json.dumps(health, indent=2, ensure_ascii=False))

    # Conforme o contrato SDD, DEGRADED e HEALTHY retornam 0 para permitir operação da IDE
    sys.exit(0)


if __name__ == "__main__":
    main()
