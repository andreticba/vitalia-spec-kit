<!-- cli-contracts.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:30(GMT-04:00) -->
> **cli-contracts.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:30(GMT-04:00)**

# Contratos de CLI e Biblioteca: Spec 004 — Pre-Flight & Verbosidade

---

## 1. Contrato da Biblioteca `source/bin/lib/preflight.sh`

A biblioteca **MUST** residir em `source/bin/lib/preflight.sh` e fornecer as seguintes funções públicas com retorno semântico POSIX:

### 1.1 `check_python_version_semver [MIN_MAJOR] [MIN_MINOR]`
- **Entrada**: Inteiro maior (padrão `3`), Inteiro menor (padrão `10`).
- **Comportamento**: Invoca `python3` para checar `sys.version_info >= (MIN_MAJOR, MIN_MINOR)`.
- **Saída / Códigos de Retorno**:
  - `0`: Python disponível e versão `>= MIN_MAJOR.MIN_MINOR`.
  - `1`: Python indisponível ou versão `< MIN_MAJOR.MIN_MINOR`.
- **Stderr**: Emite mensagem prescritiva em caso de falha.

### 1.2 `check_venv_capability`
- **Entrada**: Nenhuma.
- **Comportamento**: Cria um virtualenv descartável em diretório temporário isolado via `python3 -m venv` e remove-o imediatamente.
- **Saída / Códigos de Retorno**:
  - `0`: Módulo `venv` funcional e habilitado.
  - `1`: Falha na criação do venv (ex: pacote `python3-venv` ausente).
- **Stderr**: Emite comando acionável para Debian/Ubuntu (`sudo apt update && sudo apt install -y python3-venv`).

### 1.3 `check_writable_target <PATH>`
- **Entrada**: Caminho de arquivo ou diretório de destino.
- **Comportamento**: Encontra o primeiro ancestral existente no filesystem e executa probe de criação/remoção de arquivo temporário.
- **Saída / Códigos de Retorno**:
  - `0`: Permissão de escrita garantida no caminho.
  - `1`: Sistema de arquivos somente-leitura ou permissão negada.
- **Stderr**: Mensagem indicando o caminho bloqueado e a natureza do erro.

### 1.4 `check_git_requirements [SESSION_REPO_URL] [DATA_REPO_URL]`
- **Entrada**: URLs opcionais de repositórios remotos Git.
- **Comportamento**: Valida presença de `git` no PATH; caso URLs sejam informadas, valida sintaxe básica sem travar.
- **Saída / Códigos de Retorno**:
  - `0`: Git disponível e URLs sintaticamente válidas.
  - `1`: Git não encontrado no PATH.

---

## 2. Contrato de CLI: `kit-bootstrap.sh`

```text
Uso: ./kit-bootstrap.sh [OPÇÕES]

Opções:
  --target-dir <PATH>   Diretório de instalação do kit (padrão: ~/.vitalia-spec-kit)
  --non-interactive     Executa sem prompts interativos (usa valores padrão)
  -v, --verbose         Habilita saída detalhada ao vivo de comandos externos (pip)
  -h, --help            Exibe esta mensagem de ajuda
```

---

## 3. Contrato de CLI: `install-project` / `vitalia-install-project`

```text
Uso: vitalia-install-project [OPÇÕES]

Opções:
  --session-repo <URL>  URL ou caminho do repositório Git de sessão (.vitalia/memory/session)
  --data-repo <URL>     URL ou caminho do repositório Git de dados (.vitalia/memory/data_storage)
  --non-interactive     Executa sem prompts interativos
  -v, --verbose         Habilita verbosidade estendida
  -h, --help            Exibe esta mensagem de ajuda
```

