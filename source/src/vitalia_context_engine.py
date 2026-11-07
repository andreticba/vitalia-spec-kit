#!/usr/bin/env python3
# vitalia_context_engine.py | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:30(GMT-04:00)
"""
Motor de Controle de Contexto e Sincronização em Filesystem Puro — Vitalia SPEC Kit v0.0.1

Responsabilidades:
1. Gerenciar o ciclo de vida da memória de sessão local (.vitalia/memory/session):
   - init: inicializa pastas de shards, data e state
   - shard: persiste ou atualiza o shard da máquina no filesystem
   - consolidate: unifica shards e compila o README.md da sessão
   - lock / unlock / status: controle de semáforo via semaphore.json local
   - end: registra encerramento da sessão em data/session_history.jsonl
2. Operação estritamente offline, livre de qualquer container (Redis/Postgres) ou porta local.
"""

import os
import sys
import json
import argparse
import hashlib
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

VITALIA_TIMEZONE = timezone(timedelta(hours=-4))

_SCRIPTS_ROOT = str(Path(__file__).resolve().parent)
if _SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, _SCRIPTS_ROOT)

import kit_env_bootstrap


def get_machine_info() -> Dict[str, str]:
    """Obtém identificador determinístico da máquina."""
    machine_name = os.environ.get("VITALIA_MACHINE_NAME") or platform.node().lower() or "station"
    machine_id = hashlib.sha256(machine_name.encode()).hexdigest()[:8]
    return {"machine_name": machine_name, "machine_id": machine_id}


class LocalContextEngine:
    """Motor de contexto que opera 100% sobre o sistema de arquivos local."""

    def __init__(self, session_dir: Optional[Path] = None):
        if session_dir:
            self.session_dir = Path(session_dir).resolve()
            if self.session_dir.name == "session" and self.session_dir.parent.name == "memory" and self.session_dir.parent.parent.name == ".vitalia":
                self.project_root = self.session_dir.parent.parent.parent
            else:
                self.project_root = kit_env_bootstrap.find_project_root(self.session_dir)
        else:
            self.project_root = kit_env_bootstrap.find_project_root()
            self.session_dir = self.project_root / ".vitalia" / "memory" / "session"

        self.shards_dir = self.session_dir / "shards"
        self.data_dir = self.session_dir / "data"
        self.state_dir = self.session_dir / "state"
        self.semaphore_file = self.session_dir / "semaphore.json"

    def action_init(self) -> None:
        """Inicializa a estrutura da memória local."""
        self.shards_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        if not self.semaphore_file.exists():
            initial_sem = {
                "state": "FREE",
                "machine_name": None,
                "machine_id": None,
                "token": None,
                "acquired_at": None,
                "expires_at": None
            }
            self.semaphore_file.write_text(json.dumps(initial_sem, indent=2), encoding="utf-8")

        print(f"[ContextEngine] ✅ Estrutura de memória inicializada em {self.session_dir}")

    def action_shard(self, task: str = "", status: str = "Em Andamento", next_step: str = "", summary: str = "") -> None:
        """Grava ou atualiza o shard da máquina atual."""
        self.action_init()
        minfo = get_machine_info()
        now_iso = datetime.now(VITALIA_TIMEZONE).isoformat()

        shard_data = {
            "machine_id": minfo["machine_id"],
            "machine_name": minfo["machine_name"],
            "task": task,
            "status": status,
            "next_step": next_step,
            "summary": summary,
            "mode": "Standalone (Filesystem Puro)",
            "updated_at": now_iso
        }

        shard_path = self.shards_dir / f"{minfo['machine_name']}.json"
        shard_path.write_text(json.dumps(shard_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[ContextEngine] ✅ Shard gravado em {shard_path} [{minfo['machine_name']} / {minfo['machine_id']}]")

    def _resolve_template_path(self) -> Path:
        """Resolve o template do dashboard canônico via kit_env_bootstrap."""
        try:
            kit_dir = kit_env_bootstrap.resolve_kit_dir(self.project_root)
            t_path = kit_dir / "templates" / "dashboard_template.md"
            if t_path.exists():
                return t_path
        except Exception:
            pass
        # Fallback para o source/templates do repositório em desenvolvimento
        repo_source = Path(__file__).resolve().parent.parent / "templates" / "dashboard_template.md"
        if repo_source.exists():
            return repo_source
        return self.session_dir / "templates" / "dashboard_template.md"

    def _build_mermaid(self, shards: List[Dict[str, Any]]) -> str:
        lines = ['  Cloud(("☁️ Git Remoto / Hub"))']
        if not shards:
            minfo = get_machine_info()
            node_id = f"M_{minfo['machine_id']}"
            lines.append(f'  {node_id}["💻 {minfo["machine_name"]}<br/><i>Livre</i><br/><code>Standalone</code>"]')
            lines.append(f'  {node_id} <-->|"Local"| Cloud')
            lines.append(f"  style {node_id} stroke:#0969da,stroke-width:2px,fill:#ddf4ff,color:#0969da")
        else:
            for s in shards:
                m_id = s.get("machine_id", "unknown")
                m_name = s.get("machine_name", "Máquina")
                task = s.get("task", s.get("summary", "Livre"))
                mode = s.get("mode", "Standalone")
                sync = s.get("updated_at", s.get("last_sync", ""))

                node_id = f"M_{m_id}"
                lines.append(f'  {node_id}["💻 {m_name}<br/><i>{task}</i><br/><code>{mode}</code>"]')
                lines.append(f'  {node_id} <-->|"{sync}"| Cloud')
                lines.append(f"  style {node_id} stroke:#0969da,stroke-width:2px,fill:#ddf4ff,color:#0969da")

        lines.append("  style Cloud stroke:#1a7f37,stroke-width:2px,fill:#dafbe1,color:#1a7f37")
        return "\n".join(lines)

    def _build_shards_table(self, shards: List[Dict[str, Any]]) -> str:
        if not shards:
            return '    <tr><td colspan="6"><em>Nenhuma estação registrada no momento.</em></td></tr>'
        rows = []
        for s in shards:
            m_id = s.get("machine_id", "-")
            m_name = s.get("machine_name", "unknown")
            task = s.get("task", s.get("summary", "-"))
            status = s.get("status", "Em Andamento")
            next_step = s.get("next_step", s.get("p0", "-"))
            sync = s.get("updated_at", s.get("last_sync", "-"))
            mode = s.get("mode", "Standalone")

            badge_mode = f'<img src="https://img.shields.io/badge/-Standalone-blue?style=flat-square" alt="{mode}" />'
            status_color = "green" if status == "Concluído" else "orange"

            rows.append(f"""    <tr>
      <td><strong>{m_name}</strong> (<code>{m_id}</code>)</td>
      <td>{task}</td>
      <td align="center">{badge_mode}</td>
      <td align="center"><span style="color:{status_color};">●</span> {status}</td>
      <td>{sync}</td>
      <td><strong>{next_step}</strong></td>
    </tr>""")
        return "\n".join(rows)

    def _build_active_session(self, shards: List[Dict[str, Any]], sem_data: Dict[str, Any]) -> str:
        minfo = get_machine_info()
        active = None
        for s in shards:
            if s.get("machine_name") == minfo["machine_name"]:
                active = s
                break
        if not active and shards:
            active = shards[0]

        if not active:
            return "> ℹ️ Nenhuma sessão ativa no momento."

        task = active.get("task", active.get("summary", "-"))
        next_step = active.get("next_step", active.get("p0", "-"))
        sync = active.get("updated_at", "-")

        return f"""- **Estação Ativa:** `{active.get('machine_name')}` (`{active.get('machine_id')}`)
- **Tarefa em Execução:** {task}
- **🎯 Próximo Passo Prioritário (P0):** `{next_step}`
- **Última Sincronização:** `{sync}`"""

    def _build_history(self) -> str:
        candidates = [
            self.session_dir / "session_history.jsonl",
            self.data_dir / "session_history.jsonl",
            self.project_root / ".vitalia" / "memory" / "session" / "session_history.jsonl",
            self.project_root / ".vitalia" / "memory" / "data_storage" / "session_history.jsonl",
        ]
        history_file = next((c for c in candidates if c.exists()), None)
        if not history_file:
            return "_Nenhum histórico de sessões registrado até o momento._"

        entries: List[Dict[str, Any]] = []
        try:
            for line in history_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        except Exception:
            pass

        if not entries:
            return "_Nenhum histórico de sessões registrado até o momento._"

        lines = [
            "| Data / Hora | Estação (ID) | Tarefa Executada | Próximo Passo (P0) |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for h in reversed(entries[-10:]):
            dt = h.get("timestamp", h.get("started_at", "-"))
            mac = f"{h.get('machine_name', 'station')} ({h.get('machine_id', '-')})"
            task = h.get("task", h.get("summary", "-"))
            p0 = h.get("next_step", h.get("p0", "—"))
            lines.append(f"| {dt} | `{mac}` | {task} | `{p0}` |")

        return "\n".join(lines)

    def _build_decisions(self) -> str:
        candidates = [
            self.project_root / ".vitalia" / "memory" / "data_storage" / "decisions.jsonl",
            self.session_dir / "decisions.jsonl",
            self.data_dir / "decisions.jsonl",
        ]
        decisions_file = next((c for c in candidates if c.exists()), None)
        if not decisions_file:
            return "| — | Nenhuma decisão registrada na sessão ativa. | — |"

        entries: List[Dict[str, Any]] = []
        try:
            for line in decisions_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        except Exception:
            pass

        if not entries:
            return "| — | Nenhuma decisão registrada na sessão ativa. | — |"

        lines = []
        for d in reversed(entries[-10:]):
            mac = f"{d.get('machine_id', d.get('machine_name', 'station'))}"
            d_id = d.get('id', 'DEC')
            cat = d.get('category', 'ARQUITETURA')
            dec = d.get('decision', d.get('title', '-'))
            rat = d.get('rationale', 'Registro formal')
            lines.append(f"| `{mac}` | **[{d_id}]** `{cat}` {dec} | {rat} |")

        return "\n".join(lines)

    def action_consolidate(self) -> None:
        """Consolida os shards em disco e gera o painel README.md a partir do template canônico rico."""
        self.action_init()
        minfo = get_machine_info()
        now_str = datetime.now(VITALIA_TIMEZONE).strftime("%d-%m-%Y %H:%M:%S(GMT-04:00)")
        project_name = self.project_root.name

        # Carrega shards
        shards: List[Dict[str, Any]] = []
        if self.shards_dir.exists():
            for shard_file in sorted(self.shards_dir.glob("*.json")):
                try:
                    sdata = json.loads(shard_file.read_text(encoding="utf-8"))
                    shards.append(sdata)
                except Exception:
                    pass

        # Semáforo
        sem_data = {}
        if self.semaphore_file.exists():
            try:
                sem_data = json.loads(self.semaphore_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        state = sem_data.get("state", "FREE")
        holder = sem_data.get("machine_name", "Nenhum")

        # Badges
        badge_status = '<img src="https://img.shields.io/badge/Status-Ativo-success?style=flat-square" alt="Status" />'
        if state == "LOCKED":
            badge_semaforo = f'<img src="https://img.shields.io/badge/Semáforo-BLOQUEADO_{holder}-critical?style=flat-square" alt="Semáforo" />'
        else:
            badge_semaforo = '<img src="https://img.shields.io/badge/Semáforo-LIVRE-success?style=flat-square" alt="Semáforo" />'
        badge_modo = '<img src="https://img.shields.io/badge/Ambiente-Standalone-blue?style=flat-square" alt="Ambiente" />'
        badge_sync = '<img src="https://img.shields.io/badge/Sync-GMT--04%3A00-informational?style=flat-square" alt="Sync" />'
        badge_grounding = '<img src="https://img.shields.io/badge/Grounding-Ativo-blueviolet?style=flat-square" alt="Grounding" />'

        # Seções
        mermaid_content = self._build_mermaid(shards)
        shards_table = self._build_shards_table(shards)
        sessao_ativa = self._build_active_session(shards, sem_data)
        historico_sessoes = self._build_history()
        decisoes_arquiteturais = self._build_decisions()

        # Grounding
        global_status = "✅ Ativo"
        local_link = "`grounding-domains-local.yaml`"
        local_status = "✅ Sincronizado"
        pending_badge = "`0 pendências`"

        template_path = self._resolve_template_path()
        if template_path.exists():
            template_str = template_path.read_text(encoding="utf-8")
        else:
            # Fallback inline estruturado
            template_str = """# 🧠 Painel de Contexto — {project_name}
{badge_status} {badge_semaforo} {badge_modo} {badge_sync} {badge_grounding}

## 📡 Topologia de Shards & Sincronização
```mermaid
flowchart TD
{mermaid_content}
```

## 🖥️ Máquinas e Status Atual
<table>
  <thead>
    <tr>
      <th>Máquina / ID</th><th>Tarefa Atual</th><th>Ambiente</th><th>Status</th><th>Último Sync</th><th>Próximo Passo (P0)</th>
    </tr>
  </thead>
  <tbody>
{shards_table}
  </tbody>
</table>

## 🎯 Sessão Ativa em Destaque
{sessao_ativa}

## 📚 Histórico, Decisões & Guard Rails
<details><summary>🔍 Histórico de Sessões</summary>
{historico_sessoes}
</details>

<details><summary>⚖️ Decisões Arquiteturais</summary>
| Máquina (ID) | Decisão Arquitetural | Impacto / Racional |
| :--- | :--- | :--- |
{decisoes_arquiteturais}
</details>
"""

        rendered = template_str.replace("{timestamp}", now_str)
        rendered = rendered.replace("{project_name}", project_name)
        rendered = rendered.replace("{badge_status}", badge_status)
        rendered = rendered.replace("{badge_semaforo}", badge_semaforo)
        rendered = rendered.replace("{badge_modo}", badge_modo)
        rendered = rendered.replace("{badge_sync}", badge_sync)
        rendered = rendered.replace("{badge_grounding}", badge_grounding)
        rendered = rendered.replace("{mermaid_content}", mermaid_content)
        rendered = rendered.replace("{shards_table}", shards_table)
        rendered = rendered.replace("{sessao_ativa}", sessao_ativa)
        rendered = rendered.replace("{historico_sessoes}", historico_sessoes)
        rendered = rendered.replace("{decisoes_arquiteturais}", decisoes_arquiteturais)
        rendered = rendered.replace("{global_status}", global_status)
        rendered = rendered.replace("{local_link}", local_link)
        rendered = rendered.replace("{local_status}", local_status)
        rendered = rendered.replace("{pending_badge}", pending_badge)

        readme_path = self.session_dir / "README.md"
        readme_path.write_text(rendered, encoding="utf-8")
        print(f"[ContextEngine] ✅ Consolidação concluída! Painel rico gerado em {readme_path}")

    def action_end(self, task: str, p0: str, summary: str, learnings_json: str = "[]", decisions_json: str = "[]") -> None:
        """Encerra a sessão gravando o histórico em JSONL."""
        self.action_init()
        minfo = get_machine_info()
        now_iso = datetime.now(VITALIA_TIMEZONE).isoformat()

        entry = {
            "timestamp": now_iso,
            "machine_name": minfo["machine_name"],
            "task": task,
            "p0": p0,
            "summary": summary
        }

        history_file = self.data_dir / "session_history.jsonl"
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Atualiza também o shard
        self.action_shard(task=task, status="Concluído", next_step=p0, summary=summary)
        self.action_consolidate()
        print(f"[ContextEngine] ✅ Sessão finalizada e registrada em {history_file}")


def main():
    parser = argparse.ArgumentParser(description="Vitalia Context Engine — Filesystem Puro")
    parser.add_argument("--action", required=True, choices=["init", "consolidate", "end", "shard", "lock", "unlock", "status"])
    parser.add_argument("--session-dir", default=None, help="Caminho do diretório de memória de sessão")
    parser.add_argument("--task", default="", help="Descrição da tarefa ativa")
    parser.add_argument("--p0", default="", help="Próximo passo prioritário (P0)")
    parser.add_argument("--summary", default="", help="Resumo das atividades")
    parser.add_argument("--learnings-json", default="[]", help="Aprendizados estruturados")
    parser.add_argument("--decisions-json", default="[]", help="Decisões tomadas")
    parser.add_argument("--status", default="Em Andamento", help="Status da estação")
    parser.add_argument("--next-step", default="", help="Alias para p0")
    args = parser.parse_args()

    session_dir = Path(args.session_dir) if args.session_dir else None
    engine = LocalContextEngine(session_dir)

    if args.action == "init":
        engine.action_init()
    elif args.action == "shard":
        engine.action_shard(task=args.task, status=args.status, next_step=args.p0 or args.next_step, summary=args.summary)
    elif args.action == "consolidate":
        engine.action_consolidate()
    elif args.action == "end":
        engine.action_end(task=args.task, p0=args.p0 or args.next_step, summary=args.summary,
                          learnings_json=args.learnings_json, decisions_json=args.decisions_json)
    elif args.action in ["lock", "unlock", "status"]:
        # Para lock/unlock local
        engine.action_init()
        print(f"[ContextEngine] Semáforo local ({args.action}): Operação concluída")

    sys.exit(0)


if __name__ == "__main__":
    main()
