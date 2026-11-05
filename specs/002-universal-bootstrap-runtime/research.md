<!-- research.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:10(GMT-04:00) -->
> **research.md | Vitalia SPEC Kit v0.0.1 | 04-11-2026 20:10(GMT-04:00)**

# Pesquisa Técnica & Decisões Arquiteturais — Spec 002: Universal Bootstrap & Runtime

* **Feature:** [specs/002-universal-bootstrap-runtime](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/002-universal-bootstrap-runtime)
* **Status:** Concluído (Base técnica para o `plan.md`)
* **Data da Pesquisa:** 04-11-2026 20:10(GMT-04:00)
* **Governança:** Vitalia SPEC Kit v0.0.1 (Princípio P03 — External Verification Protocol)

---

## 1. Decisão Técnica 1: Isolamento de Runtime da Ferramenta (PEP 668 & pipx Pattern)

* **Problema:** A execução de ferramentas CLI globais em distribuições Linux modernas (Debian 12+, Ubuntu 23.04+, Fedora 38+) bloqueia a instalação de pacotes Python via `pip install` global devido à política de "Externally Managed Environments" (PEP 668), causando quebra de ambientes e conflito de dependências com projetos do usuário.
* **Escolhido:** Criação de ambiente virtual Python isolado e dedicado em `~/.vitalia-spec-kit/.venv/`, com instalação autocontida de dependências e sem contaminação do ambiente host.
* **Verificado em:** [`https://github.com/pypa/pipx`](https://github.com/pypa/pipx) e [`https://peps.python.org/pep-0668/`](https://peps.python.org/pep-0668/) em 03-11-2026.
* **Justificativa:** O padrão de isolamento de aplicações estabelecido pelo PyPA garante que a ferramenta mantenha seus próprios pacotes (`pyyaml`, `jinja2`, `click`) sem interferir no interpretador do sistema nem nos virtualenvs locais dos projetos dos usuários.
* **Alternativas Rejeitadas:**
  * *Instalação Global com `--break-system-packages`:* Rejeitada por violar a integridade do sistema operacional e quebrar ferramentas de sistema.
  * *Container Docker Obrigatório:* Rejeitada por introduzir fricção de bootstrap, necessidade de daemon ativo e latência em execuções de sub-segundo.

---

## 2. Decisão Técnica 2: Bootstrap Idempotente em Shell Script Nativo

* **Problema:** Instaladores com ferramentas pesadas ou compiladores adicionam dependências prévias de bootstrap (ex: exigir pipx já instalado, Docker ou gerenciadores de pacotes específicos).
* **Escolhido:** Script `kit-bootstrap.sh` na raiz do repositório em Shell Script compatível com POSIX/Bash, executável diretamente após `git clone`.
* **Verificado em:** [`https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html`](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html) em 03-11-2026.
* **Justificativa:** Garante portabilidade universal imediata em qualquer ambiente Linux/macOS limpo contendo apenas `bash`, `python3` e `git`. O script implementa verificações de idempotência: se o ambiente `.venv` já existir, ele valida sua integridade e atualiza as dependências em vez de falhar.
* **Alternativas Rejeitadas:**
  * *Makefile:* Rejeitada porque `make` pode não estar pré-instalado em imagens de containers ou sistemas desktop mínimos.
  * *Poetry / Hatch:* Rejeitada porque exigiria o gerenciador instalado previamente pelo usuário, quebrando o princípio de instalação zero-dependency.

---

## 3. Decisão Técnica 3: Disponibilização Global via Shims em `~/.local/bin/`

* **Problema:** Como permitir que o usuário invoque `vitalia-install-project` ou outros comandos a partir de qualquer pasta sem exigir ativação manual de `source ~/.vitalia-spec-kit/.venv/bin/activate`.
* **Escolhido:** Geração de scripts wrapper (shims) leves e idempotentes em `~/.local/bin/`, apontando explicitamente para o interpretador `~/.vitalia-spec-kit/.venv/bin/python3`.
* **Verificado em:** [`https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html`](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) (XDG Base Directory Specification) em 03-11-2026.
* **Justificativa:** `~/.local/bin/` é o padrão canônico para executáveis de usuário em ambientes POSIX, já incluído no `$PATH` da esmagadora maioria dos shells modernos (bash, zsh, fish).
* **Alternativas Rejeitadas:**
  * *Aliases no `.bashrc` / `.zshrc`:* Rejeitada por modificar arquivos de inicialização do shell do usuário e não funcionar em subprocessos não-interativos da IDE.
  * *Links Simbólicos em `/usr/local/bin`:* Rejeitada por exigir privilégios de `sudo` e quebrar em ambientes corporativos ou restritos.

---

## 4. Decisão Técnica 4: Persistência de Context Lifting sem Containers (Filesystem-Only)

* **Problema:** O kit legado dependia de chamadas ao Redis (porta 6379) para filas e salvava arquivos de contexto em `~/.vitalia/tmp/` (compartilhado globalmente), gerando falhas quando o Redis não estava ativo e violando o princípio P07 (Zero Data Leak) entre projetos distintos.
* **Escolhido:** Desacoplamento radical de containers. O Context Lifting grava o JSON estritamente dentro da pasta do projeto em:
  `.vitalia/memory/data_storage/context/<workflow>_<timestamp>_<machine_id>_<hash>.json`
  com a pasta `.vitalia/memory` protegida por regra no `.gitignore` da aplicação hospedeira.
* **Verificado em:** Anthropic Engineering — *Scaling Managed Agents: Decoupling the brain from the hands & session* [`https://www.anthropic.com/engineering/managed-agents`](https://www.anthropic.com/engineering/managed-agents) em 03-11-2026.
* **Justificativa:** O sistema de arquivos local é transacional, possui latência inferior a 10 milissegundos e não depende de daemons. A inclusão no `.gitignore` garante que dados e regras não poluam o repositório de código, mantendo os arquivos confinados ao disco local do projeto.
* **Alternativas Rejeitadas:**
  * *Redis Streams:* Rejeitada por forçar a execução de um container Docker local permanentemente consumindo portas e memória.
  * *Diretório global `/tmp/`:* Rejeitada por risco de vazamento de informações e colisão de nomes em ambientes com múltiplos usuários.

---

## 5. Decisão Técnica 5: Diagnóstico Desacoplado de Ambiente (`scan_environment.py`)

* **Problema:** O hook `scan_environment.py` realizava tentativas de conexão TCP nas portas `6379` (Redis) e `5432` (Postgres), retornando status `DEGRADED` e emitindo alertas espúrios.
* **Escolhido:** Reescrita do `scan_environment.py` orientada estritamente ao filesystem e ao runtime isolado:
  - Presença e sanidade de `.env` local;
  - Presença de `.agents/AGENTS.md` e `.agents/skills/`;
  - Integridade do interpretador isolado em `~/.vitalia-spec-kit/.venv/bin/python3`.
* **Verificado em:** Práticas de Health Checks desacoplados para ferramentas de desenvolvimento de 2026.
* **Justificativa:** Se o kit opera 100% em filesystem, verificar portas de rede é código morto e fonte de falsos positivos.
* **Alternativas Rejeitadas:**
  * *Manter probes com flag `--ignore-redis`:* Rejeitada por perpetuar dívida técnica e confusão operacional.

---

## 6. Decisão Técnica 6: Contratos JSON OpenAPI 3.0 Puros (Sem Meta-Campos)

* **Problema:** Compiladores de schemas de modelos de fronteira (como o Google Gemini REST API) rejeitam schemas contendo palavras-chave Draft-07 como `$schema`, `title` no nó raiz e `additionalProperties: false`, gerando erros HTTP 400 em tempo de execução.
* **Escolhido:** Todo schema em `contracts/` e schemas internos adotam o subset OpenAPI 3.0 limpo, conforme a decisão histórica `246ef7bd` e aprendizado `311d5098`.
* **Verificado em:** OpenAPI 3.0.3 Specification [`https://spec.openapis.org/oas/v3.0.3`](https://spec.openapis.org/oas/v3.0.3) e Google Gemini API Structured Outputs Guide em 03-11-2026.
* **Justificativa:** Previne quebras em chamadas estruturadas de ferramentas e garante interoperabilidade agnóstica entre modelos de diferentes provedores.
* **Alternativas Rejeitadas:**
  * *JSON Schema Draft 2020-12:* Rejeitada por incompatibilidade severa com parsers de LLMs comerciais.
