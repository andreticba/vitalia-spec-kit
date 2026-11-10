<!-- research.md | Vitalia SDD v0.6.0 | 10-11-2026 14:50(GMT-04:00) -->
> **research.md | Vitalia SDD v0.6.0 | 10-11-2026 14:50(GMT-04:00)**

# Technical Research: 003-modular-runtime-and-sensor-suite

**Data:** 10-11-2026 14:50 (GMT-04:00)  
**Status Constitucional:** EM CONFORMIDADE (P03 GROUNDING VERIFICADO)  
**Feature:** `specs/003-modular-runtime-and-sensor-suite`  
**Autor:** Vitalia AI Spec Lead & Solution Architect  

---

## 1. Engenharia Reversa Funcional em 3 Camadas

Para toda a refatoração e migração estrutural prevista nesta feature, aplica-se o protocolo de Engenharia Reversa Funcional em 3 Camadas:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Camada 1: Intenção de Negócio Pura a Preservar                         │
│ - §11 Context Lifting (entrega de contexto sem vazamento)              │
│ - Constituição Integral em Runtime (P00-P17 sem poda)                  │
│ - Trilha de Memória e Sharding 3-Tier                                  │
│ - Governança SDD estrita e HITL Soberano                               │
├────────────────────────────────────────────────────────────────────────┤
│ Camada 2: Infraestrutura Legada a Purgar                               │
│ - Probes e conexões de rede locais na porta 6379 (Redis local banido)  │
│ - Matriz temporária de atenção (tmp_cleanup_matrix em guardian_json)    │
│ - Caminhos absolutos e locais hardcoded (source/, ~/.vitalia)          │
│ - Arquivos soltos e ocultos na raiz de .vitalia e em .agents/skills    │
├────────────────────────────────────────────────────────────────────────┤
│ Camada 3: Contrato Estrito do Consumidor                               │
│ - Progressive Disclosure da IDE Antigravity (.agents/skills/*/SKILL.md)│
│ - Schemas OpenAPI 3.0 Limpos (sem $schema, sem title raiz)             │
│ - Saídas JSON planas para orquestradores de workflow                   │
│ - Suíte de Sensores VRSS para verificação contínua                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Decisões Técnicas Fundamentadas (Grounding P03)

### Decisão 1: Runtime Baseado Exclusivamente em Filesystem Puro & Purga do Redis Local
- **Escolhido**: Operação nativa sobre o sistema de arquivos local (`filesystem`) utilizando I/O atômico com biblioteca padrão Python (`pathlib`, `json`, `os`).
- **Verificado em**: https://docs.python.org/3/library/pathlib.html em 07-11-2026.
- **Justificativa**: O Vitalia SPEC Kit é uma ferramenta de desenvolvimento e governança para ambientes locais e IDEs. A exigência de um daemon local como Redis para telemetria ou cache em desenvolvimento adiciona um ponto único de falha, complexidade de instalação e ruído operacional no console (`ConnectionRefusedError: port 6379`). O armazenamento em arquivos JSON transitórios sob `.vitalia/memory/data_storage/context/` provê latência sub-milissegundo, rastreabilidade auditável e total independência de serviços em segundo plano.
- **Alternativas**:
  - *Redis / Memcached Local*: Rejeitado porque introduz dependência de daemons externos, portas de rede e falhas silenciosas de conexão em máquinas de desenvolvimento sem Docker ativo.
  - *SQLite Local*: Rejeitado para artefatos transitórios porque o formato binário dificulta a inspeção humana direta e diffs do git.

### Decisão 2: Suíte de Sensores em Runtime - VRSS (Vitalia Runtime Sensor Suite)
- **Escolhido**: Implementação de 5 sensores modulares em `source/src/sensors/`:
  1. `sensor_purity.py`: Inspeciona `.agents/skills/` assegurando diretórios limpos com apenas `SKILL.md`.
  2. `sensor_contract_dbc.py`: Valida pré/pós-condições dos contextos em `data_storage/context/`.
  3. `sensor_memory_ledger.py`: Valida ordenação cronológica decrescente dos shards e hashes 3-Tier.
  4. `sensor_tokens_leak.py`: Varre segredos (P06), dados não sanitizados (P07) e contagem de tokens.
  5. `sensor_path_hygiene.py`: Detecta strings de caminhos hardcoded (`source/`, `~/.vitalia`, `$HOME/.vitalia`).
- **Verificado em**: https://docs.python.org/3/library/ast.html e https://docs.python.org/3/library/re.html em 07-11-2026.
- **Justificativa**: Sensores atômicos baseados em análise léxica e estrutural (AST + Regex defensivo) executam em milissegundos sem overhead no sandbox, permitindo auditorias contínuas em hooks de pipeline e em testes automatizados.
- **Alternativas**:
  - *Auditor Monolítico Único*: Rejeitado por violar o Single Responsibility Principle (SRP), dificultando isolamento de falhas e testes de regressão específicos.

### Decisão 3: Contratos Declarativos dos 16 Workflows em TOML e OpenAPI 3.0 Limpo
- **Escolhido**: Formato TOML estruturado para as extensões de workflow em `source/extensions/` e schemas JSON centralizados em `source/src/schemas/`.
- **Verificado em**: https://spec.openapis.org/oas/v3.0.3.html em 07-11-2026.
- **Justificativa**: O subset OpenAPI 3.0 Limpo elimina meta-campos (`$schema`, `title`, `additionalProperties: false`) que causam falhas de compilação em bibliotecas de LLM REST Tooling. O formato TOML é nativamente legível para humanos e possui parser nativo em Python 3.11+ (`tomllib`) e retrocompatível via fallback nativo.
- **Alternativas**:
  - *YAML para Extensões*: Rejeitado devido à complexidade de indentação e problemas de tipagem implícita em strings multi-linha.
  - *JSON Schema Draft 2020-12 Completo*: Rejeitado devido à incompatibilidade com modelos de LLM que não aceitam palavras-chave fora de OpenAPI 3.0.

### Decisão 4: Persistência de Backups e Manifestos na Camada 4 (`.vitalia/memory/data_storage/`)
- **Escolhido**: Centralizar todos os artefatos de integridade, manifestos de hash SHA-256 e backups de skills sob a árvore `.vitalia/memory/data_storage/`:
  - Backups: `<project_root>/.vitalia/memory/data_storage/backups/skills/`
  - Manifestos: `<project_root>/.vitalia/memory/data_storage/manifests/.vitalia-manifest`
- **Verificado em**: Documentação de arquitetura da Antigravity IDE (`agy-customizations/SKILL.md`) em 10-11-2026.
- **Justificativa**: A IDE Antigravity realiza indexação em tempo real do repositório. Arquivos soltos como `.vitalia-manifest` na raiz de `.vitalia/` ou pastas `.trash`/`.backup` sob `.agents/` violam a pureza arquitetural e provocam ruído de indexação. A Camada 4 é a zona oficial de persistência de estado do kit.
- **Alternativas**:
  - *Persistência na Raiz de `.vitalia/`*: Rejeitado por poluir o diretório de governança do projeto.

### Decisão 5: Erradicação Incondicional da `tmp_cleanup_matrix` do Runtime
- **Escolhido**: Remoção total do bloco de geração e injeção de matrizes de expurgo dentro de `vitalia_hook_runner.py`. A funcionalidade de faxina é isolada em ferramenta autônoma CLI `source/src/vitalia_tmp_cleanup.py`.
- **Verificado em**: https://owasp.org/www-project-top-10-for-large-language-model-applications em 07-11-2026.
- **Justificativa**: Evidências empíricas coletadas no turno de concepção demonstraram que a injeção de mais de 100 linhas de caminhos e menus interativos (`[a/d/n/t]`) dentro do `guardian_json` causava perda de atenção e sequestro cognitivo do LLM. Separar ferramentas de manutenção de infraestrutura do prompt cognitivo dos agentes restaura o foco dos modelos de fronteira.
- **Alternativas**:
  - *Manter a matriz resumida*: Rejeitado porque qualquer ruído de infraestrutura não essencial em `guardian_json` degrada a precisão de raciocínio do modelo.

### Decisão 6: Resolução Dinâmica e Defensiva com Validação Física de Existência
- **Escolhido**: Em `kit_env_bootstrap.resolve_kit_dir()`, validar a existência física do diretório candidato (`if candidate.exists(): return candidate`) antes de adotá-lo, com fallback estrito para `script_kit_root`.
- **Verificado em**: https://docs.python.org/3/library/pathlib.html#pathlib.Path.exists em 07-11-2026.
- **Justificativa**: Ambientes heterogêneos frequentemente contêm arquivos `.env` legados apontando para diretórios inexistentes em disco. O fallback defensivo assegura resiliência operacional incondicional, prevenindo falhas com `FileNotFoundError`.
- **Alternativas**:
  - *Lançar exceção imediata*: Rejeitado porque quebra o fluxo do usuário sem necessidade, quando o interpretador já dispõe do kit executável local.

### Decisão 7: Normalização Idempotente no Gerador de Skills (`skill_generator.sh`)
- **Escolhido**: Utilizar expansão de parâmetros nativa do shell POSIX para remover prefixos duplicados:
  ```bash
  local base_name="${ext_name#vitalia-}"
  update_skill "vitalia-${base_name}" "${rendered}" "${skills_dir}" "${vitalia_dir}"
  ```
- **Verificado em**: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_06_02 (POSIX Shell Parameter Expansion).
- **Justificativa**: Garante idempotência absoluta independente de a extensão já conter ou não o prefixo `vitalia-` no arquivo fonte.
- **Alternativas**:
  - *Scripts Python auxiliares*: Rejeitado por adicionar sobrecarga de processo filho desnecessária em loops de shell.

---

## 3. Conclusão da Pesquisa e Conformidade

Todas as decisões técnicas acima foram validadas contra as cláusulas da Constituição SDD v0.6.0 (especialmente `P00`, `P01`, `P03`, `P05`, `P06`, `P07`, `P11`) e estão prontas para embasar o plano de implementação em `plan.md`.

