<!-- research.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 12:20(GMT-04:00) -->
> **research.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 12:20(GMT-04:00)**

# Technical Research: [BUGFIX] Faxineiro de Contexto CLI & Saúde de Sessão (Spec 007)

## 1. Visão Geral e Contexto de Pesquisa

Este documento consolida as decisões técnicas, grounding temporal (P03) e a Engenharia Reversa Funcional em 3 Camadas aplicados para a correção cirúrgica do CLI Faxineiro (`source/src/vitalia_tmp_cleanup.py`), adição da sonda ultraleve no sensor de ambiente (`source/src/hooks/scan_environment.py`), criação do executável shim (`source/bin/vitalia-clean`) e integração não-intrusiva no checklist de inicialização de sessão (`source/extensions/session-start.toml`).

---

## 2. Engenharia Reversa Funcional em 3 Camadas (P03 / P05)

### Camada 1: Intenção de Negócio Pura a Preservar
- Manter o diretório `.vitalia/memory/data_storage/context/<machine_id>/` organizado e sustentável.
- **Invariante Soberana:** A sessão do dia civil atual (`📅 hoje (DD-MM-YYYY, sessão ativa — preservada automaticamente)`) no fuso GMT-04:00 (America/Cuiaba) **JAMAIS** pode ser apagada por padrão ou por engano, prevenindo perda de contexto de trabalho em andamento.
- Oferecer controle granular ao operador: deletar anteriores (`[a]`), deletar datas específicas (`[d]`), cancelar com segurança (`[n]`), ou purga total sob confirmação afirmativa explícita (`[t]` com `[s/N]`).

### Camada 2: Infraestrutura Legada e Defeitos a Purgar
- **Defeito 1:** Código atual em `source/src/vitalia_tmp_cleanup.py` apaga indiscriminadamente sem segregar por data civil e sem preservar a data de hoje.
- **Defeito 2:** Ausência do menu interativo formatado conforme especificado na Seção 3 do Spec 003.
- **Defeito 3:** Ausência de flags não-interativas completas (`--dry-run`, `--force`, `--purge-all`, `--target-dir`).
- **Defeito 4:** Falta do binário executável `vitalia-clean` em `source/bin/`.
- **Defeito 5:** Falta da contagem ultraleve `context_cleanup` em `source/src/hooks/scan_environment.py` e aviso no `session-start.toml`.

### Camada 3: Contrato Estrito do Consumidor
- O sensor `scan_environment.py` emite nó `context_cleanup` estritamente conforme o padrão **OpenAPI 3.0 Limpo**:
  - `total_files` (integer >= 0)
  - `eligible_files` (integer >= 0)
  - `eligible_bytes` (integer >= 0)
  - `needs_cleanup` (boolean)
- Sem campos de metadados proibidos (`$schema`, root `title`, `additionalProperties: false`).
- CLI interativo consome stdin/stdout com fallback seguro caso stdin não seja um TTY (executando comportamento `--dry-run` ou cancelamento seguro).

---

## 3. Decisões Técnicas e Grounding

### Decisão 1: Extração e Agrupamento de Datas Civis por Timestamp GMT-04:00
- **Escolhido**: Regex para padrão `<workflow>_<YYYYMMDD>_<HHMMSS>_<hash>.json` com fallback para `os.stat().st_mtime` convertido para datetime com timezone `ZoneInfo("America/Cuiaba")` (ou `datetime.timezone(datetime.timedelta(hours=-4))`).
- **Verificado em**: Python Standard Library `datetime` & `re` (Python 3.10+) em 15-11-2026.
- **Justificativa**: Garante que arquivos gerados no mesmo dia civil em Cuiabá sejam agrupados de forma idêntica independentemente do relógio do sistema host estar em UTC ou outro fuso.
- **Alternativas**:
  - *Usar apenas st_mtime*: Rejeitado porque o nome do arquivo já carrega a estampa canônica gerada pelo Kit, sendo mais determinístico e resiliente a cópias/backups de arquivos.
  - *Usar dateutil*: Rejeitado por adicionar dependência externa desnecessária quando a biblioteca padrão do Python já atende nativamente.

### Decisão 2: Gramática do Parser de Seleção de Datas (`[d]`)
- **Escolhido**: Mini-parser combinando vírgulas e hífens (ex: `"1,3"` -> `[1, 3]`; `"2-4"` -> `[2, 3, 4]`; `"1, 3-5"` -> `[1, 3, 4, 5]`), com validação de limites `1 <= idx <= len(datas)`.
- **Verificado em**: Seção 3 de `specs/003-modular-runtime-and-sensor-suite/relatorio_contratos_sdd_e_faxineiro.md` em 15-11-2026.
- **Justificativa**: Proporciona máxima flexibilidade e conformidade literal com os contratos históricos de faxina do kit.
- **Alternativas**:
  - *Apenas seleção numérica única*: Rejeitado por obrigar o operador a executar o faxineiro múltiplas vezes para limpar múltiplos dias passados.

### Decisão 3: Execução Ultraleve do Sensor de Ambiente (`scan_environment.py`)
- **Escolhido**: Iteração via `os.scandir` em `.vitalia/memory/data_storage/context/` somando contagens sem abrir os arquivos JSON, mantendo o overhead estritamente abaixo de 50ms.
- **Verificado em**: Python `os.scandir` benchmark (< 10ms para < 1000 arquivos) em 15-11-2026.
- **Justificativa**: `scan_environment.py` roda no hook `before` de múltiplos comandos de sessão. Ele deve permanecer ultraleve para não degradar a experiência da IDE e o tempo de resposta.
- **Alternativas**:
  - *Ler o conteúdo de cada JSON*: Rejeitado veementemente por violar a restrição de latência (<50ms) e consumir I/O excessivo.

### Decisão 4: Executável Shim `vitalia-clean`
- **Escolhido**: Script bash simples com `#!/usr/bin/env bash`, localizando a raiz do repositório ou kit e executando `python3 -m vitalia_tmp_cleanup "$@"` ou chamando o script diretamente.
- **Verificado em**: Padrão de scripts em `source/bin/` em 15-11-2026.
- **Justificativa**: Fornece DX ergonômica para invocação direta no terminal sem que o operador precise digitar o path completo do python.
- **Alternativas**:
  - *Instalação de console_scripts via pip*: Rejeitado pois o kit opera em dual-runtime isolado sem exigir instalação global do pacote no projeto cliente.

---

## 4. Rastro de Pesquisa e Grounding P03

| Assunto | Fonte / Referência | Data Verificação | Status |
|---|---|---|---|
| Contratos do Faxineiro | `specs/003-modular-runtime-and-sensor-suite/relatorio_contratos_sdd_e_faxineiro.md` (Seção 3) | 15-11-2026 | ✅ Integral |
| Invariante GMT-04:00 | Constituição P04 | 15-11-2026 | ✅ Integral |
| Padrão OpenAPI 3.0 Limpo | `docs/CONTRATOS_WORKFLOWS_SDD.md` & `specs/007-.../contracts/` | 15-11-2026 | ✅ Validado |
| Metodologia TDA Bugfix | Constituição P05 (`[TEST:BUGFIX]` Red-First) | 15-11-2026 | ✅ Inviolável |
