#!/usr/bin/env python3
# domain_detector.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:01(GMT-04:00)
"""
Detector Semântico de Domínios e Verificador de Validade Temporal — Vitalia SPEC Kit v0.0.1
"""

from datetime import datetime
from typing import Any, Dict, List

from core.utils import get_current_datetime, parse_sync_time


def verify_temporal_status(items: Any, now: datetime | None = None) -> List[str]:
    """
    Inspeciona recursivamente uma lista ou dicionário de domínios (grounding_domains ou dynamic_questioning)
    e marca qualquer entrada cujo `valid_until` esteja no passado com `status = "TEMPORAL_REFRESH_REQUIRED"`.
    Retorna a lista de IDs/chaves expirados.
    """
    if now is None:
        now = get_current_datetime()

    expired_ids: List[str] = []

    if isinstance(items, list):
        for entry in items:
            if not isinstance(entry, dict):
                continue
            valid_until = entry.get("valid_until")
            if valid_until:
                dt_until = parse_sync_time(valid_until)
                if dt_until < now:
                    entry["status"] = "TEMPORAL_REFRESH_REQUIRED"
                    expired_ids.append(str(entry.get("id", "unknown")))
    elif isinstance(items, dict):
        for key, entry in items.items():
            if not isinstance(entry, dict):
                continue
            valid_until = entry.get("valid_until")
            if valid_until:
                dt_until = parse_sync_time(valid_until)
                if dt_until < now:
                    entry["status"] = "TEMPORAL_REFRESH_REQUIRED"
                    expired_ids.append(str(key))

    return expired_ids

