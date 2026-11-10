<!-- data-model.md | Vitalia SDD v0.6.0 | 10-11-2026 15:00(GMT-04:00) -->
> **data-model.md | Vitalia SDD v0.6.0 | 10-11-2026 15:00(GMT-04:00)**

# Data Model: 003-modular-runtime-and-sensor-suite (Camada 4 — Data Storage)

**Data:** 10-11-2026 15:00 (GMT-04:00)  
**Status Constitucional:** EM CONFORMIDADE (P07 PRIVACY BY DESIGN & DATA VAULT)  
**Feature:** `specs/003-modular-runtime-and-sensor-suite`  
**Autor:** Vitalia AI Spec Lead & Solution Architect  

---

## 1. Topologia da Camada 4 (`.vitalia/memory/data_storage/`)

Toda persistência transitória, histórica e de integridade do Vitalia SPEC Kit reside exclusivamente na Camada 4. A raiz do repositório `.vitalia/` permanece reservada estritamente para ponteiros estruturais (`feature.json`, `pipeline.json`, `extensions.yml`).

```
.vitalia/memory/data_storage/
├── context/                                    # Contextos transitórios gerados por §11 Context Lifting
│   └── <session_id>/
│       └── <workflow>_<timestamp>_<hash>.json  # Context Payload (Prompt + Guardian JSON)
├── backups/                                    # Backups automáticos de integridade
│   └── skills/
│       └── <skill_name>_<timestamp>.bak/       # Backup atômico de SKILL.md anterior
├── manifests/                                  # Trilha de integridade de hashes
│   └── .vitalia-manifest                       # Hash SHA-256 e timestamps de skills instaladas
└── handoffs/                                   # Handoffs determinísticos entre workflows
    └── handoff_<source>_to_<target>_<hash>.json
```

---

## 2. Modelos de Entidades

### 2.1 Entidade: Context Payload (`context_payload.json`)
- **Arquivo físico**: `.vitalia/memory/data_storage/context/<session_id>/<workflow>_<timestamp>_<hash>.json`
- **Ciclo de vida**: Criado pelo `vitalia_hook_runner.py` no início do workflow; lido pelo agente no turno de execução; expurgado por `vitalia_tmp_cleanup.py`.
- **Campos**:
  - `description` (*string*): Descrição do workflow.
  - `meta` (*object*): Versão, perfil de hardware (`frontier`), perfil de modelo (`pro`/`flash`), domain gates.
  - `hooks` (*object*): Lista de comandos executados em `before` e `after`.
  - `tools` (*object*): `required` (*array de strings*), `optional` (*array de strings*).
  - `context` (*object*): `reads` (*array de paths*), `writes` (*array de paths*).
  - `variables` (*object*): Mapeamento de variáveis de entrada e saída.
  - `transport` (*object*): Meio de transporte (`filesystem`), arquivo de estado, flag de shard.
  - `guardian` (*object*): Fontes YAML, profile do guardião, hardware profile.
  - `guardian_json` (*object*): Constituição integral, tabelas de grounding e regras de fase sem poda.
  - **Invariante Constitucional**: É terminantemente proibida a presença da chave `tmp_cleanup_matrix`.

### 2.2 Entidade: Skill Manifest Record (`.vitalia-manifest`)
- **Arquivo físico**: `.vitalia/memory/data_storage/manifests/.vitalia-manifest`
- **Ciclo de vida**: Atualizado por `skill_generator.sh` e `agent_preserver.sh` durante o ciclo de build/instalação de skills.
- **Formato**: Linhas de texto delimitadas por pipe (`|`):
  `timestamp | skill_dir | sha256_hash | source_toml`
- **Restrição**: Nunca pode residir na raiz de `.vitalia/` nem em `.agents/skills/`.

### 2.3 Entidade: Skill Backup Archive (`skill_backup`)
- **Diretório físico**: `.vitalia/memory/data_storage/backups/skills/<skill_name>_<timestamp>.bak/`
- **Conteúdo**: Cópia física integral do `SKILL.md` prévio antes de sofrer sobrescrita.
- **Retenção**: Gerenciado pelo utilitário `vitalia_tmp_cleanup.py`.

### 2.4 Entidade: Handoff Transitório (`handoff_record.json`)
- **Arquivo físico**: `.vitalia/memory/data_storage/handoffs/handoff_<source>_to_<target>_<hash>.json`
- **Ciclo de vida**: Emitido ao término de um workflow e consumido determinísticamente pelo workflow seguinte.
- **Campos**:
  - `handoff_id` (*string*): Hash SHA-256 parcial.
  - `source_workflow` (*string*): Workflow de origem.
  - `target_workflow` (*string*): Workflow de destino proposto.
  - `timestamp` (*string*): Timestamp no formato GMT-04:00.
  - `feature_directory` (*string*): Diretório da feature ativa.
  - `artifacts` (*array de strings*): Links para os artefatos produzidos.
  - `status` (*string*): `pending`, `consumed`, `archived`.

