<!-- research.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 09:58(GMT-04:00) -->
> **research.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 09:58(GMT-04:00)**

# Technical Research: Spec 005 — Runtime Discrepancy, Dual-Virtualenv and Runner Inviolability

---

## 1. Decisão: Resolução de `sys.executable` e Inviolabilidade de Subprocessos

- **Escolhido**: Uso de `sys.executable` para garantir a identidade do interpretador que executa o processo pai do kit, combinado com inspeção de caminho para auto-substituição de comandos:
  ```python
  def sanitize_kit_cmd(cmd: str, kit_dir: str) -> str:
      # Se o comando inicia com python3 e aponta para script dentro de kit_dir, substitui por sys.executable
      parts = cmd.strip().split()
      if len(parts) >= 2 and parts[0] in ("python3", "python"):
          target_script = Path(parts[1]).resolve()
          if str(target_script).startswith(str(Path(kit_dir).resolve())):
              return f"{sys.executable} " + " ".join(parts[1:])
      return cmd
  ```
- **Verificado em**: https://docs.python.org/3/library/sys.html#sys.executable em 11-11-2026
- **Justificativa**: `sys.executable` contém a string canônica do caminho absoluto para o executável binário do Python que iniciou o interpretador corrente. Quando o kit é invocado via `${VITALIA_KIT_DIR}/.venv/bin/python3`, `sys.executable` aponta diretamente para o interpretador virtual isolado com suas bibliotecas completas (`yaml, jinja2, jsonschema`), independentemente de como o `$PATH` do terminal esteja configurado.
- **Alternativas**:
  - Confiar em `subprocess.run("python3 ...", shell=True)`: rejeitado porque herda o `$PATH` global do shell hospedeiro e executa o Python do sistema ou do projeto local.
  - Ativar o virtualenv via `source ${VITALIA_KIT_DIR}/.venv/bin/activate`: rejeitado porque comandos de shell em subshells efêmeros não preservam ativação entre chamadas e dependem de scripts shell específicos (`activate` bash vs zsh vs fish).

---

## 2. Decisão: Algoritmo de Descoberta em 4 Níveis de `project_runtime`

- **Escolhido**: Resolução em cascata ordenada por explicitude:
  ```python
  def find_project_python(project_root: Path) -> Tuple[bool, Optional[str], str]:
      # 1. Shell ativo
      if "VIRTUAL_ENV" in os.environ:
          candidate = Path(os.environ["VIRTUAL_ENV"])
          py_bin = resolve_venv_binary(candidate)
          if py_bin: return True, str(py_bin), "shell_env"

      # 2. .env local (PROJECT_VENV_PATH)
      env_file = project_root / ".env"
      if env_file.exists():
          dotenv = load_dotenv_native(env_file)
          if "PROJECT_VENV_PATH" in dotenv:
              raw_p = dotenv["PROJECT_VENV_PATH"].strip()
              candidate = (project_root / raw_p).resolve() if not os.path.isabs(raw_p) else Path(raw_p).resolve()
              py_bin = resolve_venv_binary(candidate)
              if py_bin: return True, str(py_bin), "dotenv_config"

      # 3 e 4. Pastas canônicas e binário
      for vname in (".venv", "venv", "env", ".env_py"):
          candidate = project_root / vname
          py_bin = resolve_venv_binary(candidate)
          if py_bin: return True, str(py_bin), "canonical_folder"

      return False, None, "not_found"
  ```
- **Verificado em**: https://peps.python.org/pep-0405/ (PEP 405 — Python Virtual Environments) em 11-11-2026
- **Justificativa**: A PEP 405 estabelece a estrutura canônica de virtualenvs (`pyvenv.cfg`, pasta `bin/` ou `Scripts/`). Respeitar `$VIRTUAL_ENV` e `PROJECT_VENV_PATH` atende a desenvolvedores que utilizam gerenciadores modernos como Poetry, Pipenv, Hatch ou caminhos centralizados (`~/.cache/pypoetry/virtualenvs`), sem amarrar o projeto à pasta fixa `.venv`.
- **Alternativas**:
  - Checar apenas se `(project_root / ".venv").exists()`: rejeitado por ser excessivamente rígido e falhar em projetos com estruturas não-canônicas.
  - Executar comandos CLI como `poetry env info -p` no shell: rejeitado por adicionar acoplamento com CLIs de terceiros que podem não estar instaladas ou demorar segundos para responder.

---

## 3. Decisão: Resolução de Placeholders Semânticos `{{KIT_PYTHON}}` e `{{PROJECT_PYTHON}}`

- **Escolhido**: Mapeamento determinístico em `resolve_placeholders` no `vitalia_hook_runner.py`:
  ```python
  cmd = cmd.replace("{{KIT_PYTHON}}", str(kit_python_bin))
  cmd = cmd.replace("{{PROJECT_PYTHON}}", str(project_python_bin or kit_python_bin))
  ```
- **Verificado em**: https://docs.python.org/3/library/stdtypes.html#str.replace em 11-11-2026
- **Justificativa**: O uso de placeholders explícitos torna as definições dos 16 arquivos `.toml` auto-documentadas. Um comando que pertence ao ecossistema do kit declara `{{KIT_PYTHON}}`, enquanto um comando que deve rodar o código de negócio do cliente declara `{{PROJECT_PYTHON}}`. Se o projeto cliente ainda não tiver configurado seu ambiente virtual, o fallback transparente para `{{KIT_PYTHON}}` evita interrupções fatais desnecessárias.
- **Alternativas**:
  - Manipular o `$PATH` pré-pendendo `${VITALIA_KIT_DIR}/.venv/bin`: rejeitado porque mascararia qual interpretador está sendo invocado em cada comando e manteria comandos ambíguos `python3 ...`.

---

## 4. Decisão: Diretriz Constitucional Anti-Loop de Sandbox na IDE Antigravity

- **Escolhido**: Inclusão de regra expressa na Seção 8 do `AGENTS.md` e em `SKILL.md.template`:
  - Erro 127 (`No such file or directory`) para arquivos fora do workspace deve ser retentado com `BypassSandbox: true`.
  - **Veto Absoluto:** Proibição de disparar `./kit-bootstrap.sh` sem instrução direta do usuário.
- **Verificado em**: Antigravity Built-in Sandbox Guidelines (System Prompt & Execution Model) em 11-11-2026
- **Justificativa**: No modelo de execução segura de coding assistants, os comandos do terminal são restritos ao diretório de trabalho local. Como o kit é instalado globalmente em `${HOME}/.vitalia-spec-kit`, qualquer acesso inicial fora do sandbox é interceptado pelo kernel/sandbox com erro de arquivo inexistente. A instrução cognitiva direta no prompt do agente evita o falso reflexo de reinstalação.
- **Alternativas**:
  - Criar um symlink do `.venv` dentro do projeto (`.vitalia/venv_link`): rejeitado porque symlinks para destinos fora da raiz do sandbox continuam bloqueados pelo runtime de segurança do sandbox.

