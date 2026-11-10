#!/usr/bin/env python3
# vitalia_tmp_cleanup.py | Vitalia SDD v0.6.0 | 10-11-2026 16:00(GMT-04:00)
"""
Utilitário Autônomo de Faxina e Manutenção de Contexto do Vitalia SPEC Kit.

Exemplos de Uso Didático:
  1. Simulação segura (dry-run):
     python3 vitalia_tmp_cleanup.py --dry-run

  2. Limpeza real de contextos antigos com confirmação automática:
     python3 vitalia_tmp_cleanup.py --force

  3. Limpeza apontando para diretório de projeto customizado:
     python3 vitalia_tmp_cleanup.py --target-dir /caminho/do/projeto --dry-run
"""

import argparse
import sys
from pathlib import Path


def cleanup_contexts(target_root: Path, dry_run: bool = False, force: bool = False) -> int:
    context_dir = target_root / ".vitalia" / "memory" / "data_storage" / "context"
    if not context_dir.exists():
        print(f"[Faxineiro] Diretório de contextos não encontrado: {context_dir}")
        return 0

    candidate_files = [f for f in context_dir.rglob("*.json") if f.is_file()]
    total_bytes = sum(f.stat().st_size for f in candidate_files)

    print(f"[Faxineiro] Encontrados {len(candidate_files)} arquivos transitórios ({total_bytes / 1024:.2f} KB).")

    if not candidate_files:
        print("[Faxineiro] Nenhum arquivo necessita de limpeza.")
        return 0

    if dry_run:
        print("[Faxineiro] MODO DRY-RUN: Nenhum arquivo será removido.")
        for f in candidate_files:
            print(f"  - Candidato: {f.relative_to(target_root)}")
        return 0

    if not force:
        confirm = input(f"Deseja remover {len(candidate_files)} arquivos? [s/N]: ").strip().lower()
        if confirm != "s":
            print("[Faxineiro] Operação cancelada pelo operador.")
            return 0

    removed = 0
    for f in candidate_files:
        try:
            f.unlink()
            removed += 1
        except OSError as e:
            print(f"[Faxineiro] Erro ao remover {f.name}: {e}", file=sys.stderr)

    print(f"[Faxineiro] ✅ Sucesso: {removed} arquivos removidos. Espaço liberado: {total_bytes / 1024:.2f} KB.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Utilitário Autônomo de Faxina de Contextos Transitórios — Vitalia SPEC Kit",
        epilog="Exemplos de Uso:\n  vitalia_tmp_cleanup.py --dry-run\n  vitalia_tmp_cleanup.py --force",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--target-dir",
        type=str,
        default=".",
        help="Diretório raiz do projeto assistido (padrão: diretório atual).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a limpeza sem deletar nenhum arquivo físico.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Executa a remoção sem solicitar confirmação interativa no terminal.",
    )

    args = parser.parse_args()
    target_root = Path(args.target_dir).resolve()
    sys.exit(cleanup_contexts(target_root, dry_run=args.dry_run, force=args.force))


if __name__ == "__main__":
    main()

