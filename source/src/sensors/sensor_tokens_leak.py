#!/usr/bin/env python3
# sensor_tokens_leak.py | Vitalia SDD v0.6.0 | 10-11-2026 16:30(GMT-04:00)
"""
Vitalia Runtime Sensor Suite (VRSS) — Sensor de Prevenção de Vazamento de Segredos e Tokens.
Audita arquivos transitórios de contexto garantindo conformidade com P06 (Secrets Never in Git)
e P07 (Privacy by Design / Data Vault).

Exemplos de Uso Didático:
  python3 sensor_tokens_leak.py --context-dir .vitalia/memory/data_storage/context
"""

import argparse
import re
import sys
from pathlib import Path

SECRET_PATTERNS = [
    (re.compile(r"sk_[live|test]_[0-9a-zA-Z]{16,}"), "Chave de API OpenAI/Stripe"),
    (re.compile(r"ghp_[0-9a-zA-Z]{36}"), "Token de Acesso Pessoal GitHub"),
    (re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"), "Chave Privada Criptográfica"),
    (re.compile(r"(?:api_key|apikey|secret|password)[\"'\s:=]+[\"'][^\"'\s]{8,}[\"']", re.IGNORECASE), "Credencial sensível em texto puro"),
]


def audit_tokens_leak(context_dir: Path) -> int:
    if not context_dir.exists():
        print(f"[Sensor Segredos] ❌ Diretório não encontrado: {context_dir}", file=sys.stderr)
        return 1

    violations = []
    files_checked = 0

    for item in context_dir.rglob("*.json"):
        if not item.is_file():
            continue

        files_checked += 1
        try:
            content = item.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern, desc in SECRET_PATTERNS:
            match = pattern.search(content)
            if match:
                # Sanitizar exibição do trecho vazado
                snippet = match.group(0)[:12] + "..."
                violations.append(f"{item.name} — {desc}: '{snippet}'")

    if violations:
        print(f"[Sensor Segredos] ❌ FALHA: {len(violations)} vazamentos de segredos/tokens detectados:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print(f"[Sensor Segredos] ✅ SUCESSO: {files_checked} arquivos de contexto auditados com 0 segredos expostos.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="VRSS Sensor de Prevenção de Vazamento de Segredos e Dados Sensíveis",
        epilog="Exemplo:\n  python3 sensor_tokens_leak.py --context-dir .vitalia/memory/data_storage/context",
    )
    parser.add_argument(
        "--context-dir",
        type=str,
        default=".vitalia/memory/data_storage/context",
        help="Caminho para o diretório de contextos a auditar.",
    )
    args = parser.parse_args()
    target = Path(args.context_dir).resolve()
    sys.exit(audit_tokens_leak(target))


if __name__ == "__main__":
    main()

