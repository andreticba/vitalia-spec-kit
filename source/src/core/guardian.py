# guardian.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
"""
Módulo Core Guardian — Facade e Ponto Central de Governança Constitucional.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import sys

_SRC_DIR = str(Path(__file__).resolve().parent.parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from hooks.guardian_context import GuardianContextV2


class Guardian:
    """Facade de alto nível para invocação do oráculo Guardian sem podas."""

    @staticmethod
    def get_context(workflow_name: str, config: Optional[dict] = None, cwd: Optional[Path] = None, user_args: str = "") -> Dict[str, Any]:
        target_cwd = cwd or Path.cwd()
        engine = GuardianContextV2(
            workflow_name=workflow_name,
            guardian_config=config or {},
            cwd=target_cwd,
            user_args=user_args
        )
        return engine.build_payload()
