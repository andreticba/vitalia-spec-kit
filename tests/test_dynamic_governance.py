# test_dynamic_governance.py | Vitalia SPEC Kit v0.0.1 | 11-11-2026 22:10(GMT-04:00)
"""
Testes de integridade da governança dinâmica e saneamento de números mágicos (T013 / FR-004 / FR-006).
Cenário de Falsificação (P05): Falha se qualquer arquivo em profiles, extensions ou código interno
contiver menções estáticas a faixas/contagens fixas de governança ("P00–P17", "18 princípios",
"16 workflows", "16 *.toml", "14 gp_*.yaml") em vez do Padrão Afirmativo Dinâmico.
"""

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = REPO_ROOT / "source" / "profiles"
EXTENSIONS_DIR = REPO_ROOT / "source" / "extensions"
SRC_DIR = REPO_ROOT / "source" / "src"

FORBIDDEN_MAGIC_PATTERNS = [
    re.compile(r"P00[–\-]P17", re.IGNORECASE),
    re.compile(r"18\s+princ[íi]pios", re.IGNORECASE),
    re.compile(r"18\s+principles", re.IGNORECASE),
    re.compile(r"16\s+workflows", re.IGNORECASE),
    re.compile(r"16\s+\*\.toml", re.IGNORECASE),
    re.compile(r"14\s+gp_\*\.yaml", re.IGNORECASE),
]


def test_profiles_free_from_static_magic_numbers():
    """
    FR-004 / FR-006: Nenhum arquivo YAML em source/profiles/ deve conter
    contagens fixas de princípios ou workflows.
    """
    assert PROFILES_DIR.exists()
    yaml_files = list(PROFILES_DIR.glob("*.yaml")) + list(PROFILES_DIR.glob("*.yml"))
    assert len(yaml_files) > 0

    violations = []
    for yf in yaml_files:
        content = yf.read_text(encoding="utf-8")
        for pat in FORBIDDEN_MAGIC_PATTERNS:
            matches = pat.findall(content)
            if matches:
                violations.append(f"{yf.name}: encontrado '{matches[0]}'")

    assert not violations, (
        f"Cenário de Falsificação atingido: arquivos de perfil com números mágicos estáticos: {violations}"
    )


def test_extensions_free_from_static_magic_numbers():
    """
    FR-004 / FR-006: Nenhum arquivo TOML em source/extensions/ deve conter
    contagens fixas de princípios ou workflows.
    """
    assert EXTENSIONS_DIR.exists()
    toml_files = list(EXTENSIONS_DIR.glob("*.toml"))
    assert len(toml_files) > 0

    violations = []
    for tf in toml_files:
        content = tf.read_text(encoding="utf-8")
        for pat in FORBIDDEN_MAGIC_PATTERNS:
            matches = pat.findall(content)
            if matches:
                violations.append(f"{tf.name}: encontrado '{matches[0]}'")

    assert not violations, (
        f"Cenário de Falsificação atingido: extensões com números mágicos estáticos: {violations}"
    )


def test_src_core_free_from_static_magic_numbers():
    """
    FR-004 / FR-006: Scripts internos de contexto e hook não devem conter
    contagens fixas de princípios ou workflows.
    """
    assert SRC_DIR.exists()
    python_files = list(SRC_DIR.glob("**/*.py"))

    violations = []
    for pf in python_files:
        content = pf.read_text(encoding="utf-8")
        for pat in FORBIDDEN_MAGIC_PATTERNS:
            matches = pat.findall(content)
            if matches:
                violations.append(f"{pf.name}: encontrado '{matches[0]}'")

    assert not violations, (
        f"Cenário de Falsificação atingido: scripts python com números mágicos estáticos: {violations}"
    )

