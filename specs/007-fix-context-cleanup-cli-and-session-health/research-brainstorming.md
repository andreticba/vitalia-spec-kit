<!-- research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 10:35(GMT-04:00) -->
> **research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 10:35(GMT-04:00)**

# Síntese de Concepção — Spec 007: [BUGFIX] Correção do CLI Faxineiro e Indicador de Saúde da Sessão

---

## 1. Resumo Executivo e Justificativa do BUGFIX

Esta especificação formaliza a correção corretiva (**[BUGFIX]**) do utilitário autônomo de faxina e manutenção de contextos transitórios (`source/src/vitalia_tmp_cleanup.py`).

Na entrega da Spec 003, o script foi introduzido como um stub minimalista contendo apenas um prompt binário plano (`[s/N]`), omitindo a totalidade dos requisitos contratuais definidos na **Seção 3 de `specs/003-modular-runtime-and-sensor-suite/relatorio_contratos_sdd_e_faxineiro.md`**. Além disso, a ferramenta permaneceu invisível para o desenvolvedor durante o ciclo diário de sessões (`/vitalia-session-start`), acumulando dezenas de megabytes de payloads JSON antigos sem aviso ou mecanismo de curadoria.

### Decisões Acordadas (Consenso HITL)
1. **Natureza Estrita de [BUGFIX]:** A feature não introduz especificação arbitrária nova, mas resgata, corrige e implementa na íntegra a especificação formal preexistente da Seção 3 do relatório contratual da Spec 003.
2. **Motor de Agrupamento Temporal por Data:** Agrupar envelopes transitórios de `.vitalia/memory/data_storage/context/<machine_id>/` por data (`DD-MM-YYYY GMT-04:00`), extraindo o timestamp diretamente da convenção de nomenclatura `<workflow>_<YYYYMMDD>_<HHMMSS>_<hash>.json` com fallback para `mtime`.
3. **Preservação Automática da Sessão Ativa (`📅 hoje`):** Os arquivos pertencentes à data corrente (`America/Cuiaba GMT-04:00`) são obrigatoriamente preservados por padrão, evitando a deleção acidental de envelopes do turno de trabalho ativo.
4. **Menu Interativo Canônico `[a/d/n/t]` com Seleção Granular:**
   - `[a]`: Apagar tudo (exceto hoje) — comportamento padrão não-destrutivo.
   - `[d]`: Selecionar datas específicas para apagar, com suporte a índices e faixas (ex: `1,2` ou `1-3`).
   - `[n]`: Não apagar nada (cancelar / Enter padrão).
   - `[t]`: Apagar tudo (inclusive hoje) — purga total deliberada.
5. **Automação Não-Interativa e Conformidade Didática (P10):**
   - Suporte estrito a flags CLI: `--dry-run` (simulação segura), `--force` (não-interativo, comportamento de `[a]`), `--purge-all` (não-interativo, comportamento de `[t]`), `--target-dir` e `--help` didático com exemplos práticos (P10).
6. **Integração Não-Invasiva de Saúde no `/vitalia-session-start`:**
   - Adição de inspeção ultraleve em `scan_environment.py` reportando o total de arquivos e volume de dias anteriores acumulados.
   - Exibição de dica informativa amigável no passo de apresentação ao usuário, sem poluir o `guardian_json` nem sequestrar a atenção cognitiva da LLM (*lost-in-the-middle*).
7. **Exposição de Shim Executável:**
   - Criação do wrapper/shim `source/bin/vitalia-clean` instalado em `${VITALIA_KIT_DIR}/bin/` para uso direto no terminal pelo desenvolvedor.

---

## 2. Especificação Canônica Herdada (Seção 3 Integral de `relatorio_contratos_sdd_e_faxineiro.md`)

Abaixo é reproduzida integralmente a Seção 3 do relatório contratual formal da Spec 003, que serve como **especificação de verdade e critério de aceite mandatório** para esta spec corretiva:

## 3. Especificação do Novo Faxineiro de Contexto (`vitalia_tmp_cleanup.py`)

### 3.1. Requisitos e Diagnóstico
- **Localização dos Envelopes no Kit Novo:**  
  `.vitalia/memory/data_storage/context/<machine_id>/*`
- **Problema de Apagar Indiscriminadamente:**  
  O desenvolvedor precisa ter acesso ao histórico de envelopes de sessões anteriores para debugar prompts ou auditar decisões. A limpeza nunca pode ser automática e silenciosa.

### 3.2. Comportamento Interativo e Terminal CLI
O utilitário será implementado em `source/src/maintenance/vitalia_tmp_cleanup.py` e disponibilizado via CLI (`vitalia-tmp-cleanup`) ou acionado pelo `session-start`.

#### Exemplo Visual da Saída no Terminal / Chat:

```text
[vitalia_tmp_cleanup] Arquivos por data em `.vitalia/memory/data_storage/context/`:

  📅 [1] 25-08-2026 (12 arquivos — 48 KB):
      session-start_20260825_112872_a1b2.json, brainstorming_20260825_113045_c3d4.json, ...

  📅 [2] 26-08-2026 (8 arquivos — 32 KB):
      spec-plan_20260826_091520_e5f6.json, spec-tasks_20260826_094012_g7h8.json, ...

  📅 [3] 27-08-2026 (6 arquivos — 24 KB):
      spec-implement_20260827_142010_i9j0.json, judge_20260827_153040_k1l2.json, ...

  📅 [4] 28-08-2026 (10 arquivos — 87 KB):
      brainstorming_20260828_180012_m3n4.json, session-end_20260828_191020_o5p6.json, ...

  📅 hoje (29-08-2026, sessão ativa — preservada automaticamente)

  ──────────────────────────────────────────────────────────────────────────
  Total elegível para limpeza (exceto hoje): 36 arquivos | 191 KB

  O que deseja fazer?
  [a] Apagar tudo (exceto hoje)
  [d] Selecionar datas para apagar
  [n] Não apagar nada (padrão)
  [t] Apagar tudo (inclusive hoje)
  Escolha [a/d/n/t]:
```

#### Comportamento da Opção `[d]` (Seleção Granular por Índices):
Ao escolher `d`, o sistema solicita os índices:
```text
  Datas para apagar (ex: 1,2,3 ou 1-3): 1,2
  [vitalia_tmp_cleanup] 20 arquivos das datas 25-08-2026 e 26-08-2026 movidos para a lixeira/expurgo (80 KB liberados).
```

### 3.3. Integração com `/vitalia-session-start` (Zero Ruído no Contexto)
Para não poluir o prompt do LLM (evitando o erro do kit legado):
1. O hook de `session-start` verifica rapidamente se existem arquivos de datas anteriores em `.vitalia/memory/data_storage/context/<machine_id>/`.
2. Se **não houver** arquivos antigos, o hook não emite nada.
3. Se **houver** arquivos de datas anteriores acumulados, o resumo não é injetado como um payload JSON pesado no prompt, mas exibido amigavelmente no chat no passo de apresentação:
   ```markdown
   💡 **Manutenção de Disco:** Existem 36 envelopes de sessões anteriores (191 KB) em `.vitalia/memory/data_storage/context/`.
   Para gerenciar a limpeza por datas, execute no terminal:
   `python3 {{VITALIA_KIT_DIR}}/src/maintenance/vitalia_tmp_cleanup.py`
   ```
4. Se o usuário quiser acionar de dentro do chat, o comando de manutenção pode ser disparado interativamente com `ask_question`.

---

---

## 3. Engenharia Reversa Funcional em 3 Camadas

Para garantir que a correção do faxineiro seja cirúrgica e preserve 100% da integridade da base de código:

### Camada 1: Intenção de Negócio Pura (O que preservar e corrigir)
- Higiene do disco no repositório de dados (`.vitalia/memory/data_storage/context/<machine_id>/`), evitando acúmulo descontrolado de milhares de arquivos JSON ao longo de semanas de uso.
- Capacidade de auditoria forense: o desenvolvedor pode preservar seletivamente dias específicos para investigar comportamentos anteriores de prompts e envelopes.
- Transparência operacional: o usuário sabe exatamente quantos arquivos e megabytes estão ocupados antes de confirmar qualquer remoção.

### Camada 2: Purga de Infraestrutura e Defeitos do Código Atual (O que remover)
- Remoção do prompt binário simplista `input("Deseja remover N arquivos? [s/N]")`.
- Eliminação do comportamento indiscriminado que apaga envelopes de hoje e de dias passados no mesmo pacote.
- Remoção de qualquer resquício de injeção de matrizes pesadas dentro de `guardian_json`.

### Camada 3: Contrato do Consumidor e Interfaces da IDE
- A interface de linha de comando deve rodar perfeitamente tanto no terminal interativo do desenvolvedor quanto de forma headless em scripts e CI (via flags `--force`, `--dry-run` e `--purge-all`).
- O resumo em `session-start` deve ser uma única linha informativa concisa, respeitando o princípio de Progressive Disclosure.
- Execução sob `{KIT_PYTHON}` isolado no runtime do kit.

---

## 4. Classificação na Matriz de Testes P05 & Cenários de Falsificação

Como se trata de uma spec **majoritariamente de BUGFIX**, a estratégia de testes é classificada na categoria:

### Modalidade: `[TEST:BUGFIX]` (Bug Reproduction First)

#### Cenário de Falsificação Comportamental (FMEA):
1. **Falsificação do Agrupamento Temporal e Proteção de 'Hoje':**
   - *Teste:* Criar em diretório temporário arquivos com timestamps de 3 dias atrás, 1 dia atrás e hoje. Executar o CLI com opção `[a]` (apagar exceto hoje).
   - *Falha no código atual:* O código atual não tem opção `[a]`; ele pede confirmação binária e apaga TODOS os arquivos incluindo os de hoje, violando a regra de preservação da sessão ativa.
2. **Falsificação da Seleção Granular `[d]`:**
   - *Teste:* Simular `stdin` escolhendo `d` e informando `1,2`.
   - *Falha no código atual:* Opção `d` inexiste no código atual; a entrada é rejeitada ou tratada como cancelamento.
3. **Falsificação do Cancelamento Padrão `[n]`:**
   - *Teste:* Pressionar Enter ou digitar `n`. O teste falha se qualquer arquivo for deletado do disco.
4. **Falsificação da Purga Total `[t]` / `--purge-all`:**
   - *Teste:* Executar com `t` ou flag `--purge-all`. O teste falha se qualquer arquivo restar no diretório de contextos.
5. **Falsificação da Observabilidade do `session-start`:**
   - *Teste:* Executar `scan_environment.py` em projeto com envelopes de dias anteriores. O teste falha se o diagnóstico JSON não reportar as métricas estruturadas de envelopes transitórios elegíveis.

---

## 5. Rastro de Pesquisa e Grounding (P03)

| # | Afirmação / Tecnologia | Fonte Canônica | URL / Arquivo Validado (HTTP 200 / Local) | Status Temporal | Data |
|---|---|---|---|---|---|
| 1 | Contrato Original do Faxineiro | Spec 003 SDD Kit | `specs/003-modular-runtime-and-sensor-suite/relatorio_contratos_sdd_e_faxineiro.md` | Preservado | 15-11-2026 |
| 2 | Python `argparse` & Terminal Interativo | Python 3.10+ stdlib | `https://docs.python.org/3/library/argparse.html` | Ativo | 15-11-2026 |
| 3 | Convenção de Envelopes Context Lifting | Hook Runner Kit | `source/src/vitalia_hook_runner.py` (L150-165) | Ativo | 15-11-2026 |
| 4 | Fuso Imutável America/Cuiaba GMT-04:00 | Princípio P04 Constituição | `source/profiles/constitution.yaml` | Ativo | 15-11-2026 |

---

## 6. Handoff e Próximos Passos

Esta síntese conclui a etapa de concepção e alinhamento sob o comando `/vitalia-brainstorming`.
A especificação sequencial aprovada é:

📁 **`specs/007-fix-context-cleanup-cli-and-session-health/`**

**Próximo Passo:** Execute `/vitalia-route` para registrar formalmente o handoff determinístico e acionar o **Vitalia Architect** para a elaboração de `regencia-architect-plano-turno.md` e a partida oficial do SDD (`/vitalia-spec-specify`).
