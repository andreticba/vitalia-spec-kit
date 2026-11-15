#!/usr/bin/env python3
# vitalia_tmp_cleanup.py | Vitalia SPEC Kit v0.0.1 | 15-11-2026 13:57(GMT-04:00)
"""
Utilitário Autônomo de Faxina e Manutenção de Contexto do Vitalia SPEC Kit.

Exemplos de Uso Didático:
  1. Menu interativo (padrão):
     python3 vitalia_tmp_cleanup.py

  2. Simulação segura (dry-run):
     python3 vitalia_tmp_cleanup.py --dry-run

  3. Limpeza automática de sessões passadas (preserva hoje):
     python3 vitalia_tmp_cleanup.py --force

  4. Purga total sob confirmação afirmativa (inclui hoje):
     python3 vitalia_tmp_cleanup.py --purge-all

  5. Limpeza em diretório customizado:
     python3 vitalia_tmp_cleanup.py --target-dir /caminho/do/projeto --dry-run
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

CUIABA_TZ = datetime.timezone(datetime.timedelta(hours=-4))
FILENAME_DATE_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+_(\d{4})(\d{2})(\d{2})_\d{6}_[a-zA-Z0-9]+\.json$")


def format_bytes(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.2f} KB"
    else:
        return f"{num_bytes / (1024 * 1024):.2f} MB"


def extract_civil_date(file_path: Path) -> Tuple[datetime.date, str]:
    match = FILENAME_DATE_REGEX.match(file_path.name)
    if match:
        year, month, day = map(int, match.groups())
        try:
            d = datetime.date(year, month, day)
            return d, d.strftime("%d-%m-%Y")
        except ValueError:
            pass

    # Fallback para st_mtime em fuso GMT-04:00
    try:
        mtime = file_path.stat().st_mtime
        dt = datetime.datetime.fromtimestamp(mtime, tz=CUIABA_TZ)
        d = dt.date()
        return d, d.strftime("%d-%m-%Y")
    except OSError:
        d = datetime.datetime.now(CUIABA_TZ).date()
        return d, d.strftime("%d-%m-%Y")


def parse_date_selection(raw_input: str, max_choice: int) -> List[int]:
    """
    Interpreta faixas e listas numéricas como '1,2', '1-3' ou '1, 3-4'.
    Retorna lista de índices válidos (1-based).
    """
    selected = set()
    parts = [p.strip() for p in raw_input.split(",") if p.strip()]
    for part in parts:
        if "-" in part:
            range_parts = part.split("-", 1)
            try:
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                if 1 <= start <= end <= max_choice:
                    for i in range(start, end + 1):
                        selected.add(i)
                else:
                    return []
            except ValueError:
                return []
        else:
            try:
                val = int(part)
                if 1 <= val <= max_choice:
                    selected.add(val)
                else:
                    return []
            except ValueError:
                return []
    return sorted(list(selected))


def cleanup_contexts(
    target_root: Path,
    dry_run: bool = False,
    force: bool = False,
    purge_all: bool = False,
) -> int:
    context_dir = target_root / ".vitalia" / "memory" / "data_storage" / "context"
    if not context_dir.exists():
        print(f"[Faxineiro] Diretório de contextos não encontrado: {context_dir}")
        return 0

    candidate_files = [f for f in context_dir.rglob("*.json") if f.is_file()]
    if not candidate_files:
        print("[Faxineiro] Nenhum arquivo de contexto encontrado para limpeza.")
        return 0

    today = datetime.datetime.now(CUIABA_TZ).date()
    today_str = today.strftime("%d-%m-%Y")

    # Agrupa por data civil
    date_groups: Dict[Tuple[datetime.date, str], List[Path]] = {}
    for f in candidate_files:
        d, d_str = extract_civil_date(f)
        date_groups.setdefault((d, d_str), []).append(f)

    # Ordena datas decrescentes
    sorted_dates = sorted(date_groups.keys(), key=lambda x: x[0], reverse=True)

    today_group = None
    past_dates = []
    for d, d_str in sorted_dates:
        if d == today:
            today_group = (d, d_str)
        else:
            past_dates.append((d, d_str))

    total_bytes = sum(f.stat().st_size for f in candidate_files)
    print(f"\n📦 Arquivos de contexto transitórios encontrados por data civil ({len(candidate_files)} arquivos, {format_bytes(total_bytes)}):")

    for idx, (d, d_str) in enumerate(past_dates, start=1):
        files = date_groups[(d, d_str)]
        size = sum(f.stat().st_size for f in files)
        print(f"   [{idx}] 📅 {d_str}: {len(files)} arquivos ({format_bytes(size)})")

    if today_group:
        files = date_groups[today_group]
        size = sum(f.stat().st_size for f in files)
        print(f"   -- 📅 hoje ({today_str}, sessão ativa — preservada automaticamente): {len(files)} arquivos ({format_bytes(size)})")
    else:
        print(f"   -- 📅 hoje ({today_str}, sessão ativa — preservada automaticamente): 0 arquivos")

    # 1. Modo DRY-RUN
    if dry_run:
        print("\n[DRY-RUN] Modo simulação ativo:")
        if purge_all:
            print(f"  - Seriam removidos TODOS os {len(candidate_files)} arquivos ({format_bytes(total_bytes)}), INCLUINDO a sessão de hoje.")
        elif force:
            past_files_count = sum(len(date_groups[k]) for k in past_dates)
            past_size = sum(f.stat().st_size for k in past_dates for f in date_groups[k])
            print(f"  - Seriam removidos {past_files_count} arquivos passados ({format_bytes(past_size)}).")
            print(f"  - A data de hoje ({today_str}) seria PRESERVADA.")
        else:
            print("  - Apresentação do menu concluída com sucesso.")
            print(f"  - A data de hoje ({today_str}) permanece PRESERVADA por padrão.")
        print("[DRY-RUN] Simulação concluída. Nenhum arquivo foi removido.")
        return 0

    # 2. Modo PURGE-ALL não-interativo / interativo
    if purge_all:
        try:
            confirm = input(f"\nTem certeza que deseja apagar TODOS os arquivos de contexto, incluindo hoje? [s/N]: ").strip().lower()
        except EOFError:
            confirm = "n"
        if confirm != "s":
            print("[Faxineiro] Operação cancelada pelo operador.")
            return 0
        files_to_delete = candidate_files

    # 3. Modo FORCE (Opção [a] automática)
    elif force:
        files_to_delete = [f for k in past_dates for f in date_groups[k]]
        if not files_to_delete:
            print("\n[Faxineiro] Nenhum arquivo anterior a hoje para remover. Sessão de hoje preservada.")
            return 0

    # 4. Modo Interativo
    else:
        print("\nOpções de limpeza:")
        print("  [a] Apagar todas as datas anteriores a hoje (preserva a sessão ativa)")
        print("  [d] Selecionar datas específicas para apagar (ex: 1,2 ou 1-3)")
        print("  [n] Não apagar nada (cancelar)")
        print("  [t] Apagar TUDO (incluindo a sessão de hoje)")

        try:
            choice = input("\nEscolha uma opção [a/d/n/t] (padrão: n): ").strip().lower()
        except EOFError:
            choice = "n"

        if not choice or choice == "n":
            print("[Faxineiro] Operação cancelada pelo operador. Nenhum arquivo foi removido.")
            return 0
        elif choice == "a":
            files_to_delete = [f for k in past_dates for f in date_groups[k]]
        elif choice == "t":
            try:
                confirm = input("Tem certeza que deseja apagar TODOS os arquivos de contexto, incluindo hoje? [s/N]: ").strip().lower()
            except EOFError:
                confirm = "n"
            if confirm != "s":
                print("[Faxineiro] Operação cancelada pelo operador.")
                return 0
            files_to_delete = candidate_files
        elif choice == "d":
            if not past_dates:
                print("[Faxineiro] Não há datas anteriores disponíveis para seleção.")
                return 0
            try:
                sel_raw = input(f"Informe as datas a apagar (1 a {len(past_dates)}, ex: 1,2 ou 1-3): ").strip()
            except EOFError:
                sel_raw = ""
            selected_indices = parse_date_selection(sel_raw, len(past_dates))
            if not selected_indices:
                print(f"[Faxineiro] Seleção inválida '{sel_raw}'. Operação cancelada.")
                return 0
            files_to_delete = []
            for idx in selected_indices:
                date_key = past_dates[idx - 1]
                files_to_delete.extend(date_groups[date_key])
        else:
            print(f"[Faxineiro] Opção inválida '{choice}'. Operação cancelada.")
            return 0

    if not files_to_delete:
        print("[Faxineiro] Nenhum arquivo selecionado para remoção.")
        return 0

    bytes_to_free = sum(f.stat().st_size for f in files_to_delete if f.exists())
    removed_count = 0
    for f in files_to_delete:
        try:
            f.unlink()
            removed_count += 1
        except OSError as e:
            print(f"[Faxineiro] Erro ao remover {f.name}: {e}", file=sys.stderr)

    print(f"\n[Faxineiro] ✅ Sucesso: {removed_count} arquivos removidos. Espaço liberado: {format_bytes(bytes_to_free)}.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Utilitário Autônomo de Faxina e Manutenção de Contextos Transitórios — Vitalia SPEC Kit",
        epilog="Exemplos de Uso:\n  vitalia_tmp_cleanup.py --dry-run\n  vitalia_tmp_cleanup.py --force\n  vitalia_tmp_cleanup.py --purge-all",
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
        help="Simula a limpeza e exibe o agrupamento civil sem deletar nenhum arquivo físico.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Executa a opção [a] automaticamente: remove datas anteriores e preserva a sessão de hoje.",
    )
    parser.add_argument(
        "--purge-all",
        action="store_true",
        help="Solicita confirmação afirmativa [s/N] para remover TODOS os arquivos de contexto, incluindo hoje.",
    )

    args = parser.parse_args()
    target_root = Path(args.target_dir).resolve()
    sys.exit(cleanup_contexts(
        target_root,
        dry_run=args.dry_run,
        force=args.force,
        purge_all=args.purge_all,
    ))


if __name__ == "__main__":
    main()
