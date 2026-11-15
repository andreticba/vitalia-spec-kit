<!-- plan.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 12:21(GMT-04:00) -->
> **plan.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 12:21(GMT-04:00)**

# Implementation Plan: [BUGFIX] Faxineiro de Contexto CLI & Saúde de Sessão

**Branch**: `007-fix-context-cleanup-cli-and-session-health` | **Date**: 15-11-2026 | **Spec**: [spec.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/007-fix-context-cleanup-cli-and-session-health/spec.md)

---

## 1. Summary

Correção arquitetural definitiva (`[BUGFIX]`) do utilitário de limpeza de contexto efêmero (`source/src/vitalia_tmp_cleanup.py`), restauração fiel do menu interativo e contratos definidos na Seção 3 do Spec 003, implementação da sonda ultraleve de monitoramento em `source/src/hooks/scan_environment.py` emitindo contrato OpenAPI 3.0 Limpo, disponibilização do executável `source/bin/vitalia-clean`, e integração não-intrusiva do lembrete de manutenção em `source/extensions/session-start.toml`.

---

## 2. Technical Context

- **Language/Version**: Python 3.10+ (compatível com dual-runtime 3.10, 3.11, 3.12).
- **Primary Dependencies**: Biblioteca padrão do Python (`datetime`, `re`, `os`, `sys`, `pathlib`, `argparse`, `shutil`). Zero dependências externas de terceiros.
- **Storage**: Sistema de arquivos local (`.vitalia/memory/data_storage/context/<machine_id>/`).
- **Testing**: `pytest` com fixtures temporárias (`tmp_path`) e testes comportamentais de caixa-preta (`[TEST:BUGFIX]`).
- **Target Platform**: Linux / POSIX (bash shell).
- **Project Type**: CLI Utility & Sensor Extension para Antigravity IDE / Vitalia SPEC Kit.
- **Performance Goals**:
  - `scan_environment.py`: Execução da contagem de contexto < 50ms.
  - `vitalia-clean`: Varredura e apresentação do menu < 100ms para até 5.000 arquivos.
- **Constraints**:
  - Padrão Afirmativo em confirmações destrutivas (default `N`).
  - OpenAPI 3.0 Limpo (proibido `$schema`, root `title`, `additionalProperties: false`).
  - Preservação estrita da data civil de hoje no fuso GMT-04:00.

---

## 3. Constitution Check

| Princípio | Descrição | Status no Plano |
|---|---|---|
| **P00 (Human Wellbeing First)** | Prevenção de perda de dados ativos da sessão de trabalho. | ✅ CONFORME (Hoje é preservado por padrão). |
| **P01 (SDD Inviolability)** | Código implementado estritamente após plan.md e tasks.md aprovados. | ✅ CONFORME. |
| **P02 (User-Centric & Impact)** | DX transparente, não bloqueante, menus didáticos e flags para automação. | ✅ CONFORME. |
| **P03 (External Verification)** | Grounding temporal e Engenharia Reversa Funcional em 3 Camadas. | ✅ CONFORME (Documentado em research.md). |
| **P04 (Timestamp GMT-04:00)** | Cabeçalhos padronizados e agrupamento de datas em America/Cuiaba. | ✅ CONFORME. |
| **P05 (TDD Inviolável & Falsificação)** | Modalidade `[TEST:BUGFIX]` com reprodução da falha antes da correção. | ✅ CONFORME (Red Phase obrigatória). |
| **P10 (Didactic Engineering)** | Mensagens amigáveis, ajuda `--help` didática e menu autoexplicativo. | ✅ CONFORME. |
| **P11 (Dual-Runtime Isolation)** | Código executável tanto pelo interpretador do projeto quanto do kit. | ✅ CONFORME. |
| **P15 (Observability)** | Métrica `context_cleanup` estruturada no sensor `scan_environment.py`. | ✅ CONFORME (OpenAPI 3.0 Limpo). |

---

## 4. Technical Decisions

Detalhadas na íntegra em [research.md](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/007-fix-context-cleanup-cli-and-session-health/research.md):
1. **Extração de Data Civil**: Padrão de nome de arquivo regex com fallback para `st_mtime` em GMT-04:00.
2. **Parser de Intervalos**: Suporte a listas e faixas (`1,2`, `1-3`, `1, 3-5`).
3. **Sonda Ultraleve**: Varredura via `os.scandir` sem leitura de conteúdo de arquivos para manter overhead < 50ms.
4. **Executável Shim**: `source/bin/vitalia-clean` em bash puro encaminhando argumentos.

---

## 5. Matriz de Migração e Preservação Comportamental

| Componente | Comportamento Existente a Preservar (Invariante de Negócio) | Acoplamento / Defeito a Remover | Contrato do Consumidor & Estratégia de Teste (`[TEST:MIGRATION]` / `[TEST:BUGFIX]`) |
|---|---|---|---|
| `source/src/vitalia_tmp_cleanup.py` | Capacidade de purgar arquivos em lote. | Deleção cega sem confirmação e apagamento indiscriminado de arquivos de hoje. | Teste de caixa-preta garantindo que arquivos com estampa de hoje sobrevivam e que `--dry-run` não delete nada. |
| `source/src/hooks/scan_environment.py` | Verificação do ambiente, venvs e integridade de diretórios. | Ausência do nó `context_cleanup`. | Teste de esquema garantindo presença de `context_cleanup` com 4 campos obrigatórios no padrão OpenAPI 3.0 Limpo. |
| `source/extensions/session-start.toml` | Checklist de início de sessão. | Ausência de visibilidade sobre o acúmulo de arquivos de contexto. | Exibição de dica não-bloqueante formatada apenas quando `needs_cleanup == True`. |

---

## 6. Test Depth Agreement (TDA — Matriz Constitucional P05)

A modalidade primária desta feature é **`[TEST:BUGFIX]`**.

- **Critério Red-First de Falsificação:**
  - O teste em `source/tests/test_vitalia_tmp_cleanup.py` DEVE falhar contra a implementação atual de `source/src/vitalia_tmp_cleanup.py` antes da aplicação do patch.
  - A falha comprovada deve ser:
    1. O código antigo apaga os arquivos de hoje indiscriminadamente.
    2. O código antigo não possui o menu interativo com as opções `[a/d/n/t]`.
    3. O código antigo não possui os argumentos `--dry-run`, `--force`, `--purge-all`.
- **Critério Green-Phase:**
  - Após a implementação, 100% dos cenários de teste passam com louvor.
- **Critério de Profundidade:**
  - Proibidos testes superficiais (ex: apenas verificar se a função retorna sem erro).
  - Testes devem criar arquivos reais em diretórios temporários simulando datas passadas e a data de hoje, validar remoção física seletiva e integridade dos preservados.

---

## 7. Project Structure

### Documentation & Governance (this feature)
```text
specs/007-fix-context-cleanup-cli-and-session-health/
├── ambiguity_metrics.json
├── checklists/
│   └── requirements.md
├── contracts/
│   ├── cli-contracts.md
│   └── context_cleanup.schema.json
├── data-model.md
├── plan.md
├── quickstart.md
├── regencia-architect-plano-turno.md
├── research-brainstorming.md
├── research.md
└── spec.md
```

### Source Code Impacted
```text
source/
├── bin/
│   └── vitalia-clean                                 # NOVO: Executável shim
├── extensions/
│   └── session-start.toml                            # MODIFICADO: Dica de faxina de contexto
├── src/
│   ├── hooks/
│   │   └── scan_environment.py                      # MODIFICADO: Sonda ultraleve context_cleanup
│   └── vitalia_tmp_cleanup.py                       # MODIFICADO: Bugfix e menu interativo
└── tests/
    └── test_vitalia_tmp_cleanup.py                   # NOVO/MODIFICADO: Testes [TEST:BUGFIX]
```

---

## 8. Phase Overview

### Phase 1: Setup & Baseline
- Criação dos mocks e fixtures de arquivos de contexto para datas anteriores e data de hoje.
- Verificação do estado do repositório e isolamento de runtime.

### Phase 2: Red Phase (`[TEST:BUGFIX]`)
- Escrita dos testes comportamentais em `source/tests/test_vitalia_tmp_cleanup.py`:
  - `test_cleanup_preserves_today_by_default` (DEVE FALHAR no código antigo).
  - `test_cleanup_dry_run_leaves_files_intact` (DEVE FALHAR no código antigo).
  - `test_cleanup_menu_options_and_date_parsing` (DEVE FALHAR no código antigo).
  - `test_scan_environment_context_cleanup_node` (DEVE FALHAR no código antigo).
- Execução e comprovação do status RED.

### Phase 3: Implementation & Green Phase
- **US1: Bugfix do Utilitário Central (`vitalia_tmp_cleanup.py`)**
  - Implementação do parser de datas GMT-04:00 e agrupamento.
  - Implementação das flags CLI (`--dry-run`, `--force`, `--purge-all`, `--target-dir`).
  - Implementação do menu interativo `[a/d/n/t]`.
- **US2: Sonda Ultraleve no Sensor (`scan_environment.py`)**
  - Adição da contagem rápida de arquivos em `.vitalia/memory/data_storage/context/`.
  - Emissão do nó `context_cleanup` (OpenAPI 3.0 Limpo).
- **US3: Executável Shim e Lembrete de Sessão**
  - Criação de `source/bin/vitalia-clean` com permissão de execução (+x).
  - Ajuste de `source/extensions/session-start.toml` para exibir aviso condicional.
- Execução e comprovação do status GREEN.

### Phase 4: Polish & Acceptance Scenarios
- Validação end-to-end com os cenários de `quickstart.md`.
- Verificação de conformidade constitucional e geração de métricas finais.
