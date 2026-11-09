<!-- research.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:49(GMT-04:00) -->
> **research.md | Vitalia SPEC Kit v0.0.1 | 08-11-2026 18:49(GMT-04:00)**

# Technical Research: Universal Bootstrap, Runtime Autônomo em 4 Camadas & Blindagem SDD (`specs/002-universal-bootstrap-runtime`)

- **Fontes Canônicas de Verdade (Anti-Alucinação):**
  1. [`.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/.vitalia/memory/data_storage/research/anchor-research-brainstorming-002-003.md)
  2. [`specs/002-universal-bootstrap-runtime/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/research-brainstorming.md)
  3. [`specs/002-universal-bootstrap-runtime/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime/spec.md)
  4. [`docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md)
- **Sub-Agente de Grounding (P03):** `vitalia-researcher` (`conversationId: e99297d5-0a94-4872-9795-9e871009f5be`)

---

## Decisão: Isolamento de Ambiente Python via `venv` Nativo com Pré-Checagem em `kit-bootstrap.sh`
- **Escolhido**: Módulo nativo `python3 -m venv` (`ensurepip`) em `${VITALIA_KIT_DIR}/.venv` com validação prévia em diretório temporário antes de criar a árvore do kit instalado.
- **Verificado em**: https://docs.python.org/3/library/venv.html em 08-11-2026 (HTTP 200)
- **Justificativa**: A documentação oficial da biblioteca padrão do Python 3 estabelece `venv` como o mecanismo canônico para isolamento de interpretador (`sys.prefix` / `sys.exec_prefix`) e pacotes sem poluir o Python do sistema operacional (PEP 668 `externally-managed-environment` em Ubuntu/Debian/WSL2). Em instalações novas de `WSL2/zsh` baseadas em Ubuntu/Debian, o pacote `python3-venv` (`ensurepip`) pode estar ausente por padrão; pré-validar `python3 -m venv` antes de criar `${VITALIA_KIT_DIR}` impede estados semi-instalados (`RCA-02`).
- **Alternativas**:
  - `pip install --user` ou `--break-system-packages` global: rejeitado porque viola a PEP 668 em distribuições Linux modernas e causa conflito de versões com projetos hospedeiros (P11).
  - Gerenciadores externos obrigatórios (`conda`, `poetry` ou `pipenv`): rejeitado porque exige binários de terceiros não presentes por padrão em uma estação Linux/WSL2 limpa.

---

## Decisão: Parser Nativo de Extensões `.toml` (`tomllib` + Fallback Seguro)
- **Escolhido**: Biblioteca padrão `tomllib` (nativa a partir do Python 3.11+) com fallback para `tomli` ou parser estrutural em `vitalia_hook_runner.py` e `install-project`.
- **Verificado em**: https://docs.python.org/3/library/tomllib.html em 08-11-2026 (HTTP 200)
- **Justificativa**: `tomllib` integra a biblioteca padrão do Python desde a versão 3.11 (PEP 680), permitindo o parse determinístico e seguro (read-only) das 16 extensões `.toml` do kit (`meta`, `hooks`, `tools`, `context`, `variables`, `transport`, `guardian`) sem requerer compilação C externa.
- **Alternativas**:
  - Pacote `toml` (terceiros, legado): rejeitado porque encontra-se sem manutenção ativa para TOML v1.0.0 e é desnecessário em Python 3.11+.
  - Extração puramente via `grep`/`sed` em Bash para campos multilinhas complexos: rejeitado porque corrompe strings multilinhas (`prompt = """..."""`) e arrays aninhados.

---

## Decisão: Clonagem Rasa (`git clone --depth=1`) com Fallback `git init` em `git_storage_manager.sh`
- **Escolhido**: Inspeção prévia via `git ls-remote "$repo_url" HEAD` seguida de `git clone --depth=1 "$repo_url" "$target_dir"` quando o repositório remoto existe e possui commits, e fallback `git init -b main "$target_dir"` quando o repositório remoto está vazio ou nenhuma URL é fornecida.
- **Verificado em**: https://git-scm.com/docs/git-clone em 08-11-2026 (HTTP 200)
- **Justificativa**: A documentação oficial do Git (`git-clone`) especifica que `--depth=1` cria um clone raso truncando o histórico ao último commit da branch padrão, reduzindo drasticamente o tempo de rede ao sincronizar `.vitalia/memory/session/` e `.vitalia/memory/data_storage/` entre estações de trabalho. Preservar esse fluxo (restaurando o que foi amputado em `RCA-04b`) garante continuidade multi-máquina sem quebrar projetos novos locais sem URL remota.
- **Alternativas**:
  - Executar apenas `git init` e `git remote add origin` sem clonar: rejeitado porque causa perda silenciosa do contexto remoto existente e conflito `non-fast-forward` no primeiro push (`RCA-04b`).
  - Exigir obrigatoriamente uma URL remota acessível para instalar o kit: rejeitado porque inviabiliza o Cenário E2E em projetos novos locais sem repositório remoto pré-criado.

---

## Decisão: Compilação de Contexto 100% Sem Poda (`Zero-Pruning Policy`) em Todos os 16 Workflows
- **Escolhido**: Eliminação integral dos algoritmos de poda por orçamento de tokens (`total_budget`), domínios ou severidade em `guardian_context.py`, combinada com 14 perfis `gp_*.yaml` declarando `no_prune: true`, `total_budget: 0` e `hardware_profile: "frontier"` para cobrir 100% dos 16 workflows canônicos.
- **Verificado em**: https://ai.google.dev/gemini-api/docs/models/gemini em 08-11-2026 (HTTP 200)
- **Justificativa**: Modelos de fronteira vigentes operam com janelas de contexto de 1M+ tokens, tornando obsoleta a poda de princípios constitucionais que existia para GPUs locais de 6 GB VRAM. Quando a Constituição (`constitution.yaml`, ~2.800 tokens) era podada em fases como `session-start` (`total_budget: 350`), o agente perdia princípios transversais críticos (`P03`, `P04`, `P05`, `P07`, `P11`, `P16`). Com a política de **Zero Poda em 100% dos workflows**, todos os 16 comandos recebem sempre os 18 princípios (`P00`–`P17`), 100% das fontes declaradas em `yaml_sources`, 100% de `decisions.jsonl` e `learnings.jsonl` e os `phase_guardrails` específicos da fase.
- **Alternativas**:
  - Manter poda condicional por workflow (`total_budget: 350` em `session-start`): rejeitado por determinação soberana do usuário e porque induz perda de regras constitucionais logo na abertura da sessão.
  - Excluir os arquivos `gp_*.yaml`: rejeitado porque os perfis carregam `phase_guardrails` e `phase_profiles` indispensáveis para especializar o comportamento adversarial de cada fase SDD.

---

## Decisão: Renderização Rica do Dashboard 3-Tier via Jinja2 e Ordenação Cronológica de Shards (`PyYAML`)
- **Escolhido**: Preservação da árvore modular `core/` (`context_engine.py`, `shard_manager.py`, `utils.py`) e `rendering/` (`dashboard_renderer.py`, `view_renderer.py`, `grounding_renderer.py`, `constitution_renderer.py`) renderizando `templates/dashboard_template.md` com `Jinja2` e `yaml.safe_load`, corrigindo `ShardManager.load_all_shards()` para ordenar por `parse_sync_time(shard.get("last_sync", ""))` decrescente.
- **Verificado em**: https://jinja.palletsprojects.com/en/stable/ e https://pyyaml.org/wiki/PyYAMLDocumentation em 08-11-2026 (HTTP 200)
- **Justificativa**: O painel publicado em `vitalia-spec-kit-context` depende de `dashboard_renderer.py` e `dashboard_template.md` para produzir a tabela HTML de máquinas, o grafo Mermaid de topologia (com labels entre aspas duplas — P16), a estação ativa em destaque e os blocos `<details>` de histórico, decisões e grounding. A ordenação cronológica explícita via `datetime.strptime` sobre `DD-MM-YYYY HH:MM:SS(GMT-04:00)` corrige o defeito em que `sorted(glob("*.yaml"))` selecionava `17a6f667.yaml` (`03-11-2026`) acima de `eb10269b.yaml` (`07-11-2026`) por mera ordem alfabética hexadecimal.
- **Alternativas**:
  - Substituir o pacote `rendering/` por concatenação simples de strings Markdown: rejeitado porque destrói o dashboard rico do repositório `vitalia-spec-kit-context` (`RCA-05`).
  - Ordenar shards pelo `mtime` do arquivo no sistema de arquivos local: rejeitado porque em um `git clone` todos os arquivos `.yaml` recebem o `mtime` do checkout, perdendo a cronologia real registrada no campo `last_sync`.

---

## Decisão: Validação Estrita de Contratos em Subset OpenAPI 3.0 Puro (`jsonschema`)
- **Escolhido**: Validação via `jsonschema` utilizando estritamente o subset compatível com OpenAPI 3.0.3 (`type`, `required`, `properties`, `items`, `enum`, `description`), proibindo `$schema`, `title` na raiz e `additionalProperties: false`.
- **Verificado em**: https://spec.openapis.org/oas/v3.0.3.html e https://python-jsonschema.readthedocs.io/en/stable/ em 08-11-2026 (HTTP 200)
- **Justificativa**: Compiladores de structured outputs / function calling de modelos de fronteira (como a API REST do Google Gemini) rejeitam com HTTP 400 schemas JSON que contenham meta-campos do JSON Schema Draft-07 (`$schema`, `title` raiz, `additionalProperties: false`). O uso do subset OpenAPI 3.0 limpo satisfaz simultaneamente o validador `jsonschema` em Python e os compiladores de modelos de fronteira (P11).
- **Alternativas**:
  - JSON Schema Draft-07 completo com `$schema` e `additionalProperties: false`: rejeitado por violação direta do princípio P11 (`BLOCKING`).

---

## Decisão: Suíte de Testes Comportamentais Executáveis em Subprocessos Isolados (`pytest` + `tmp_path`)
- **Escolhido**: Framework `pytest` com fixtures `tmp_path` e `monkeypatch`, executando scripts Bash e CLIs Python via `subprocess.run(..., env=..., cwd=...)` estruturados nas 4 modalidades da Matriz P05 (`[TEST:NEW]`, `[TEST:BUGFIX]`, `[TEST:REFACTOR]`, `[TEST:MIGRATION]`).
- **Verificado em**: https://docs.pytest.org/en/stable/ em 08-11-2026 (HTTP 200)
- **Justificativa**: `pytest` provê diretórios temporários isolados (`tmp_path`) por teste, permitindo simular uma estação limpa (`HOME`, `VITALIA_KIT_DIR`, repositórios Git bare locais para testar `git clone --depth=1`, simulação de falha de `python3 -m venv` via wrapper no `PATH`, e execução real de `kit-bootstrap.sh`, `install-project`, `vitalia_hook_runner.py`, `vitalia_handoff.py` e `vitalia_context_engine.py`) sem tocar em `~/.vitalia` nem em `~/.vitalia-spec-kit`.
- **Alternativas**:
  - Testes estáticos baseados em `assert path.is_file()` ou busca de substrings no código-fonte: rejeitado por veto constitucional `BLOCKING` (P05 — Anti-Shallow Testing).

---

## Síntese da Engenharia Reversa Funcional em 3 Camadas (Referência `~/.vitalia` $\rightarrow$ `source/`)

| Camada | Definição | Elementos Mapeados para `source/` |
|---|---|---|
| **Camada 1 — Intenção de Negócio Pura (Preservar 100%)** | Comportamentos funcionais estáveis que entregam valor real ao desenvolvedor. | 1. Bootstrap de `.venv` e shim `vitalia-install-project`.<br>2. Clonagem remota `git clone --depth=1` quando URL existe e `git init` local quando vazio em `git_storage_manager.sh`.<br>3. Geração de `.agents/AGENTS.md` e `.agents/skills/vitalia-*/SKILL.md`.<br>4. Motor 3-Tier completo (`vitalia_context_engine.py`, `core/*`, `rendering/*`, `templates/dashboard_template.md`).<br>5. Handoff atômico com `resolve_project_root()` em `vitalia_handoff.py`.<br>6. 16 workflows `.toml`, 14 lentes `gp_*.yaml` e 6 catálogos YAML. |
| **Camada 2 — Infraestrutura Legada e Defeitos (Purgar/Corrigir)** | Acoplamentos obsoletos e bugs reproduzidos em `~/.vitalia`. | 1. Purgar `redis_detector.sh`, probes TCP 6379/5432 em `scan_environment.py`/`kit_env_bootstrap.py` e `import redis` em `vitalia_hook_runner.py`/`guardian_context.py`/`context_engine.py`.<br>2. Purgar escrita em `~/.vitalia/tmp/` e `tmp_cleanup_matrix`, migrando para `.vitalia/memory/data_storage/context/<machine_id>/`.<br>3. Purgar algoritmos de poda em `guardian_context.py` e `total_budget: 350` em `gp_session-start.yaml` (100% dos workflows sem poda).<br>4. Corrigir ordenação alfabética em `shard_manager.py:105` para ordenação decrescente por `last_sync`.<br>5. Purgar os 11 `.toml` auxiliares legados de `~/.vitalia/extensions/` e referências a `sdd_judge.py`. |
| **Camada 3 — Contrato Estrito do Consumidor (Blindar)** | Invariantes exigidas pela Antigravity IDE, pelo ambiente `WSL2/zsh` e por P04/P11. | 1. Pureza 100% em `.agents/skills/` (proibido `.trash/` e `.vitalia-manifest` dentro de `.agents/skills/`).<br>2. Pré-validação de `python3 -m venv` antes de criar pastas em `kit-bootstrap.sh`.<br>3. Cabeçalho P04 `Vitalia SPEC Kit v0.0.1` e timestamps `DD-MM-YYYY HH:MM:SS(GMT-04:00)`.<br>4. Schemas JSON em OpenAPI 3.0 limpo. |

