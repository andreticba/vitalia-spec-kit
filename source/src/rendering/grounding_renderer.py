#!/usr/bin/env python3
# grounding_renderer.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:07(GMT-04:00)
"""
Compilador de Domínios de Grounding — Vitalia SPEC Kit (Domínio RENDERING)
"""

import sys
from pathlib import Path

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap

health = kit_env_bootstrap.init()
from core.utils import get_timestamp, read_jsonl


class GroundingRenderer:
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.local_domains_jsonl = session_dir / "data" / "grounding-domains.jsonl"
        self.output_yaml = session_dir / "grounding-domains-local.yaml"

    def compile(self) -> int:
        pending_count = 0
        local_records = read_jsonl(self.local_domains_jsonl) if self.local_domains_jsonl.exists() else []
        ts = get_timestamp()

        lines = [
            f"# grounding-domains-local.yaml | Vitalia SPEC Kit v0.0.1 | {ts}",
            "# Dicionário de domínios com verificação externa obrigatória (10 domínios canônicos)",
            "version: '0.0.1'",
            "domains:",
        ]

        canonical_domains = [
            ("provedores_de_ia", "Modelos de fronteira e orquestração híbrida de IA"),
            ("python_packages", "Ecossistema Python, Django 6.x, ASGI e Data Vault"),
            ("web_technologies", "Frontend moderno: Next.js 16, React 19, TypeScript 5 e TailwindCSS v4"),
            ("external_apis", "APIs externas, gateways omnichannel, WebSockets e contratos OpenAPI 3.0"),
            ("security_practices", "Segurança ofensiva/defensiva, OWASP LLM Top 10 e criptografia"),
            ("regulations_compliance", "LGPD, HIPAA, GDPR, EU AI Act e regulamentos ANVISA/CFM"),
            ("cloud_services", "Infraestrutura cloud, containers, bancos vetoriais e observabilidade"),
            ("scientific_claims", "Revisões integrativas PRISMA 2020, Scopus, Web of Science e PubMed"),
            ("clinical_safety", "Segurança clínica, faixas de biomarcadores e suporte à decisão médica"),
            ("software_architecture", "Clean Architecture, SDD, contratos de consumidor e engenharia de contexto"),
        ]
        for name, desc in canonical_domains:
            lines.append(f"  - name: '{name}'")
            lines.append(f"    description: '{desc}'")
            lines.append("    scope: 'global'")

        for r in local_records:
            status = r.get("status", "PENDING")
            if status == "PENDING":
                pending_count += 1
            lines.append(f"  - name: '{r.get('domain', '')}'")
            lines.append(f"    description: '{r.get('description', '')}'")
            lines.append("    scope: 'local'")
            lines.append(f"    status: '{status}'")

        self.output_yaml.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return pending_count

