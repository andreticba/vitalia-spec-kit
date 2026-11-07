<!-- plan.md | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:33:00(GMT-04:00) -->
> **plan.md | Vitalia SPEC Kit v0.0.1 | 06-11-2026 22:33:00(GMT-04:00)**

# Plano Técnico de Implementação — Spec 003: Fix Universal Bootstrap Omissions (v0.0.1)

---

## 1. Visão Geral da Arquitetura & Diretrizes de Design

O presente plano técnico operacionaliza a remediação arquitetural da **Spec 003**. O objetivo central é estabelecer uma fundação estável, previsível e estritamente desacoplada para o **Vitalia SPEC Kit (v0.0.1)**.

### Princípios Estruturais:
1. **Single Responsibility Principle (SRP):** Cada script, módulo Python, template e perfil YAML possui uma única e bem definida razão para mudar.
2. **Instalação Filtrada Átomo a Átomo:** Eliminação total do comando `cp -r` cego no `kit-bootstrap.sh`. Cada arquivo autorizado é copiado individualmente com validação de existência e integridade.
3. **Resolução Dinâmica em 3 Níveis:** `VITALIA_KIT_DIR` é resolvido sem depender de caminhos hardcoded no sistema operacional.
4. **Governança Temporal de Conhecimento:** Domínios técnicos possuem data de validade (`valid_until`) e status auditável (`ACTIVE`/`STALE`), impedindo decisões baseadas em premissas defasadas.
5. **Restauração da Fidelidade Visual do Painel de Contexto:** O motor de contexto volta a gerar o `README.md` completo via template canônico com diagramas Mermaid, badges e seções colapsáveis `<details>`.
6. **Auditoria Estática Nativa na IDE:** O workflow `/vitalia-analyze` inspeciona a consistência entre plano e código real via Git Diff e análise de call-sites sem depender de CLIs de terminal.
7. **Blindagem do Sistema Host:** Testes automatizados executam estritamente em ambiente sandbox (`tmp_path`), garantindo zero modificação no host de desenvolvimento.

---

## 2. Architecture Decision Records (ADRs)

### ADR-001: Instalação Atômica com Prompt Interativo no `kit-bootstrap.sh`
- **Contexto:** A Spec 002 hardcodou caminhos e usou `cp -r source/bin/.`, omitindo pastas essenciais como `integrations/`, templates e `AGENTS.md`.
- **Decisão:** O `kit-bootstrap.sh` solicitará interativamente o destino (default `~/.vitalia-spec-kit`), expandirá o til (`~`) e criará a estrutura de diretórios explicitamente. Cada componente será copiado átomo a átomo, gravando o shim em `~/.local/bin/vitalia-install-project` com o caminho absoluto exportado.
- **Consequência:** Independência total de caminhos fixos; instalação robusta e reprodutível.

### ADR-002: Resolução em 3 Níveis de `VITALIA_KIT_DIR` e Purga de `~/.vitalia`
- **Contexto:** Scripts antigos buscavam o caminho legado `~/.vitalia` (com dependência de Redis 6379), causando poluição de runtime.
- **Decisão:** A função `resolve_kit_dir()` em `kit_env_bootstrap.py` adota estritamente:
  1. `os.environ.get("VITALIA_KIT_DIR")`
  2. Leitura do `.env` do projeto via parser nativo `load_dotenv_native()`
  3. Fallback canônico: `Path.home() / ".vitalia-spec-kit"`
  Qualquer referência a `~/.vitalia` é purgada do código.
- **Consequência:** Precedência clara e determinística; zero contaminação cruzada.

### ADR-003: Governança Temporal de Grounding e Escopo Expandido
- **Contexto:** O catálogo anterior misturava PII/PHI com condicionais de hardware local (`nvidia-smi`, GPU 6GB) e continha apenas domínios restritos.
- **Decisão:** Criar formalmente 10 domínios canônicos em `grounding_domains.yaml` e 9 domínios em `dynamic_questioning.yaml`. Injetar em cada domínio: `last_verified_at`, `valid_until`, `validity_window_days`, `status`, `last_update_source` e `update_history`. Definir componentes desacoplados regidos por SRP como o padrão canônico de engenharia de software.
- **Consequência:** Blindagem ontológica contra premissas desatualizadas; inteligência oracular contextualizada e moderna.

### ADR-004: Restauração do Renderizador Rico de Dashboard no `LocalContextEngine`
- **Contexto:** O `action_consolidate()` do `vitalia_context_engine.py` reduziu o painel de sessão a um arquivo de texto minimalista, descartando badges, topologia Mermaid e seções colapsáveis `<details>`.
- **Decisão:** Portar o template canônico higienizado para `source/templates/dashboard_template.md` (livre de menções a Redis) e integrar o motor de renderização visual dentro do `LocalContextEngine` em `source/src/vitalia_context_engine.py`. Resolver o template dinamicamente via `resolve_kit_dir()`.
- **Consequência:** Retorno da experiência visual rica e informativa no dashboard de sessão (`README.md`).

### ADR-005: Workflow Nativo `/vitalia-analyze` com Relatório Dual e HITL Soberano
- **Contexto:** Análise de consistência e código não pode ser um binário de terminal, mas um workflow de IDE com Sanduíche Constitucional.
- **Decisão:** Implementar a extensão `source/extensions/analyze.toml`, gerando a skill `.agents/skills/vitalia-analyze/SKILL.md`. Implementar modos `after_tasks` (consistência de planejamento) e `after_implement` (classificação Git Diff em 3 camadas e detecção estática de breaking changes em call-sites), emitindo relatório físico e chat com pausa mandatória HITL.
- **Consequência:** Governança soberana e blindagem contra scope drift durante o ciclo SDD.

---

## 3. Matriz de Rastreabilidade (Requisitos $\leftrightarrow$ Componentes)

| Requisito | Descrição Sintética | Componentes Envolvidos |
| :--- | :--- | :--- |
| **FR-001** | Prompt interativo de destino no bootstrap | `kit-bootstrap.sh` |
| **FR-002** | Instalação componente por componente sem `cp -r` cego | `kit-bootstrap.sh` |
| **FR-003** | Exclusão física de `gp_*` e `redis_detector.sh` | `kit-bootstrap.sh`, `source/profiles/`, `source/bin/lib/` |
| **FR-004** | Geração do shim com `export VITALIA_KIT_DIR` | `kit-bootstrap.sh` |
| **FR-005** | Resolução em 3 níveis no Python | `source/src/kit_env_bootstrap.py` |
| **FR-006** | Purga total do caminho legado `~/.vitalia` | `source/src/`, `source/bin/lib/` |
| **FR-007** | Zero suposição de `source/` no runtime instalado | Todos os scripts e templates |
| **FR-008** | Buffer de eventos de log em memória | `source/bin/lib/logger.sh` |
| **FR-009** | Gravação condicional de log no destino | `source/bin/lib/logger.sh`, `source/bin/install-project` |
| **FR-010** | Backup condicional de `.agents` e alerta explícito | `source/bin/lib/agent_preserver.sh`, `source/bin/install-project` |
| **FR-011** | Remoção de prompts e referências ao Gemini CLI | `source/bin/install-project` |
| **FR-012** | Template de skills com `---` na Linha 1 | `source/integrations/antigravity/SKILL.md.template` |
| **FR-013** | 10 domínios canônicos em `grounding_domains.yaml` | `source/profiles/grounding_domains.yaml` |
| **FR-014** | Campos temporais (`valid_until`, `status`) | `source/profiles/grounding_domains.yaml`, `dynamic_questioning.yaml` |
| **FR-015** | Rastreabilidade de fontes (`last_update_source`) | `source/profiles/grounding_domains.yaml`, `dynamic_questioning.yaml` |
| **FR-016** | Padrão SRP em `software_architecture` | `source/profiles/grounding_domains.yaml`, `dynamic_questioning.yaml` |
| **FR-017** | 7 domínios semânticos em `brainstorming_intents.yaml` | `source/profiles/brainstorming_intents.yaml` |
| **FR-018** | Purga de `guardian_profile = "gp_*"` nos 11 `.toml` | `source/extensions/*.toml` |
| **FR-019** | Template canônico do dashboard rico | `source/templates/dashboard_template.md` |
| **FR-020** | Renderizador visual rico integrado no engine | `source/src/vitalia_context_engine.py` |
| **FR-021** | Workflow nativo em `analyze.toml` (sem script CLI) | `source/extensions/analyze.toml`, `install-project` |
| **FR-022** | Git Diff 3 camadas, call-sites e pausa HITL | `source/extensions/analyze.toml` |
| **FR-023** | Teste de fumaça E2E em sandbox temporário | `tests/test_bootstrap_e2e_project.py` |

---

## 4. Topologia do Repositório e do Kit Instalado

```
vitalia-spec-kit/ (Repositório de Desenvolvimento)
├── kit-bootstrap.sh                                [Atualizado: prompt interativo, cópia atômica filtrada]
├── requirements.txt                                [Pinagem mínima: pyyaml, jinja2, pytest, jsonschema]
├── source/
│   ├── AGENTS.md                                   [Atualizado: anti-Lost in the Middle, SRP, HITL soberano]
│   ├── bin/
│   │   ├── install-project                         [Atualizado: log condicional, sem Gemini CLI, extensions.yml com analyze]
│   │   └── lib/
│   │       ├── agent_preserver.sh                  [Atualizado: VITALIA_KIT_DIR, sem ~/.vitalia]
│   │       ├── env_manager.sh                      [Preservação de VITALIA_KIT_DIR no .env]
│   │       ├── git_storage_manager.sh              [Storage de dados em filesystem]
│   │       ├── logger.sh                           [Atualizado: _VITALIA_LOG_BUFFER e write_install_log]
│   │       └── redis_detector.sh                   [EXCLUÍDO DEFINITIVAMENTE]
│   ├── extensions/
│   │   ├── analyze.toml                            [NOVO: workflow nativo de análise pré e pós-implementação]
│   │   └── (demais 11 .toml)                       [Atualizados: purga de guardian_profile = "gp_*"]
│   ├── integrations/
│   │   └── antigravity/
│   │       └── SKILL.md.template                   [Atualizado: Linha 1 com '---', {{VITALIA_KIT_DIR}}/.venv/bin/python3]
│   ├── profiles/
│   │   ├── agents_catalog.yaml                     [Catálogo de agentes limpo]
│   │   ├── brainstorming_intents.yaml              [Atualizado: 7 domínios semânticos expandidos]
│   │   ├── constitution.yaml                       [Constituição v0.0.1 com frescura temporal no P03]
│   │   ├── dynamic_questioning.yaml                [NOVO: 9 domínios canônicos, SRP, governança temporal]
│   │   ├── grounding_domains.yaml                  [NOVO: 10 domínios canônicos, fontes autoritativas, valid_until]
│   │   ├── routing_table.yaml                      [Tabela de rotas determinística]
│   │   └── gp_sdd-judge.yaml                       [EXCLUÍDO DEFINITIVAMENTE]
│   ├── src/
│   │   ├── kit_env_bootstrap.py                    [Atualizado: resolução 3 níveis, purga ~/.vitalia]
│   │   ├── vitalia_context_engine.py               [Atualizado: renderizador rico de dashboard com templates]
│   │   ├── vitalia_hook_runner.py                  [Atualizado: precedência de PATH com .venv/bin]
│   │   ├── vitalia_handoff.py                      [Atualizado: Zero Data Leak parametrizado]
│   │   └── hooks/
│   │       ├── guardian_context.py                 [Atualizado: purga gp_*, checagem de status ACTIVE/STALE]
│   │       └── scan_environment.py                [Sonda de integridade do runtime isolado]
│   └── templates/
│       └── dashboard_template.md                   [NOVO: template canônico do painel de sessão]
├── specs/
│   └── 003-fix-universal-bootstrap-omissions/      [Artefatos SDD da spec ativa]
└── tests/
    └── test_bootstrap_e2e_project.py               [NOVO: teste E2E completo em sandbox tmp_path]
```

---

## 5. Especificação Detalhada dos Componentes

### 5.1. `kit-bootstrap.sh`
- Solicita interativamente: `Diretório de instalação do Vitalia SPEC Kit [~/.vitalia-spec-kit]: `
- Normaliza o caminho com expansão de `~` via shell nativo (`eval echo "$input"`).
- Cria diretórios de destino: `${DEST}/{bin,bin/lib,extensions,profiles,src,src/hooks,templates,integrations/antigravity}`.
- Cria o virtualenv `${DEST}/.venv` e instala `requirements.txt`.
- Executa cópia componente a componente:
  ```bash
  # Binários e bibliotecas
  cp source/bin/install-project "${DEST}/bin/"
  cp source/bin/lib/agent_preserver.sh "${DEST}/bin/lib/"
  cp source/bin/lib/env_manager.sh "${DEST}/bin/lib/"
  cp source/bin/lib/git_storage_manager.sh "${DEST}/bin/lib/"
  cp source/bin/lib/logger.sh "${DEST}/bin/lib/"
  
  # Extensões e Perfis
  cp source/extensions/*.toml "${DEST}/extensions/"
  cp source/profiles/*.yaml "${DEST}/profiles/"
  
  # Motor Python e Hooks
  cp source/src/*.py "${DEST}/src/"
  cp source/src/hooks/*.py "${DEST}/src/hooks/"
  
  # Templates e Integrações
  cp source/templates/dashboard_template.md "${DEST}/templates/"
  cp source/integrations/antigravity/SKILL.md.template "${DEST}/integrations/antigravity/"
  cp source/AGENTS.md "${DEST}/AGENTS.md"
  ```
- Gera o shim em `~/.local/bin/vitalia-install-project` com `export VITALIA_KIT_DIR="${DEST}"`.

### 5.2. `source/bin/lib/logger.sh` & `install-project`
- Declara variável global `_VITALIA_LOG_BUFFER=""`.
- A cada log de info/warn/error, concatena no buffer com timestamp GMT-04:00.
- Função `write_install_log(target_path)` descarrega o buffer no arquivo de destino.
- Em `install-project`:
  - Se `DATA_REPO` informado $\rightarrow$ salva em `.vitalia/memory/data_storage/install_<timestamp>.log`.
  - Se `DATA_REPO` vazio $\rightarrow$ salva em `./install_<timestamp>.log` e alerta sobre ausência de backup de `.agents`.
  - Remove menu do Gemini CLI; ativa Antigravity IDE diretamente.
  - Escreve `.vitalia/extensions.yml` incluindo hooks para a extensão `analyze`.

### 5.3. `source/src/kit_env_bootstrap.py`
- Algoritmo de resolução:
  ```python
  def resolve_kit_dir(project_root: Optional[Path] = None) -> Path:
      # 1. os.environ
      if os.environ.get("VITALIA_KIT_DIR"):
          p = Path(os.environ["VITALIA_KIT_DIR"]).expanduser().resolve()
          if p.exists():
              return p
      # 2. .env do projeto
      root = project_root or find_project_root()
      env_file = root / ".env"
      if env_file.exists():
          parsed = load_dotenv_native(env_file)
          if "VITALIA_KIT_DIR" in parsed:
              p = Path(parsed["VITALIA_KIT_DIR"]).expanduser().resolve()
              if p.exists():
                  return p
      # 3. Fallback canônico
      return (Path.home() / ".vitalia-spec-kit").resolve()
  ```

### 5.4. `source/templates/dashboard_template.md` & `vitalia_context_engine.py`
- O template contém os marcadores: `{timestamp}`, `{project_name}`, `{badge_status}`, `{badge_semaforo}`, `{badge_modo}`, `{badge_sync}`, `{badge_grounding}`, `{mermaid_content}`, `{shards_table}`, `{sessao_ativa}`, `{historico_sessoes}`, `{decisoes_arquiteturais}`, `{global_status}`, `{local_link}`, `{local_status}`, `{pending_badge}`.
- O método `LocalContextEngine.action_consolidate()`:
  - Carrega o template via `resolve_kit_dir() / "templates" / "dashboard_template.md"`.
  - Monta o diagrama Mermaid `flowchart TD` iterando sobre os arquivos em `shards/`.
  - Monta a tabela executiva de máquinas com status verde/amarelo.
  - Carrega as últimas 10 entradas de `data/session_history.jsonl` e `data/decisions.jsonl`.
  - Injeta a lista de domínios monitorados a partir de `grounding_domains.yaml`.
  - Grava o painel renderizado em `.vitalia/memory/session/README.md`.

### 5.5. `source/profiles/grounding_domains.yaml` & `dynamic_questioning.yaml`
- Criação dos 10 domínios canônicos com `valid_until` em 2027 e URLs auditadas:
  - `provedores_de_ia`, `python_packages`, `web_technologies`, `external_apis`, `security_practices`, `regulations_compliance`, `cloud_services`, `scientific_claims`, `clinical_safety`, `software_architecture`.
- Em `software_architecture`, explicitar a adoção de componentes desacoplados regidos por SRP como baseline inviolável.
- Em `dynamic_questioning.yaml`, definir os 9 domínios canônicos com trade-offs estruturais desacoplados de infraestruturas locais descontinuadas.

### 5.6. `source/extensions/analyze.toml`
- Define os metadados do workflow `/vitalia-analyze`:
  - Hook `before`: extração de contexto via `vitalia_hook_runner.py`.
  - Instruções operacionais para os modos:
    - `after_tasks`: auditoria de consistência entre spec, plano e tasks.
    - `after_implement`: leitura do `git diff`, classificação em 3 camadas (Previsto, Adaptação Correlata, Órfão Real), verificação estática de aridade e imports em arquivos consumidores de funções alteradas, emissão do relatório `specs/<feature>/Relatório de Análise e Consistência - <fase>.md` e pausa mandatória HITL soberana.

---

## 6. Plano de Fases de Implementação

1. **Fase 1: Higienização de Componentes & Purga de Legado**
   - Excluir `source/bin/lib/redis_detector.sh`.
   - Excluir `source/profiles/gp_sdd-judge.yaml`.
   - Remover `guardian_profile = "gp_*"` de todos os 11 arquivos `.toml` em `source/extensions/`.
   - Atualizar `source/bin/lib/agent_preserver.sh` (eliminar `~/.vitalia`).
2. **Fase 2: Perfis Canônicos com Governança Temporal & Padrão SRP**
   - Criar `source/profiles/grounding_domains.yaml` com 10 domínios canônicos.
   - Criar `source/profiles/dynamic_questioning.yaml` com 9 domínios canônicos.
   - Atualizar `source/profiles/brainstorming_intents.yaml` com 7 domínios semânticos.
3. **Fase 3: Template & Restauração do Dashboard de Memória**
   - Criar `source/templates/dashboard_template.md`.
   - Atualizar `source/src/vitalia_context_engine.py` com renderizador rico completo.
4. **Fase 4: Motor de Resolução, Hooks e Workflow `analyze`**
   - Atualizar `source/src/kit_env_bootstrap.py` (resolução em 3 níveis sem `~/.vitalia`).
   - Atualizar `source/src/hooks/guardian_context.py` (checagem de status `ACTIVE`/`STALE`).
   - Criar `source/extensions/analyze.toml`.
   - Atualizar `source/integrations/antigravity/SKILL.md.template` (Linha 1 com `---`).
   - Atualizar `source/AGENTS.md`.
5. **Fase 5: Instaladores e Bibliotecas de Shell**
   - Atualizar `source/bin/lib/logger.sh` com buffer em memória e gravação no destino.
   - Atualizar `source/bin/install-project` (sem Gemini CLI, backup condicional, extensions.yml com analyze).
   - Atualizar `kit-bootstrap.sh` (prompt interativo, instalação átomo a átomo filtrada).
6. **Fase 6: Verificação & Teste E2E em Sandbox**
   - Implementar `tests/test_bootstrap_e2e_project.py`.
   - Executar `pytest tests/test_bootstrap_e2e_project.py` garantindo 100% de sucesso sem tocar no host.

---

## 7. Constitution Check

- [x] **P00 (Human Wellbeing First):** Salvaguardas clínicas e prioridade humana preservadas.
- [x] **P01 (SDD Pipeline Inviolability):** Plano formal elaborado e pronto para julgamento adversarial antes de qualquer código.
- [x] **P03 (External Verification Protocol / Grounding):** Todas as fontes oficiais verificadas e ativas.
- [x] **P04 (Timestamp & GMT-04:00 Integrity):** Formatação canônica dupla em todos os documentos.
- [x] **P11 (Hardware Agnosticism & Runtime Isolation):** Purga total de dependências locais de Redis, Celery, GPU/VRAM e Ollama; runtime isolado em `.venv`.
- [x] **P15 (Observability & Zero Data Leak):** Logs em buffer de memória e painel visual rico restaurado.
