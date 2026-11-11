<!-- spec.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:20(GMT-04:00) -->
> **spec.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:20(GMT-04:00)**

# Especificação de Funcionalidade: Pre-Flight Check, Isolamento Estrito do `.venv` e Observabilidade Passo a Passo na Instalação

**Data:** 10-11-2026  
**Versão:** 0.0.1  
**Autor/Agente:** Vitalia SPEC Kit Architect & Requirements Engineer  
**Feature:** `specs/004-installer-preflight-and-verbosity`  
**Status:** DRAFT (Submetido à Auditoria `/vitalia-judge --mode=specify` e Aprovação HITL)  
**Fontes Canônicas Obrigatórias:**
- [`specs/004-installer-preflight-and-verbosity/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/004-installer-preflight-and-verbosity/research-brainstorming.md)
- [`docs/adr/ADR-0003-installer-preflight-isolated-venv-observability.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0003-installer-preflight-isolated-venv-observability.md)
- [`specs/004-installer-preflight-and-verbosity/regencia-architect-plano-turno.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/004-installer-preflight-and-verbosity/regencia-architect-plano-turno.md)

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

### 1.1 Problema de Negócio e Engenharia
Durante a experiência real de bootstrap e provisionamento do **Vitalia SPEC Kit** em novas estações de trabalho e ambientes controlados (como containers, WSL2 e ambientes com sandboxes de segurança), a instalação apresentava lacunas críticas de transparência e estabilidade:
1. **Opacidade e Silêncio Excessivo:** O comando de instalação de dependências operava em silêncio absoluto (`pip install --quiet >/dev/null 2>&1`), gerando pausas de 20 a 40 segundos sem indicador de atividade, levando o usuário a supor que o processo travou.
2. **Degradação Silenciosa do Isolamento (`--system-site-packages`):** Quando a instalação isolada falhava, o script destruía o ambiente virtual e recorria silenciosamente a `python3 -m venv --system-site-packages`. Se o sistema global da máquina não possuísse as bibliotecas exigidas (`pyyaml`, `jinja2`, `jsonschema`, `pytest`), o kit quebrava em cascata nos primeiros comandos SDD.
3. **Ausência de Pre-Flight de Permissões de Escrita:** O instalador tentava criar diretórios em `${TARGET_KIT_DIR}` e `${HOME}/.local/bin` sem testar previamente se o usuário possuía permissões de escrita, abortando com erros não-tratados (`mkdir: Read-only file system`) após iniciar operações parciais.
4. **Verificação Semântica Rasa:** A presença do Python era checada apenas com `command -v python3`, sem validar se a versão atendia ao requisito semântico real de Python `>= 3.10`.
5. **Falta de Destaque no Recarregamento do Shell:** Após a injeção do `$PATH` em `~/.bashrc` e `~/.zshrc`, o processo não destacava que a sessão ativa do terminal precisava ser recarregada (`source ~/.bashrc`) para que o comando `vitalia-install-project` fosse reconhecido.

### 1.2 Declaração de Impacto ao Usuário e Validação Pré-Spec (Princípio P02)
- **Impacto ao Desenvolvedor (DX):** Transforma um instalador opaco em um assistente transparente, com feedback visual a cada etapa e mensagens de erro prescritivas com comandos de solução prontos para copiar e colar.
- **Isolamento e Segurança (P11):** Garante que o kit seja executado estritamente sobre dependências isoladas, sem poluição nem interferência de pacotes legados do sistema operacional hospedeiro.
- **Didática e Automação (P10):** Toda falha de ambiente expõe a causa raiz de forma didática e não requer suporte manual ad-hoc.
- **Rastreabilidade e Observabilidade (P15):** Logs completos de ferramentas de terceiros são direcionados a `/tmp/vitalia-bootstrap.log`, mantendo a tela limpa sem perder capacidade forense.

---

## 2. Requisitos Funcionais

### FR-001: Módulo Compartilhado de Pre-Flight Check (`preflight.sh`)
O sistema **MUST** fornecer uma biblioteca modular em `source/bin/lib/preflight.sh` capaz de ser executada tanto antes da instalação global (`kit-bootstrap.sh`) quanto durante a ativação de projetos (`install-project`):
- **FR-001.1 (Python Semântico):** **MUST** validar deterministicamente se a versão do `python3` no PATH é superior ou igual a `3.10`. Caso inferior ou ausente, **MUST** abortar com código de saída $\neq 0$ e mensagem orientando a versão necessária.
- **FR-001.2 (Módulo `venv` Executável):** **MUST** testar a criação de um ambiente virtual temporário para comprovar a presença de `python3-venv` e `ensurepip`. Se falhar, **MUST** abortar com instrução prescritiva de instalação para a distribuição em uso (ex: `sudo apt install python3-venv`).
- **FR-001.3 (Permissão Efetiva de Escrita):** **MUST** testar a capacidade real de escrita nos caminhos de destino antes de qualquer modificação em disco (para o bootstrap: diretório do kit e `${HOME}/.local/bin`; para o projeto: raiz do projeto e diretório `.agents/skills/`). Caso o diretório de destino ainda não exista no sistema de arquivos, o pre-flight **MUST** inspecionar recursivamente o primeiro diretório ancestral existente (ex: `${HOME}`) testando a criação e remoção imediata de um arquivo temporário de probe (`touch probe && rm probe` / `mktemp`). Caso sem permissão de escrita, **MUST** abortar imediatamente com código de saída 1 e mensagem prescritiva sem criar pastas órfãs residuais.
- **FR-001.4 (Integridade do Git):** **MUST** validar a presença do executável `git` no PATH e, caso URLs remotas sejam fornecidas para memória de sessão ou dados, validar previamente a sintaxe e a acessibilidade da URL antes de iniciar o provisionamento.

### FR-002: Inviolabilidade do `.venv` Puro (Purga de `--system-site-packages`)
O provisionamento do ambiente virtual do kit **MUST**:
- Criar o ambiente virtual em `${VITALIA_KIT_DIR}/.venv` exclusivamente de forma isolada.
- **MUST NOT** utilizar a flag `--system-site-packages` em nenhuma hipótese ou fallback.
- Se o `pip install` falhar durante a instalação das dependências de `requirements.txt`:
  - O instalador **MUST** interromper a execução com código de saída $\neq 0$.
  - O instalador **MUST** registrar o erro detalhado em `/tmp/vitalia-bootstrap-${UID:-$(id -u)}.log` (com fallback seguro via `mktemp`).
  - O instalador **MUST** imprimir no console as últimas 15 linhas do log de erro e apresentar mensagem prescritiva alertando sobre possíveis restrições de conectividade de rede, proxy corporativo ou permissões.

### FR-003: Observabilidade Passo a Passo e Redirecionamento de Logs
Durante todo o ciclo de bootstrap e instalação:
- O instalador **MUST** exibir o status visual em tempo real para cada macro-etapa utilizando indicadores padronizados (`⏳` em progresso, `✅` concluído com sucesso, `❌` falha impeditiva, `⚠️` aviso não-bloqueante).
- As saídas detalhadas de ferramentas externas (`pip`, comandos de compilação) **MUST** ser redirecionadas para arquivos de log isolados por usuário em `/tmp/vitalia-bootstrap-${UID:-$(id -u)}.log` e `/tmp/vitalia-install-${UID:-$(id -u)}.log` (com fallback seguro via `mktemp` prevenindo colisões multi-usuário em `/tmp`).
- O instalador **MUST** suportar a flag `-v` / `--verbose` para permitir streaming direto de stdout/stderr quando invocado em pipelines de integração contínua (CI) ou sessões de depuração profunda.

### FR-004: Orientação Ativa de Ambiente e $PATH no Shell
Ao concluir o bootstrap com sucesso:
- O instalador **MUST** realizar a injeção idempotente em `~/.bashrc` e `~/.zshrc`.
- O instalador **MUST** detectar dinamicamente o shell ativo (inspecionando `$SHELL`, `$ZSH_VERSION` ou `$BASH_VERSION`) e imprimir um banner final de destaque visual recomendando o comando exato de recarregamento para o shell em uso (ex: `source ~/.zshrc` caso Zsh, ou `source ~/.bashrc` caso Bash), com a alternativa secundária documentada.

### FR-005: Integração no Ativador de Projetos (`install-project`)
O ativador de projetos hospedeiros **MUST**:
- Importar e invocar as validações pertinentes de `preflight.sh` antes de criar diretórios em `.vitalia/` ou alterar arquivos do projeto.
- Informar de forma clara o status da detecção e clonagem dos repositórios remotos de sessão e dados (indicando se operou via `git clone --depth=1` ou inicialização local `git init`).

---

## 3. Critérios de Sucesso Mensuráveis (SC-xxx)

- **SC-001 (Interceptação Precoce de Falhas):** 100% das falhas de ambiente (Python < 3.10, falta de `python3-venv` e ausência de permissão de escrita) são interceptadas no Passo 0 em tempo inferior a 2 segundos, com código de saída $\neq 0$ e zero mutação residual no sistema de arquivos.
- **SC-002 (Pureza Absoluta de Runtime):** Zero referências a `--system-site-packages` no código-fonte de scripts shell ou suíte de testes do kit.
- **SC-003 (Rastreabilidade e Limpeza de Saída):** Em caso de falha de download no `pip`, o usuário recebe no console o caminho exato do log gerado (`/tmp/vitalia-bootstrap.log`) e as linhas terminais do erro sem truncamento.
- **SC-004 (Feedback Contínuo de DX):** Nenhuma etapa síncrona do instalador permanece mais de 1 segundo sem emissão de indicador visual de progresso ativo no terminal.

---

## 4. User Scenarios & Acceptance Criteria (Gherkin)

### Cenário 1: Tentativa de instalação em diretório sem permissão de escrita (Falha Precoce)
```gherkin
Given que o usuário executa kit-bootstrap.sh especificando um diretório de destino somente-leitura ou sem privilégio
When o pre-flight check executa a validação de permissões no Passo 0
Then o script aborta imediatamente com código de saída 1
And emite a mensagem de erro: "❌ Erro: sem permissão de escrita no diretório alvo"
And nenhum diretório ou arquivo temporário é deixado no destino
```

### Cenário 2: Falha de rede durante a instalação de dependências no pip (Isolamento Inviolável)
```gherkin
Given que o ambiente virtual isolado foi criado com sucesso
When o comando pip install falha por indisponibilidade de rede ou pacote inexistente
Then o instalador interrompe a execução com código de saída 1
And não tenta recriar o ambiente virtual com a flag --system-site-packages
And exibe no terminal as últimas linhas de erro e o caminho "/tmp/vitalia-bootstrap.log"
```

### Cenário 3: Bootstrap bem-sucedido com orientação visual de shell
```gherkin
Given que todos os pré-requisitos (Python >= 3.10, venv, escrita) foram aprovados
When kit-bootstrap.sh conclui a cópia dos artefatos e a injeção nos arquivos rc do shell
Then o shim "~/.local/bin/vitalia-install-project" é criado e possui permissão de execução
And o instalador imprime o banner instruindo o recarregamento com "source ~/.bashrc" ou "source ~/.zshrc"
And o comando "vitalia-install-project --help" é executável com sucesso
```

---

## 5. Suposições Verificadas (Grounding Temporal — P03)

| Dependência / Tecnologia | Fonte Canônica | URL Validada (HTTP 200) | Status | Data de Verificação |
|---|---|---|---|---|
| Python `venv` nativo | Python 3 Documentation | https://docs.python.org/3/library/venv.html | ACTIVE | 10-11-2026 |
| Tratamento defensivo Bash | GNU Bash Reference Manual | https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html | ACTIVE | 10-11-2026 |
| XDG Base Directory Specification | FreeDesktop XDG Specs | https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html | ACTIVE | 10-11-2026 |

---

## 6. Comportamentos Existentes a Preservar & Defeitos a Reproduzir

### Comportamentos Existentes a Preservar
- Criação e integridade de todos os diretórios instalados (`bin/`, `extensions/`, `profiles/`, `src/`, `templates/`, `integrations/`, `AGENTS.md`).
- Shim executável funcional em `~/.local/bin/vitalia-install-project` exportando `VITALIA_KIT_DIR`.
- Idempotência de injeção em `~/.bashrc` e `~/.zshrc`.
- Suporte a `--target-dir`, `--non-interactive` e variável `VITALIA_KIT_DIR`.

### Defeitos a Reproduzir e Eliminar nos Testes
- **Defeito 1:** Criação parcial de diretórios antes de validar capacidade de escrita.
- **Defeito 2:** Fallback silencioso para `--system-site-packages` mascarando dependências faltantes.
- **Defeito 3:** Falta de indicador de atividade e ausência de log estruturado durante o provisionamento do `pip`.

