#!/usr/bin/env python3
# constitution_renderer.py | Vitalia SPEC Kit v0.0.1 | 08-11-2026 20:07(GMT-04:00)
"""
Compilador Visual da Constituição Dual-Index — Vitalia SPEC Kit (Domínio RENDERING)
"""

import argparse
import sys
from pathlib import Path

import yaml

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap

health = kit_env_bootstrap.init()
from core.utils import format_visible_header, get_timestamp


class ConstitutionRenderer:
    def __init__(self, kit_root: Path):
        self.kit_root = kit_root
        self.yaml_file = kit_root / "profiles" / "constitution.yaml"
        self.output_md = kit_root / "docs" / "constitution_rendered.md"

    def compile(self) -> Path:
        if not self.yaml_file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.yaml_file}")

        data = yaml.safe_load(self.yaml_file.read_text(encoding="utf-8"))
        domain_index = data.get("domain_index", {})
        principles = data.get("principles", {})
        ts = get_timestamp()

        lines = [
            f"<!-- constitution_rendered.md | Vitalia SPEC Kit v0.0.1 | {ts} -->",
            f"> **constitution_rendered.md | Vitalia SPEC Kit v0.0.1 | {ts}**",
            "",
            "# 📜 Constituição de Arquitetura, Segurança e Governança Vitalia SPEC Kit",
            "",
            format_visible_header(),
            "",
            "```mermaid",
            "flowchart TD",
            '  C(("Constituição Vitalia v0.0.1"))',
        ]

        for domain_id, pids in domain_index.items():
            lines.append(f'  C --> D_{domain_id}["📦 {domain_id}"]')
            for pid in pids:
                p_info = principles.get(pid, {})
                p_name = p_info.get("name", pid)
                lines.append(f'  D_{domain_id} --> P_{pid}["⚡ {pid}: {p_name}"]')

        lines.extend(["```", "", "---", "", "## 📑 Domínios e Princípios Invioláveis", ""])

        for domain_id, pids in domain_index.items():
            lines.append(f"### 📦 {domain_id}")
            lines.append("")
            lines.append("| ID | Princípio | Severidade | Regra | Validador |")
            lines.append("|---|---|---|---|---|")
            for pid in pids:
                p_info = principles.get(pid, {})
                p_name = p_info.get("name", pid)
                p_sev = p_info.get("severity", "BLOCKING")
                p_rule = str(p_info.get("rule", "")).strip().replace("\n", " ").replace("|", "-")
                p_val = p_info.get("validator", "")
                lines.append(f"| `{pid}` | **{p_name}** | `{p_sev}` | {p_rule} | `{p_val}` |")
            lines.append("")

        self.output_md.parent.mkdir(parents=True, exist_ok=True)
        self.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return self.output_md


def main():
    parser = argparse.ArgumentParser(description="Compilador Visual da Constituição — Vitalia SPEC Kit (v0.0.1)")
    parser.add_argument("--kit-dir", default=None, help="Diretório raiz do kit")
    args = parser.parse_args()

    kit_root = Path(args.kit_dir) if args.kit_dir else kit_env_bootstrap.resolve_kit_dir()
    renderer = ConstitutionRenderer(kit_root)
    out = renderer.compile()
    print(f"✅ constitution_rendered.md compilado com sucesso em: {out}")


if __name__ == "__main__":
    main()

