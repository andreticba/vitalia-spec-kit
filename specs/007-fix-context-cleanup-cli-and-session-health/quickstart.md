<!-- quickstart.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 12:20(GMT-04:00) -->
> **quickstart.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 12:20(GMT-04:00)**

# Quickstart: [BUGFIX] Faxineiro de Contexto CLI & Saúde de Sessão (Spec 007)

## Pré-requisitos
- Ambiente Linux com bash e python3.
- Arquivos de teste populados em `.vitalia/memory/data_storage/context/<machine_id>/`.

---

## Cenário 1: Inspeção sem Deleção (`--dry-run`)
Executa a simulação completa listando as datas e informando que nenhum arquivo foi apagado.

```bash
source/bin/vitalia-clean --dry-run
```
**Resultado Esperado**:
- Exibe o menu com datas agrupadas.
- Identifica claramente a data de hoje como preservada.
- Emite aviso `[DRY-RUN] Simulação concluída. Nenhum arquivo foi removido.`

---

## Cenário 2: Faxina Automatizada em CI/Script (`--force`)
Remove todos os arquivos anteriores a hoje sem interação humana, preservando hoje.

```bash
source/bin/vitalia-clean --force
```
**Resultado Esperado**:
- Arquivos de datas civis anteriores são removidos.
- Arquivos da data civil de hoje permanecem intactos.
- Exit code 0.

---

## Cenário 3: Purga Total com Confirmação (`--purge-all`)
Solicita confirmação afirmativa antes de apagar inclusive os arquivos de hoje.

```bash
echo "s" | source/bin/vitalia-clean --purge-all
```
**Resultado Esperado**:
- Solicita confirmação `Tem certeza que deseja apagar TODOS os arquivos de contexto, incluindo hoje? [s/N]:`.
- Com resposta `s`, apaga todos os arquivos.
- Se a resposta for vazia (Enter) ou `n`, cancela a operação sem apagar nada.

---

## Cenário 4: Inspeção de Saúde via `scan_environment.py`
Verifica a presença do nó `context_cleanup` na saída JSON do sensor.

```bash
python3 source/src/hooks/scan_environment.py
```
**Resultado Esperado**:
- JSON contém a chave `"context_cleanup"`.
- Campos `total_files`, `eligible_files`, `eligible_bytes`, `needs_cleanup` presentes e no formato OpenAPI 3.0 Limpo.
