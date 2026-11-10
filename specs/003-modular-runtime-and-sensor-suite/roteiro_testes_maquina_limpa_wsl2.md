<!-- roteiro_testes_maquina_limpa_wsl2.md | Vitalia SPEC Kit v0.0.1 | 09-11-2026 19:35(GMT-04:00) -->
> **roteiro_testes_maquina_limpa_wsl2.md | Vitalia SPEC Kit v0.0.1 | 09-11-2026 19:35(GMT-04:00)**

# Roteiro de Testes e Validação em Máquina Limpa (WSL2 / zsh)

Este roteiro fornece o passo a passo exato, comandos de terminal executáveis e critérios de aceite para a validação empírica do novo Vitalia SPEC Kit em uma máquina limpa executando **WSL2 com shell zsh**.

---

## 1. Pré-Requisitos do Ambiente Limpo

Antes de iniciar, certifique-se de que a máquina possui as ferramentas básicas do sistema:
```zsh
# 1. Verificar shell ativo
echo $SHELL # Deve retornar /bin/zsh ou /usr/bin/zsh

# 2. Verificar versão do Python (3.11+ obrigatório)
python3 --version

# 3. Garantir pacotes essenciais do sistema operacional
sudo apt update && sudo apt install -y python3-venv python3-pip git curl jq
```

---

## 2. Preparação do Diretório de Teste Isolado

Para não interferir em nenhuma instalação global existente (`~/.vitalia`), definiremos uma variável de ambiente dedicada para o kit em teste:

```zsh
# Definir diretório de instalação do kit novo para o teste
export VITALIA_TEST_KIT="$HOME/.vitalia-test-kit"
rm -rf "$VITALIA_TEST_KIT"

# Navegar até o repositório onde a pasta source/ reside
cd ~/projetos/assistidos/vitalia-spec-kit
```

---

## 3. Teste 1: Execução do Bootstrap do Kit a partir de `source/`

Executar o instalador átomo a átomo apontando para o diretório de teste:

```zsh
# Disparar o instalador de bootstrap
VITALIA_DIR="$VITALIA_TEST_KIT" bash source/bin/kit-bootstrap.sh
```

### ✅ Critérios de Aceite do Teste 1:
1. Retorno com código de saída `0` sem erros de subshell no zsh.
2. Virtualenv criado em `$VITALIA_TEST_KIT/.venv`.
3. Execução bem-sucedida do validador interno:
   ```zsh
   $VITALIA_TEST_KIT/.venv/bin/python3 -c "import yaml, jinja2, jsonschema; print('Ambiente virtual 100% íntegro!')"
   ```
4. Presença funcional de:
   - `$VITALIA_TEST_KIT/bin/install-project`
   - `$VITALIA_TEST_KIT/extensions/` (todos os 16 workflows `.toml`)
   - `$VITALIA_TEST_KIT/profiles/` (catálogos e lentes sem poda `gp_*.yaml`)
   - `$VITALIA_TEST_KIT/src/schemas/` (schemas OpenAPI 3.0 Limpos)

---

## 4. Teste 2: Instalação em um Projeto Hospedeiro Limpo (`install-project`)

Simular a ativação do kit em um novo projeto do desenvolvedor:

```zsh
# 1. Criar projeto hospedeiro limpo
export TEST_PROJECT="$HOME/test-workspace/calculadora-ponto"
rm -rf "$TEST_PROJECT" && mkdir -p "$TEST_PROJECT"
cd "$TEST_PROJECT" && git init

# 2. Executar o install-project do kit novo
VITALIA_KIT_DIR="$VITALIA_TEST_KIT" "$VITALIA_TEST_KIT/bin/install-project"
```

### ✅ Critérios de Aceite do Teste 2:
1. **Pureza de Diretórios da IDE Antigravity:**
   ```zsh
   # Deve listar APENAS subpastas de skills, ZERO arquivos ocultos ou .trash
   ls -la "$TEST_PROJECT/.agents/skills"
   # Validar que NÃO existem .trash nem .vitalia-manifest aqui dentro
   test ! -d "$TEST_PROJECT/.agents/skills/.trash" && echo "✅ Skills puras sem .trash"
   test ! -f "$TEST_PROJECT/.agents/skills/.vitalia-manifest" && echo "✅ Sem manifesto espúrio"
   ```
2. **Isolamento no `.gitignore` do Projeto:**
   ```zsh
   # Validar que .agents/ foi adicionado ao .gitignore do projeto hospedeiro
   grep -qF ".agents/" "$TEST_PROJECT/.gitignore" && echo "✅ .agents/ devidamente ignorado no Git"
   grep -qF ".vitalia/memory/" "$TEST_PROJECT/.gitignore" && echo "✅ .vitalia/memory/ ignorado no Git"
   ```
3. **Localização Correta dos Backups:**
   ```zsh
   # Validar que NÃO foi criada pasta .vitalia/backups na raiz
   test ! -d "$TEST_PROJECT/.vitalia/backups" && echo "✅ Raiz .vitalia/ livre de backups espúrios"
   ```

---

## 5. Teste 3: Teste do Novo Faxineiro de Contexto (`vitalia_tmp_cleanup.py`)

Simular a criação de envelopes de sessões anteriores e testar a limpeza agrupada por data:

```zsh
cd "$TEST_PROJECT"

# 1. Criar pasta de contexto e simular arquivos de datas anteriores
MACHINE_ID=$("$VITALIA_TEST_KIT/.venv/bin/python3" -c "import socket, hashlib; print(hashlib.sha256(socket.gethostname().lower().encode()).hexdigest()[:8])")
CONTEXT_DIR="$TEST_PROJECT/.vitalia/memory/data_storage/context/$MACHINE_ID"
mkdir -p "$CONTEXT_DIR"

# Criar arquivo simulado de ontem (2026-11-08) e de hoje (2026-11-09)
touch -d "2026-11-08 14:00:00" "$CONTEXT_DIR/session-start_20261108_140000_a1b2c3d4.json"
touch -d "2026-11-08 15:00:00" "$CONTEXT_DIR/brainstorming_20261108_150000_e5f6g7h8.json"
touch "$CONTEXT_DIR/session-start_20261109_080000_i9j0k1l2.json"

# 2. Executar o utilitário em modo interativo de terminal
"$VITALIA_TEST_KIT/.venv/bin/python3" "$VITALIA_TEST_KIT/src/maintenance/vitalia_tmp_cleanup.py"
```

### ✅ Critérios de Aceite do Teste 3:
1. O utilitário exibe a data de ontem agrupada (2 arquivos) e preserva a data de hoje como sessão ativa protegida.
2. Ao escolher a opção `d`, permite informar o índice da data e expurga apenas os arquivos da data selecionada.
3. Zero impacto em requisições de IA (nenhum arquivo de contexto antigo vaza para o prompt).

---

## 6. Teste 4: Execução da Suíte Completa de Testes (`pytest`)

Executar os testes automatizados garantindo conformidade contratual:

```zsh
cd ~/projetos/assistidos/vitalia-spec-kit

# Executar pytest no ambiente isolado
"$VITALIA_TEST_KIT/.venv/bin/pytest" -v tests/
```

### ✅ Critérios de Aceite do Teste 4:
1. `test_contracts_and_handoff.py`: 100% dos catálogos YAML e lentes `gp_*.yaml` passam na validação de schema.
2. `test_bootstrap_and_install.py`: Passa com 100% de sucesso validando o fluxo E2E no zsh.
3. Zero asserções de contagem fixa quebrando em novas adições dinâmicas.
4. **Validação Constitucional da Opção `--help` Didática:**
   100% dos scripts executáveis em `bin/`, `src/` e `src/tools/` respondem a `--help` com código `0`, contendo descrições e exemplos práticos de uso:
   ```zsh
   # Script de varredura automática de conformidade com a Constituição
   for s in "$VITALIA_TEST_KIT"/bin/* "$VITALIA_TEST_KIT"/src/*.py "$VITALIA_TEST_KIT"/src/tools/*.py; do
     [ -f "$s" ] || continue
     echo -n "Testando --help didático em $(basename $s)... "
     "$VITALIA_TEST_KIT/.venv/bin/python3" "$s" --help 2>&1 | grep -qi "exemplo" && echo "✅ OK" || echo "⚠️ Requer exemplos"
   done
   ```

---

## 7. Teste 5: Ciclo SDD Guiado por Especificação na IDE Antigravity

No projeto hospedeiro aberto na IDE Antigravity:

1. **`/vitalia-session-start`:**
   - Verifica semáforo LIVRE e recupera estado sem emitir ruído no contexto.
2. **`/vitalia-brainstorming`:**
   - Digitar: `"Quero criar um utilitário de cálculo de horas trabalhadas"`.
   - **Comportamento Esperado:**
     - O agente formula até 3 perguntas socráticas de negócio/CLT e **pausa (WAIT)**.
     - NÃO emite `research-brainstorming.md` até que você digite explicitamente: `"Aprovado, pode gerar a síntese"`.
     - Zero menções a Redis, Celery ou pastas `.trash`.
3. **`/vitalia-route`:**
   - Classifica o domínio e propõe direcionar para `/vitalia-architect`.
   - Dispara handoff determinístico após seu consentimento.
4. **`/vitalia-architect`:**
   - Lê `docs/adr/*` e os artefatos de spec.
   - Define a stack e contratos OpenAPI 3.0 Limpos.
   - Emite ADR formal se houver decisão estruturante e encaminha para `/vitalia-spec-specify`.
5. **`/vitalia-judge`:**
   - Executa a auditoria adversarial com Sanduíche Constitucional.
   - Emite a análise detalhada princípio por princípio.
   - Emite o veredito (`PASS`/`WARN`/`BLOCK`) **estritamente ao final das instruções** (Inverted CoT) e pausa para seu consentimento soberano (HITL).
6. **`/vitalia-session-end` & `/vitalia-session-consolidate`:**
   - Encerra e consolida executando o fluxo Git correto (commit local $\rightarrow$ pull rebase $\rightarrow$ consolidate $\rightarrow$ push).

---
<sub>Roteiro técnico salvo em `TEMP/` pronto para guiar os testes comportamentais na máquina limpa (WSL2/zsh).</sub>

