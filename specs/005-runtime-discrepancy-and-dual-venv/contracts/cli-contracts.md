<!-- cli-contracts.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 09:58(GMT-04:00) -->
> **cli-contracts.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 09:58(GMT-04:00)**

# Contratos de API Interna e CLI: Spec 005 — Dual-Runtime e Inviolabilidade do Runner

---

## 1. Contrato de Funções Públicas: `source/src/kit_env_bootstrap.py`

### 1.1 `find_project_python(project_root: Optional[Path] = None) -> Tuple[bool, Optional[str], str]`
- **Entrada**: Diretório raiz do projeto (`Path` ou `None` para resolução automática via `find_project_root()`).
- **Comportamento**:
  1. Avalia `$VIRTUAL_ENV` no ambiente do processo.
  2. Avalia `PROJECT_VENV_PATH` no `.env` do projeto (ancorando caminhos relativos em `project_root`).
  3. Varre pastas canônicas locais (`.venv`, `venv`, `env`, `.env_py`).
  4. Localiza binário executável (`bin/python3`, `bin/python`, `Scripts/python.exe`).
- **Retorno**: `(has_venv: bool, python_bin: Optional[str], source_detected: str)`
  - `source_detected` assume um dos valores: `"shell_env"`, `"dotenv_config"`, `"canonical_folder"`, `"not_found"`.

### 1.2 `resolve_kit_python(kit_dir: Optional[Path] = None) -> Path`
- **Entrada**: Diretório base do kit ou `None` (resolvido via `resolve_kit_dir()`).
- **Comportamento**: Retorna o caminho do interpretador Python isolado do kit (`.venv/bin/python3` em POSIX; `.venv/Scripts/python.exe` em Windows).
- **Retorno**: Instância `Path` do executável binário do kit.

### 1.3 `check_environment_health(project_root: Path) -> Dict[str, Any]`
- **Entrada**: Diretório raiz do projeto.
- **Estrutura de Retorno (JSON)**:
  ```json
  {
    "status": "HEALTHY",
    "kit_runtime": {
      "kit_dir": "/caminho/kit",
      "python_bin": "/caminho/kit/.venv/bin/python3",
      "status": "HEALTHY"
    },
    "project_runtime": {
      "project_root": "/caminho/projeto",
      "has_venv": true,
      "python_bin": "/caminho/projeto/.venv/bin/python3",
      "source_detected": "canonical_folder"
    },
    "has_env": true,
    "issues": []
  }
  ```
- **Invariante**: O `status` global reporta `"HEALTHY"` apenas se `kit_runtime.status == "HEALTHY"`. A ausência de ambiente virtual no projeto hospedeiro é informativa (`has_venv: false`), não rebaixando o status do kit para `"DEGRADED"`.

---

## 2. Contrato de Substituição e Execução: `source/src/vitalia_hook_runner.py`

### 2.1 Mapeamento de Placeholders em `resolve_placeholders(cmd_template: str, cwd: str, kit_dir: str) -> str`
| Placeholder | Mapeamento / Valor Resolvido | Exemplo |
| :--- | :--- | :--- |
| `{{cwd}}` | Diretório de trabalho atual (`str(cwd)`) | `/home/andre/projetos/meu-app` |
| `{{VITALIA_KIT_DIR}}` | Diretório raiz do kit instalado (`str(kit_dir)`) | `/home/andre/.vitalia-spec-kit` |
| `{{KIT_PYTHON}}` | Binário do interpretador do kit (`resolve_kit_python(kit_dir)`) | `/home/andre/.vitalia-spec-kit/.venv/bin/python3` |
| `{{PROJECT_PYTHON}}` | Binário do interpretador do projeto local com fallback no kit | `/caminho/projeto/.venv/bin/python3` ou `${KIT_PYTHON}` |
| `{{FEATURE_DIR}}` | Diretório da feature ativa lido de `.vitalia/feature.json` | `specs/005-runtime-discrepancy-and-dual-venv` |

### 2.2 Auto-Substituição Defensiva de Runtime
- Antes de invocar `subprocess.run(cmd, shell=True, env=env_copia)`:
  - Se `cmd` iniciar por `python3 ` ou `python `:
    - Inspeciona o alvo do script (primeiro argumento terminando em `.py`).
    - Se o arquivo pertencer a `${VITALIA_KIT_DIR}` (ex: `src/hooks/scan_environment.py`), reescreve o prefixo `python3` para `sys.executable`.
    - Se o arquivo pertencer ao projeto hospedeiro (fora de `${VITALIA_KIT_DIR}`), despacha utilizando `{{PROJECT_PYTHON}}`.

---

## 3. Contrato de Variáveis de Ambiente no Processo Filho

O `vitalia_hook_runner.py` garante a exportação das seguintes variáveis no ambiente `env_copia` entregue a cada hook:
- `VITALIA_KIT_DIR`: Caminho absoluto do kit.
- `VITALIA_KIT_PYTHON`: Caminho absoluto do interpretador Python do kit.
- `VITALIA_PROJECT_PYTHON`: Caminho absoluto do interpretador Python do projeto (ou do kit em caso de fallback).

