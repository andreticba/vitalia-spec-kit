<!-- plan.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:30(GMT-04:00) -->
> **plan.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:30(GMT-04:00)**

# Implementation Plan: Spec 004 — Installer Preflight and Verbosity

**Branch**: `004-installer-preflight-and-verbosity` | **Date**: 10-11-2026 | **Spec**: [`specs/004-installer-preflight-and-verbosity/spec.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/004-installer-preflight-and-verbosity/spec.md)

---

## 1. Summary

Implementação da biblioteca modular de pre-flight check ([`source/bin/lib/preflight.sh`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/bin/lib/preflight.sh)) e integração com [`kit-bootstrap.sh`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/kit-bootstrap.sh) e [`source/bin/install-project`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/bin/install-project). O plano inclui a purga total de `--system-site-packages` garantindo a inviolabilidade do ambiente virtual isolado, redirecionamento defensivo de logs de instalação para `/tmp/vitalia-bootstrap-${UID}.log`, feedback visual passo a passo com status (`⏳`, `✅`, `❌`, `⚠️`) e emissão de banner contextual para recarregamento do shell ativo.

---

## 2. Technical Context

- **Linguagem / Runtime**: Bash 4.4+ / 5.x (compatível com `set -euo pipefail` e shells Zsh no WSL2) e Python >= 3.10.
- **Dependências Principais**: Interpretador nativo `python3` e módulos `venv` / `ensurepip`.
- **Armazenamento de Logs**: Sistema de arquivos em `/tmp/vitalia-bootstrap-${UID}.log` com fallback resiliente `mktemp`.
- **Testing**: Suíte automatizada com `pytest` e testes de caixa-preta via `subprocess.run` em ambientes simulados `tmp_path`.
- **Plataforma Alvo**: Linux padrão, WSL2/Ubuntu com shells `bash` e `zsh`.
- **Tipo de Projeto**: CLI / Shell Installer Toolchain.
- **Metas de Performance**: Pre-flight check executado em $< 2$ segundos; tempo de feedback visual contínuo $\le 1$ segundo durante operações lentas.
- **Restrições**: Proibição estrita de `--system-site-packages`; proibição de elevação automática com `sudo`; pureza total do diretório `.agents/skills/`.

---

## 3. Constitution Check

- **P00 (Purpose Arbiter):** Aprovado. Reduz atrito cognitivo e elimina falhas silenciosas de instalação.
- **P01 (SDD Inviolability):** Aprovado. Todas as mudanças decorrem de `spec.md` formalmente especificada.
- **P03 (External Grounding):** Aprovado. Todas as técnicas de verificação validadas na Seção 1 a 5 do `research.md`.
- **P04 (Timestamp GMT-04:00):** Aprovado. Cabeçalho duplo e fuso `America/Cuiaba` em 100% dos documentos.
- **P05 (TDD & Falsificação):** Aprovado. Test Depth Agreement (TDA) estipulado com 4 modalidades e cenários de falsificação.
- **P10 (Didactics-First):** Aprovado. Mensagens de erro com diagnósticos acionáveis e comandos de cópia e cola.
- **P11 (Runtime Autonomy):** Aprovado. Purga definitiva de `--system-site-packages` e isolamento estrito de `.venv`.
- **P15 (Observability):** Aprovado. Rastreabilidade de saídas volumosas do `pip` em arquivo `/tmp/`.
- **P16 (Mermaid Integrity):** Aprovado. Labels entre aspas duplas no diagrama arquitetural.

---

## 4. Technical Decisions

Consolidadas em detalhes em [`specs/004-installer-preflight-and-verbosity/research.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/004-installer-preflight-and-verbosity/research.md):
- **D1:** Verificação semântica de versão do Python via `sys.version_info >= (3, 10)` sem dependência de parsing frágil de strings.
- **D2:** Teste de permissão de escrita em diretórios inexistentes inspecionando o primeiro ancestral existente com arquivo temporário probe via `mktemp`.
- **D3:** Isolamento de logs por UID (`/tmp/vitalia-bootstrap-${UID}.log`) com fallback `mktemp` para evitar colisões multi-usuário em `/tmp`.
- **D4:** Purga incondicional de `--system-site-packages` com interrupção limpa e despejo das 15 últimas linhas do erro.
- **D5:** Detecção dinâmica do shell ativo (`$SHELL`, `$ZSH_VERSION`, `$BASH_VERSION`) para orientar `source ~/.bashrc` ou `source ~/.zshrc`.

---

## 5. Matriz de Migração e Preservação Comportamental

| Componente | Comportamento Existente a Preservar (Invariante de Negócio) | Acoplamento / Defeito a Remover | Contrato do Consumidor & Estratégia de Teste (`[TEST:MIGRATION]`) |
|---|---|---|---|
| [`kit-bootstrap.sh`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/kit-bootstrap.sh) | Instalação global na máquina hospedeira em `${TARGET_KIT_DIR}`, suporte a `--target-dir`, `--non-interactive`, geração de shim em `~/.local/bin/vitalia-install-project` e injeção idempotente em `.bashrc`/`.zshrc`. | Purgar supressão silenciosa `pip >/dev/null 2>&1`, purgar fallback para `--system-site-packages` e purgar `mkdir` sem pre-flight prévio. | `[TEST:MIGRATION]`: Executar `test_kit_bootstrap_clean_machine_e2e` garantindo que toda a topologia das 4 camadas e o shim permaneçam 100% funcionais, agora com pre-flight ativo e `.venv` puro. |
| [`source/bin/install-project`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/bin/install-project) | Ativação do kit em projeto hospedeiro, pureza total em `.agents/skills/`, geração das 16 skills e configuração de memória em `.vitalia/`. | Purgar tentativas cegas de inicialização/clonagem Git sem validação prévia de permissões de escrita no projeto. | `[TEST:MIGRATION]`: Testar ativação em projeto novo provando que as checagens de `preflight.sh` operam integradas sem quebrar o provisionamento. |

---

## 6. Test Depth Agreement (TDA — Matriz Constitucional P05)

| Modalidade P05 | Alvo da Mudança | Cenário de Falsificação Comportamental (Como o teste falha se a regra quebrar) |
|---|---|---|
| **`[TEST:NEW]`** | `source/bin/lib/preflight.sh` | 1. `test_preflight_python_version`: Invocar a função com binário mock que relata Python 3.9; o teste falha se a função retornar código 0.<br/>2. `test_preflight_writable_target`: Passar caminho dentro de diretório `chmod 555`; o teste falha se o pre-flight aprovar o caminho ou se criar arquivos órfãos não removidos.<br/>3. `test_preflight_missing_venv_guidance`: Simular falha de `python3 -m venv`; o teste falha se a mensagem de erro não contiver a instrução prescritiva de instalação (`python3-venv`). |
| **`[TEST:BUGFIX]`** | `kit-bootstrap.sh` | 1. `test_bootstrap_rejects_system_site_packages`: Simular falha na etapa do pip; o teste falha se o script recorrer a `--system-site-packages` em vez de abortar com código $\neq 0$ e exibir o caminho do log.<br/>2. `test_bootstrap_aborts_early_on_readonly_destination`: Passar `--target-dir` em pasta sem permissão de escrita; o teste falha se o script criar qualquer arquivo ou tentar rodar `pip` antes de abortar no Passo 0. |
| **`[TEST:REFACTOR]`** | `kit-bootstrap.sh` & `install-project` | `test_bootstrap_clean_machine_e2e_with_preflight`: Executar o ciclo completo em `fake_home`; o teste falha se a nova verbosidade ou a integração de `preflight.sh` quebrar a idempotência de `.bashrc`/`.zshrc`, o shim `vitalia-install-project --help` ou o `.venv` puro. |

---

## 7. Project Structure

### Documentation (this feature)
```text
specs/004-installer-preflight-and-verbosity/
├── research-brainstorming.md
├── regencia-architect-plano-turno.md
├── spec.md
├── checklists/
│   └── requirements.md
├── ambiguity_metrics.json
├── research.md
├── plan.md
├── contracts/
│   └── cli-contracts.md
└── quickstart.md
```

### Source Code Afetado
```text
kit-bootstrap.sh                    # Atualizado com preflight.sh, verbosidade, log e purga de --system-site-packages
source/
├── bin/
│   ├── install-project            # Atualizado com preflight.sh
│   └── lib/
│       └── preflight.sh           # NOVO: Módulo compartilhado de pré-validações
tests/
└── test_bootstrap_and_install.py   # Atualizado com testes [TEST:NEW], [TEST:BUGFIX] e [TEST:REFACTOR]
```

---

## 8. Phase Overview

- **Fase 1: Setup & TDD Red Phase**
  - Implementar os testes unitários e comportamentais em `tests/test_bootstrap_and_install.py` cobrindo `[TEST:NEW]` (`preflight.sh`) e `[TEST:BUGFIX]` (purga de `--system-site-packages` e falha precoce em read-only).
  - Comprovar a falha vermelha executável (**Red Phase**).
- **Fase 2: Implementação da Biblioteca `source/bin/lib/preflight.sh`**
  - Criar `source/bin/lib/preflight.sh` com as funções `check_python_version_semver`, `check_venv_capability`, `check_writable_target` e `check_git_requirements`.
  - Tornar os testes unitários da biblioteca verdes.
- **Fase 3: Refatoração e Blindagem do `kit-bootstrap.sh`**
  - Carregar `source/bin/lib/preflight.sh` no `kit-bootstrap.sh`.
  - Integrar o Passo 0 (Pre-flight), purgar `--system-site-packages`, direcionar logs para `/tmp/vitalia-bootstrap-${UID}.log`, adicionar feedback visual (`⏳`, `✅`) e banner com detecção dinâmica de shell.
  - Tornar os testes de bugfix e regressão verdes (**Green Phase**).
- **Fase 4: Integração no `install-project` & Validação E2E**
  - Integrar validações de `preflight.sh` no `source/bin/install-project`.
  - Executar a suíte completa de testes (`pytest tests/`) e validar conformidade constitucional.

