#!/usr/bin/env python3
# utils.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:00(GMT-04:00)
"""
Módulo de Utilitários Compartilhados — Vitalia SPEC Kit (Domínio CORE)
"""

import json
import hashlib
import os
import socket
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

VITALIA_TIMEZONE = timezone(timedelta(hours=-4))


def get_current_datetime() -> datetime:
    """Retorna o objeto datetime atual no fuso horário imutável America/Cuiaba (GMT-04:00)."""
    return datetime.now(VITALIA_TIMEZONE)


def get_timestamp(dt: Optional[datetime] = None) -> str:
    """Gera string de timestamp no formato canônico: DD-MM-YYYY HH:MM:SS(GMT-04:00)."""
    if dt is None:
        dt = get_current_datetime()
    return dt.strftime("%d-%m-%Y %H:%M:%S(GMT-04:00)")


def parse_sync_time(ts_str: str) -> datetime:
    """
    Converte uma string de timestamp DD-MM-YYYY HH:MM[:SS](GMT-04:00) em objeto datetime comparável.
    Retorna datetime.min (GMT-04:00) caso a string seja vazia ou inválida.
    """
    if not ts_str or not isinstance(ts_str, str):
        return datetime(1970, 1, 1, tzinfo=VITALIA_TIMEZONE)
    clean = ts_str.split("(")[0].strip()
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(clean, fmt)
            return dt.replace(tzinfo=VITALIA_TIMEZONE)
        except ValueError:
            continue
    return datetime(1970, 1, 1, tzinfo=VITALIA_TIMEZONE)


def format_visible_header(dt: Optional[datetime] = None) -> str:
    """Retorna a linha visível obrigatória para o corpo de documentos Markdown."""
    ts = get_timestamp(dt)
    return f"**Data/Hora de Geração:** `{ts}` | **Fuso Horário:** America/Cuiaba `(GMT-04:00)`"


def get_machine_identity() -> tuple[str, str]:
    """Retorna (machine_name, machine_id) derivado dinamicamente (P11)."""
    mname = os.environ.get("VITALIA_MACHINE_NAME") or socket.gethostname().lower() or "unknown"
    mid = hashlib.sha256(mname.encode("utf-8")).hexdigest()[:8]
    return mname, mid


def generate_id(content: str, length: int = 8) -> str:
    """Gera um hash hexadecimal SHA256 determinístico a partir de uma string de conteúdo."""
    hash_obj = hashlib.sha256(content.encode("utf-8"))
    return hash_obj.hexdigest()[:length]


def read_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """Lê um arquivo JSON Lines (.jsonl) de forma resiliente e retorna uma lista de dicionários."""
    records = []
    if not file_path.exists() or not file_path.is_file():
        return records

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    records.append(data)
                except json.JSONDecodeError as err:
                    print(f"⚠️ [core.utils] Aviso: Linha {line_idx} inválida em {file_path.name}: {err}", file=sys.stderr)
    except Exception as e:
        print(f"❌ [core.utils] Erro ao ler {file_path}: {e}", file=sys.stderr)

    return records


def append_jsonl(file_path: Path, record: Dict[str, Any]) -> bool:
    """Adiciona um registro (dicionário Python) como uma nova linha ao final de um arquivo .jsonl."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        return True
    except Exception as e:
        print(f"❌ [core.utils] Falha ao gravar append em {file_path}: {e}", file=sys.stderr)
        return False

