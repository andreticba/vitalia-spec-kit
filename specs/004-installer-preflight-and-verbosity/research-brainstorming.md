<!-- research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:05(GMT-04:00) -->
> **research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:05(GMT-04:00)**

# Síntese de Concepção e Engenharia Reversa — Spec 004: Pre-Flight Check e Verbosidade no Processo de Instalação

---

## 1. Resumo Executivo e Decisões Acordadas (Consenso Socrático)

O objetivo da **Spec `004-installer-preflight-and-verbosity`** é blindar e tornar transparente a experiência do usuário durante o ciclo de instalação e bootstrap do **Vitalia SPEC Kit v0.0.1** (em [`kit-bootstrap.sh`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/kit-bootstrap.sh) e [`source/bin/install-project`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/bin/install-project)). O processo atual operava como "caixa-preta" silenciosa, apresentava fallbacks frágeis como `--system-site-packages` e falhava sem diagnóstico amigável diante de restrições de sistema de arquivos ou dependências ausentes.

### Decisões Consolidadas com o Usuário
1. **D1 — Pre-Flight Check Modular e Reutilizável (`source/bin/lib/preflight.sh`):**
   - Criação de uma biblioteca de inspeção compartilhada para padronizar validações prévias tanto no bootstrap da máquina (`kit-bootstrap.sh`) quanto na ativação do projeto (`install-project`).
   - Verificações de pré-requisito: Python semântico (`>= 3.10`), módulo `python3-venv` executável, permissões de escrita efetivas nos destinos (`TARGET_KIT_DIR`, `~/.local/bin`, `.agents/skills/`), Git funcional e conectividade/autenticação dos repositórios remotos informados.
2. **D2 — Purga Total e Definitiva de `--system-site-packages` (Inviolabilidade do `.venv` Puro):**
   - Eliminação incondicional do fallback para `--system-site-packages`. O kit exige um ambiente virtual estritamente isolado contendo suas próprias dependências puras (`pyyaml`, `jinja2`, `jsonschema`, `pytest`, `pytest-subtests`).
   - Se o `pip install` falhar, o instalador não mascara o erro degradando para pacotes globais do sistema: aborta com diagnóstico claro, indicando a causa exata e o caminho do log.
3. **D3 — Feedback Visual Estruturado e Redirecionamento de Logs para Arquivo:**
   - O processo de instalação adota feedback passo a passo com status visual (`⏳`, `✅`, `❌`, `⚠️`).
   - Durante etapas lentas (download do pip, compilação de venv), o terminal mantém feedback ativo sem ruído excessivo. Saídas detalhadas de ferramentas externas são redirecionadas para log temporário (`/tmp/vitalia-bootstrap.log` ou `/tmp/vitalia-install.log`), exibindo apenas as últimas linhas do rastro caso ocorra erro.
   - Suporte à flag opcional `-v` / `--verbose` para streaming ao vivo em ambientes de depuração ou CI.
4. **D4 — Diagnóstico Prescritivo Determinístico (Zero Elevação de Privilégio Root):**
   - O kit reporta falhas com comandos exatos e prontos para copiar e colar para o usuário remediar (ex: instrução específica para Debian/Ubuntu `sudo apt update && sudo apt install -y python3-venv`), sem tentar invocar `sudo` por conta própria.
5. **D5 — Comunicação Ativa de Variáveis de Ambiente e $PATH no Shell Ativo:**
   - Ao finalizar o bootstrap, o instalador destaca visualmente em banner que o terminal ativo precisa de `source ~/.bashrc` (ou `source ~/.zshrc`) para reconhecer o shim `vitalia-install-project` imediatamente.

---

## 2. Topologia das 4 Camadas Físicas e Relação com a Mudança

1. **Camada 1 — Repositório Raiz (`/home/andre/projetos/assistidos/vitalia-spec-kit`):**
   - Modificações em [`kit-bootstrap.sh`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/kit-bootstrap.sh), `source/bin/install-project`, nova biblioteca `source/bin/lib/preflight.sh` e testes em `tests/test_bootstrap_and_install.py`.
2. **Camada 2 — Kit Instalado na Máquina (`~/.vitalia-spec-kit`):**
   - Recebe a cópia integral de `source/bin/lib/preflight.sh` e o novo `install-project`.
3. **Camada 3 — Repositório de Memória de Sessão (`.vitalia/memory/session/`):**
   - Preservado e intocado (Regra da Cerca Elétrica).
4. **Camada 4 — Repositório de Dados Operacionais (`.vitalia/memory/data_storage/`):**
   - Armazena os envelopes de handoff e registros de rastreabilidade desta spec.

---

## 3. Engenharia Reversa Funcional em 3 Camadas (Componentes Afetados)

| Componente / Subsistema | Camada 1: Intenção Pura a Preservar | Camada 2: Legado / Débito a Purgar | Camada 3: Contrato do Consumidor (IDE / Shell) |
|---|---|---|---|
| **`kit-bootstrap.sh`** | Instalar o kit na máquina, criar `.venv` isolado, instalar dependências de `requirements.txt`, injetar PATH em `.bashrc`/`.zshrc` e gerar shim em `~/.local/bin/`. | **Purgar:** `pip install --quiet >/dev/null 2>&1` sem indicador, fallback silencioso para `python3 -m venv --system-site-packages`, ausência de pré-teste de escrita em `TARGET_KIT_DIR` e `~/.local/bin`. | Pre-flight com `preflight.sh`, `.venv` 100% puro, log detalhado em `/tmp/vitalia-bootstrap.log`, saída com status amigável e banner com comando de reload do shell. |
| **`source/bin/lib/preflight.sh` (Novo)** | Centralizar checagens de integridade de ambiente, SO, versões de binários e permissões de disco. | N/A (novo componente modular). | Funções reutilizáveis `check_python_version`, `check_venv_capability`, `check_writable_paths`, `check_git_requirements`, emitindo saídas estruturadas com códigos de saída semânticos. |
| **`source/bin/install-project`** | Ativar o kit em um projeto específico, configurar `.vitalia/`, criar repositórios de memória, configurar `.env` e gerar skills com pureza total em `.agents/skills/`. | Ausência de pre-flight de repositórios Git remotos (tentativa cega de conexão que travava ou emitia mensagens crípticas) e ausência de checagem de permissão de escrita em `.agents/`. | Validar acessibilidade e escrita no projeto antes de criar diretórios, checar URLs git previamente com timeout e emitir status claro em cada passo. |

---

## 4. Classificação da Estratégia de Testes pela Matriz P05

| Modalidade P05 | Alvo da Mudança | Cenário de Falsificação Comportamental (Caixa-Preta) |
|---|---|---|
| **`[TEST:NEW]`** | `source/bin/lib/preflight.sh` | Executar as funções de pre-flight em ambientes mockados: o teste falha se a verificação aprovar Python < 3.10, se não acusar falha em diretórios somente-leitura ou se falhar silenciosamente sem mensagem de erro. |
| **`[TEST:BUGFIX]`** | `kit-bootstrap.sh` (Purga de `--system-site-packages` e Validação de Escrita) | 1. Simular falha de rede/pip: o teste falha se o script criar o `.venv` com `--system-site-packages` em vez de abortar com código $\neq 0$ e mensagem prescritiva.<br/>2. Executar o bootstrap apontando `TARGET_KIT_DIR` para um diretório sem permissão de escrita: o teste falha se o script crashar com traceback não tratado em vez de ser interceptado pelo pre-flight no Passo 1. |
| **`[TEST:REFACTOR]`** | `kit-bootstrap.sh` & `install-project` consumindo `preflight.sh` | Executar o fluxo E2E existente (`test_kit_bootstrap_clean_machine_e2e`): o teste falha se a nova verbosidade ou a importação da biblioteca quebrar o contrato do shim, do `.venv` isolado ou as 16 skills em `.agents/skills/`. |

---

## 5. Requisitos Funcionais Preliminares e Escopo Delimitado

### In-Scope (MVP da Spec 004)
- **`FR-001` (`source/bin/lib/preflight.sh`):** Módulo bash com funções padronizadas para verificação semântica de Python (`>= 3.10`), teste prático de criação de `venv`, teste de permissão de escrita em diretórios alvo e validação de dependências git.
- **`FR-002` (Blindagem do `kit-bootstrap.sh`):** Integração do pre-flight check no início da execução, purga total de `--system-site-packages`, captura de logs do pip em `/tmp/vitalia-bootstrap.log` e exibição de progresso visual passo a passo.
- **`FR-003` (Blindagem do `install-project`):** Uso do pre-flight para validar permissões do projeto hospedeiro e validação prévia de URLs dos repositórios Git de sessão e dados.
- **`FR-004` (Guia Pós-Instalação Ativo):** Exibição ao final do bootstrap de instruções claras para recarregar o shell (`source ~/.bashrc` ou `source ~/.zshrc`) e testar o shim `vitalia-install-project --help`.

### 🚧 Ideias Estacionadas (Out of Scope)
- **Instalador GUI / Webhook de Instalação:** Adiado para versões futuras (foco estrito em CLI/bash robusto).
- **Auto-instalação com elevação `sudo` automática:** Rejeitado pelo Consenso Socrático (preserva o princípio de mínimo privilégio e portabilidade multi-distro).

---

## 6. Rastro de Pesquisa e Grounding (P03)

| # | Afirmação / Tecnologia | Fonte Canônica | URL Validada (HTTP 200) | Status Temporal | Data |
|---|---|---|---|---|---|
| 1 | Python `venv` nativo e isolamento sem system-site-packages | Python 3 Documentation | https://docs.python.org/3/library/venv.html | ACTIVE | 10-11-2026 |
| 2 | Tratamento defensivo de erros em Bash (`set -euo pipefail`) | GNU Bash Manual | https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html | ACTIVE | 10-11-2026 |
| 3 | Padrões de diretórios XDG (`~/.local/bin`) | FreeDesktop XDG Base Directory Spec | https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html | ACTIVE | 10-11-2026 |

