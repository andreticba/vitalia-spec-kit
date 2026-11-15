<!-- spec.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 11:35(GMT-04:00) -->
> **spec.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 11:35(GMT-04:00)**

# Especificação Funcional — Spec 007: [BUGFIX] Correção do CLI Faxineiro, Menu Interativo de Contexto e Indicador de Saúde da Sessão

- **Data:** 15-11-2026
- **Versão:** 0.0.1
- **Autor/Agente:** Vitalia SPEC Kit Architect & Requirements Engineer
- **Feature:** `specs/007-fix-context-cleanup-cli-and-session-health`
- **Natureza:** `[BUGFIX]` (Bug Reproduction First sob Matriz P05)
- **Status:** DRAFT (Submetido à Validação e Preparação para Auditoria)
- **Fontes Canônicas Obrigatórias:**
  - [`specs/007-fix-context-cleanup-cli-and-session-health/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/007-fix-context-cleanup-cli-and-session-health/research-brainstorming.md)
  - [`specs/007-fix-context-cleanup-cli-and-session-health/regencia-architect-plano-turno.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/007-fix-context-cleanup-cli-and-session-health/regencia-architect-plano-turno.md)
  - [`specs/003-modular-runtime-and-sensor-suite/relatorio_contratos_sdd_e_faxineiro.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/003-modular-runtime-and-sensor-suite/relatorio_contratos_sdd_e_faxineiro.md) (Seção 3)
  - [`docs/CONTRATOS_WORKFLOWS_SDD.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/CONTRATOS_WORKFLOWS_SDD.md)
  - [`docs/MEMORANDO DE ARQUITETURA.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/MEMORANDO%20DE%20ARQUITETURA.md)

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

### 1.1 Declaração do Problema (Root Cause Analysis — BUGFIX)
Durante a Spec 003, o relatório contratual (`relatorio_contratos_sdd_e_faxineiro.md`, Seção 3) estabeleceu a arquitetura do faxineiro autônomo `vitalia_tmp_cleanup.py`. Contudo, a entrega foi realizada com um stub incompleto:
1. **Omissão do Motor Temporal:** O utilitário atual varre arquivos `.json` de forma plana sem agrupar por data civil (`DD-MM-YYYY GMT-04:00`).
2. **Ausência de Preservação da Sessão Ativa:** O script não identifica a data de hoje, expondo os envelopes da sessão corrente do desenvolvedor ao risco de deleção acidental.
3. **Ausência do Menu Interativo `[a/d/n/t]` e Parser Granular:** O código atual implementa apenas um prompt binário `[s/N]`, impossibilitando a seleção por datas específicas (`[d]`) com intervalos (`1-3`) ou listas (`1,2`).
4. **Invisibilidade Operacional no `session-start`:** O desenvolvedor não recebe qualquer indicação de saúde ou acúmulo de disco no início da sessão (`/vitalia-session-start`), provocando o acúmulo silencioso de dezenas de megabytes em `.vitalia/memory/data_storage/context/<machine_id>/`.

### 1.2 Declaração de Impacto e Princípios Constitucionais (P00, P01, P02, P04, P05, P10, P11, P16)
- **Bem-estar e Integridade do Desenvolvedor (P00, P02):** Elimina a frustração de acúmulo de arquivos órfãos e previne a perda de contexto ativo da sessão de hoje.
- **Inviolabilidade do SDD e Falsificação (P01, P05):** Correção formal enquadrada em `[TEST:BUGFIX]`, com reprodução obrigatória da falha no código legado antes da correção.
- **Timestamp e Fuso Horário (P04):** Todas as datas exibidas e analisadas operam no fuso imutável `America/Cuiaba (GMT-04:00)`.
- **Engenharia Didática (P10):** CLI com saída padronizada, rica em feedback visual e com `--help` exemplar.
- **Isolamento Dual-Runtime (P11):** O faxineiro executa estritamente no runtime do kit (`{{KIT_PYTHON}}`).

---

## 2. Requisitos Funcionais (FR-xxx)

### FR-001: Motor de Agrupamento Temporal por Data Civil (America/Cuiaba GMT-04:00)
O utilitário `source/src/vitalia_tmp_cleanup.py` **MUST** agrupar deterministicamente todos os envelopes `.json` localizados em `<target_dir>/.vitalia/memory/data_storage/context/<machine_id>/`:
- **FR-001.1 (Extração de Timestamp):** O sistema **MUST** extrair a data a partir da convenção canônica do nome do arquivo (`<workflow>_<YYYYMMDD>_<HHMMSS>_<hash>.json`). Se o nome não corresponder ao padrão, **MUST** utilizar a data de modificação física (`mtime`) convertida para `America/Cuiaba (GMT-04:00)`.
- **FR-001.2 (Agrupamento Cronológico):** Os arquivos **MUST** ser agrupados por data civil (`DD-MM-YYYY`) em ordem cronológica crescente, computando a contagem de arquivos e a somatória do tamanho em KB/MB para cada data.

### FR-002: Preservação Mandatória da Sessão Ativa (`📅 hoje`)
O sistema **MUST** identificar a data atual no fuso `America/Cuiaba (GMT-04:00)` e aplicar salvaguarda inegociável:
- **FR-002.1 (Isolamento de Hoje):** Os envelopes correspondentes à data corrente **MUST** ser exibidos com o rótulo destacado:
  `📅 hoje (DD-MM-YYYY, sessão ativa — preservada automaticamente) (N arquivos — X KB)`.
- **FR-002.2 (Imunidade Padrão):** Os arquivos de hoje **MUST NOT** ser contabilizados no total elegível para limpeza padrão e **MUST NOT** ser deletados pelas opções `[a]` ou `--force`.

### FR-003: Menu Interativo Canônico `[a/d/n/t]` e Parser Granular de Índices
Quando invocado sem flags não-interativas em um terminal TTY, o utilitário **MUST** exibir o menu formatado:
- **FR-003.1 (Apresentação Visual Padronizada):** Exibir cabeçalho, a lista de datas indexadas `[1]`, `[2]`, ... `[N]`, o bloco da sessão ativa de hoje, o divisor visual e o total elegível:
  `Total elegível para limpeza (exceto hoje): M arquivos | Y KB`.
- **FR-003.2 (Opção `[a]` — Apagar Tudo Exceto Hoje):** Ao receber `a` ou `A`, remove 100% dos arquivos das datas anteriores, preservando integralmente os arquivos de hoje.
- **FR-003.3 (Opção `[d]` — Seleção Granular):** Ao receber `d` ou `D`, solicita `Datas para apagar (ex: 1,2 ou 1-3):`. O parser **MUST** aceitar índices isolados separados por vírgula (`1,3`), intervalos com hífen (`1-3`) e combinações (`1,3-5`). Apenas os arquivos dos dias selecionados são removidos.
- **FR-003.4 (Opção `[n]` — Cancelamento Padrão):** Ao receber `n`, `N` ou tecla Enter vazia, aborta a operação sem deletar nenhum arquivo físico.
- **FR-003.5 (Opção `[t]` — Purga Completa Deliberada):** Ao receber `t` ou `T`, solicita confirmação extra (`Tem certeza que deseja apagar TUDO, inclusive a sessão de hoje? [s/N]: `). Se confirmado com `s`, remove todos os arquivos.

### FR-004: Parâmetros de Linha de Comando e Automação Headless (P10)
O utilitário **MUST** fornecer interface de linha de comando completa para automação e testes:
- **FR-004.1 (`--dry-run`):** Executa todo o agrupamento e exibe o plano de remoção no terminal, garantindo que nenhum arquivo físico seja excluído (`assert temp_file.exists()`).
- **FR-004.2 (`--force`):** Modo não-interativo para scripts e CI que executa a limpeza correspondente à opção `[a]` (apaga dias anteriores e protege a sessão de hoje sem prompts).
- **FR-004.3 (`--purge-all`):** Modo não-interativo que executa a limpeza correspondente à opção `[t]` (remove todos os arquivos, inclusive hoje).
- **FR-004.4 (`--target-dir`):** Permite especificar o diretório raiz do projeto assistido (padrão: `.` / diretório corrente).
- **FR-004.5 (`--help` Didático P10):** Exibe ajuda estruturada detalhada com descrição, lista de opções e exemplos de uso prático.

### FR-005: Inspeção Ultraleve de Saúde em `scan_environment.py`
O hook de ambiente `source/src/hooks/scan_environment.py` **MUST** incorporar diagnóstico passivo de acúmulo de disco:
- **FR-005.1 (Execução Read-Only Ultraleve):** Inspecionar `.vitalia/memory/data_storage/context/` sem realizar qualquer mutação em disco e sem carregar o conteúdo dos arquivos JSON em memória.
- **FR-005.2 (Nó `context_cleanup` sob OpenAPI 3.0 Limpo):** O diagnóstico emitido no JSON de saída **MUST** estruturar o nó `context_cleanup` em estrita conformidade com o padrão **OpenAPI 3.0 Limpo** adotado pelo kit:
  1. **Tipos Primitivos Estritos:** Campos representados como tipos planos da OpenAPI 3.0 (`integer` e `boolean`).
  2. **Zero Meta-Campos:** Veto absoluto a `$schema`, `title` no nível de raiz e `additionalProperties: false`.
  3. **Array `required` Explícito:** Conter obrigatoriamente os 4 campos planos: `["total_files", "eligible_files", "eligible_bytes", "needs_cleanup"]`.
  4. **Instância Concreta de Saída:**
     ```json
     "context_cleanup": {
       "total_files": 42,
       "eligible_files": 41,
       "eligible_bytes": 3334520,
       "needs_cleanup": true
     }
     ```
  Onde `needs_cleanup` é computado deterministicamente como `true` se `eligible_files >= 10` ou `eligible_bytes >= 1048576` (1 MB).

### FR-006: Aviso Informativo Discreto no `/vitalia-session-start`
O workflow `source/extensions/session-start.toml` **MUST** ser atualizado para orientar o desenvolvedor sem sequestro atencional:
- **FR-006.1 (Exibição Condicional no Chat):** Se `needs_cleanup` for `true`, o passo de apresentação inclui uma linha amigável:
  `💡 Manutenção de Disco: Existem N envelopes de sessões anteriores (X MB) em .vitalia/memory/data_storage/context/. Execute 'vitalia-clean' para gerenciar a limpeza por datas.`
- **FR-006.2 (Zero Ruído no `guardian_json`):** Veto terminante à injeção de listas de arquivos ou matrizes interativas dentro do contexto cognitivo da LLM.

### FR-007: Exposição do Wrapper Executável `source/bin/vitalia-clean`
O instalador do kit **MUST** disponibilizar o utilitário na linha de comando:
- **FR-007.1 (Script Executável):** Criar `source/bin/vitalia-clean` com permissão `755`, configurado para despachar para `{{KIT_PYTHON}} {{VITALIA_KIT_DIR}}/src/vitalia_tmp_cleanup.py "$@"`.
- **FR-007.2 (Espelhamento no Bootstrap):** Garantir que `kit-bootstrap.sh` instale `vitalia-clean` em `${VITALIA_KIT_DIR}/bin/` e crie o link em `~/.local/bin/`.

---

## 3. Requisitos Não-Funcionais e Restrições de Engenharia

- **RN-001 (Performance de Varredura):** A inspeção em `scan_environment.py` deve processar até 1.000 envelopes de contexto em menos de 100 milissegundos.
- **RN-002 (Preservação de Dados):** Nenhuma operação de faxina pode tocar em diretórios fora de `.vitalia/memory/data_storage/context/`.
- **RN-003 (Idempotência):** Executar a limpeza sucessivas vezes consecutivas deve retornar código de saída 0 com mensagem de que nenhum arquivo necessita de remoção.
- **RN-004 (Dual-Runtime Compliant):** O script opera estritamente com a biblioteca padrão do Python (`pathlib`, `argparse`, `sys`, `re`, `datetime`), sem introduzir dependências externas.

---

## 4. User Scenarios e Acceptance Criteria (BDD Given/When/Then)

### Cenário 1: Limpeza Padrão Interativa com Proteção de Hoje (`[a]`)
- **Dado que** existem envelopes de 10-11-2026, 12-11-2026 e envelopes com a data de hoje em `.vitalia/memory/data_storage/context/`,
- **Quando** o desenvolvedor executa `vitalia_tmp_cleanup.py` e digita `a`,
- **Então** todos os arquivos de 10-11-2026 e 12-11-2026 são removidos,
- **E** todos os arquivos com a data de hoje permanecem intactos no disco.

### Cenário 2: Seleção Granular de Datas (`[d]` com Faixa)
- **Dado que** o menu lista as datas `[1] 08-11-2026`, `[2] 09-11-2026` e `[3] 10-11-2026`,
- **Quando** o usuário digita `d` e em seguida informa `1-2`,
- **Então** apenas os arquivos das datas 08-11-2026 e 09-11-2026 são removidos,
- **E** os arquivos da data 10-11-2026 e de hoje permanecem no disco.

### Cenário 3: Cancelamento Seguro por Omisso (`[n]`)
- **Dado que** o menu interativo está aguardando escolha,
- **Quando** o usuário pressiona Enter ou digita `n`,
- **Então** o utilitário encerra com status 0 informando cancelamento,
- **E** nenhum arquivo é deletado.

### Cenário 4: Simulação Não-Destrutiva (`--dry-run`)
- **Dado que** existem 40 arquivos acumulados,
- **Quando** o comando é executado com `--dry-run`,
- **Então** o utilitário exibe a relação detalhada por data,
- **E** 100% dos arquivos continuam existindo fisicamente.

### Cenário 5: Execução Headless em CI (`--force`)
- **Dado que** o script é invocado em ambiente não-interativo sem TTY,
- **Quando** passado o argumento `--force`,
- **Então** a limpeza executa sem requerer `stdin`, removendo os dias anteriores e preservando a sessão de hoje.

### Cenário 6: Diagnóstico de Saúde no `scan_environment.py`
- **Dado** um projeto com 30 arquivos elegíveis para limpeza totalizando 2 MB,
- **Quando** `scan_environment.py` é executado,
- **Então** o JSON gerado contém `"context_cleanup": {"eligible_files": 30, "needs_cleanup": true}`.

---

## 5. Success Criteria (Métricas Mensuráveis)

| Métrica | Meta | Método de Medição |
|---|---|---|
| **Preservação de 'Hoje'** | 100% dos arquivos de hoje protegidos em `[a]` e `--force` | Asserção de teste automatizado `assert today_file.exists()` |
| **Precisão de Seleção Granular** | 100% de conformidade com faixas `1-3` e listas `1,2` | Suíte de testes com simulação de `stdin` |
| **Sobrecarga no scan_environment** | < 100ms de acréscimo no tempo de boot | Medição com `time.perf_counter()` no teste |
| **Ruído Cognitivo no Guardian** | 0 tokens de listas de arquivos em `guardian_json` | Inspeção do payload JSON gerado pelo hook runner |
| **Cobertura de Testes P05** | 100% das opções interativas e flags testadas | `pytest tests/test_vitalia_tmp_cleanup.py` |

---

## 6. Comportamentos Existentes a Preservar & Defeitos a Reproduzir

### Defeitos a Reproduzir no Teste Vermelho (`[TEST:BUGFIX]`):
1. **Defeito 1:** Código atual em `source/src/vitalia_tmp_cleanup.py` deleta todos os arquivos indistintamente quando confirmado com `s`, destruindo a sessão ativa de hoje.
2. **Defeito 2:** Código atual não reconhece entradas `a`, `d`, `n` ou `t`.
3. **Defeito 3:** Script `scan_environment.py` não reporta o nó `context_cleanup`.

### Comportamentos a Preservar:
1. Suporte às opções existentes `--target-dir` e `--dry-run`.
2. Preservação do princípio de não-destrutividade por padrão.

---

## 7. Modelos de Dados e Contratos OpenAPI 3.0 Limpo

### 7.1 Schema OpenAPI 3.0 do Nó `context_cleanup`
Arquivo: `specs/007-fix-context-cleanup-cli-and-session-health/contracts/context_cleanup.schema.json`

```json
{
  "type": "object",
  "required": [
    "total_files",
    "eligible_files",
    "eligible_bytes",
    "needs_cleanup"
  ],
  "properties": {
    "total_files": {
      "type": "integer",
      "description": "Total absoluto de envelopes JSON encontrados no diretório de contexto"
    },
    "eligible_files": {
      "type": "integer",
      "description": "Total de envelopes pertencentes a datas civis anteriores elegíveis para faxina"
    },
    "eligible_bytes": {
      "type": "integer",
      "description": "Volume total em bytes ocupado pelos envelopes elegíveis para faxina"
    },
    "needs_cleanup": {
      "type": "boolean",
      "description": "Indicador se o acúmulo ultrapassou o limiar de manutenção (eligible_files >= 10 ou eligible_bytes >= 1048576)"
    }
  }
}
```

### 7.2 Garantia de Compatibilidade com o Envelope de Context Lifting
O schema mestre `source/src/schemas/context-lifting-envelope.schema.json` declara a propriedade `guardian_json.env_summary` como `type: "object"` sem `additionalProperties: false`. A introdução do nó `context_cleanup` respeita 100% da validação de integridade em tempo de compilação e execução via `jsonschema` e compiladores Google Gemini REST.
