<!-- quickstart.md | Vitalia SDD v0.6.0 | 10-11-2026 15:05(GMT-04:00) -->
> **quickstart.md | Vitalia SDD v0.6.0 | 10-11-2026 15:05(GMT-04:00)**

# Quickstart & Guia de Verificação: 003-modular-runtime-and-sensor-suite

**Data:** 10-11-2026 15:05 (GMT-04:00)  
**Status Constitucional:** EM CONFORMIDADE (P10 DIDACTICS-FIRST & AUTOMATION)  
**Feature:** `specs/003-modular-runtime-and-sensor-suite`  
**Autor:** Vitalia AI Spec Lead & Solution Architect  

---

## 1. Pré-Requisitos

- Ambiente Linux ou WSL2 (Ubuntu 22.04+ / Debian 12+).
- Python 3.10+ instalado com `venv` disponível.
- Repositório clonado e interpretador ativo.

---

## 2. Cenário de Validação 1: Verificação da Suíte VRSS (5 Sensores)

Execute cada um dos 5 sensores modulares para certificar a pureza do repositório:

```bash
# 1. Sensor de Pureza da Árvore de Skills (.agents/skills/)
python3 source/src/sensors/sensor_purity.py --target-dir .agents/skills
# Esperado: 100% dos diretórios válidos, zero arquivos soltos ou pastas ocultas. Código de saída: 0.

# 2. Sensor de Higiene de Caminhos
python3 source/src/sensors/sensor_path_hygiene.py --scan-dir source/
# Esperado: Zero strings de caminhos absolutos hardcoded (source/, ~/.vitalia). Código de saída: 0.

# 3. Sensor de Integridade do Ledger e Shards
python3 source/src/sensors/sensor_memory_ledger.py --memory-dir .vitalia/memory
# Esperado: Shards ordenados decrescentemente por last_sync e hashes válidos. Código de saída: 0.

# 4. Sensor de Prevenção de Vazamento e Tokens
python3 source/src/sensors/sensor_tokens_leak.py --context-dir .vitalia/memory/data_storage/context
# Esperado: Zero segredos/tokens de API expostos. Código de saída: 0.

# 5. Sensor de Contratos DbC
python3 source/src/sensors/sensor_contract_dbc.py --extensions-dir source/extensions/
# Esperado: 100% dos 16 workflows canônicos validados com contratos DbC íntegros. Código de saída: 0.
```

---

## 3. Cenário de Validação 2: Execução de Context Lifting Limpo (Zero Context Rot)

Invoque um workflow qualquer e inspecione o arquivo de contexto para atestar ausência de ruído:

```bash
# Executa o hook runner para o workflow spec-specify
python3 source/src/vitalia_hook_runner.py source/extensions/spec-specify.toml --phase before

# Inspecione o JSON gerado (caminho retornado no campo workflow_context_file)
# Valide que a chave tmp_cleanup_matrix NÃO EXISTE no guardian_json:
grep -q "tmp_cleanup_matrix" <caminho_do_arquivo_de_contexto.json> && echo "FALHA: Matriz presente" || echo "SUCESSO: Contexto limpo"
```

---

## 4. Cenário de Validação 3: Utilitário Autônomo de Faxina (`vitalia_tmp_cleanup.py`)

Verifique a ajuda didática e o modo de simulação (dry-run):

```bash
# Exibe ajuda didática com exemplos
python3 source/src/vitalia_tmp_cleanup.py --help

# Executa simulação de limpeza (dry-run)
python3 source/src/vitalia_tmp_cleanup.py --dry-run
# Esperado: Relatório estruturado de arquivos candidatos sem remoção física.
```

---

## 5. Cenário de Validação 4: Suíte Completa de Testes Comportamentais P05

Execute todos os testes automatizados da Matriz de 4 Modalidades:

```bash
pytest source/tests/ -v
# Esperado: Todos os testes de BUGFIX, MIGRATION e NEW verdes com zero asserções rasas.
```

