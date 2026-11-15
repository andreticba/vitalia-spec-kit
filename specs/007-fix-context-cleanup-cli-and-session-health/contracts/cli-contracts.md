<!-- cli-contracts.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 12:10(GMT-04:00) -->
> **cli-contracts.md | Vitalia SPEC Kit v0.0.1 | 15-11-2026 12:10(GMT-04:00)**

# Contratos de API Interna, CLI e Schemas OpenAPI 3.0 Limpo: Spec 007 — [BUGFIX] Faxineiro e Saúde da Sessão

---

## 1. Contrato OpenAPI 3.0 Limpo do Nó `context_cleanup`

O diagnóstico de saúde de ambiente gerado por `source/src/hooks/scan_environment.py` injeta o nó `context_cleanup` em `env_summary`. Este nó segue estritamente o subset **OpenAPI 3.0 Limpo**:
- **Zero Meta-Campos:** Proibido o uso de `$schema`, `title` no nó raiz e `additionalProperties: false`.
- **Tipos Primitivos Estritos:** Campos representados como tipos planos da OpenAPI 3.0 (`integer`, `boolean`).
- **Interoperabilidade Gemini REST:** 100% compatível com compiladores de Structured Outputs de modelos de fronteira.

### 1.1 Schema Formal (`specs/007-fix-context-cleanup-cli-and-session-health/contracts/context_cleanup.schema.json`)

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

### 1.2 Exemplo de Instância Válida no Retorno do `scan_environment.py`

```json
{
  "status": "HEALTHY",
  "project_root": "/home/andre/projetos/assistidos/vitalia-spec-kit",
  "kit_dir": "/home/andre/.vitalia-spec-kit",
  "kit_runtime": {
    "kit_dir": "/home/andre/.vitalia-spec-kit",
    "python_bin": "/home/andre/.vitalia-spec-kit/.venv/bin/python3",
    "status": "HEALTHY"
  },
  "project_runtime": {
    "project_root": "/home/andre/projetos/assistidos/vitalia-spec-kit",
    "has_venv": false,
    "python_bin": null,
    "source_detected": "not_found"
  },
  "context_cleanup": {
    "total_files": 42,
    "eligible_files": 41,
    "eligible_bytes": 3334520,
    "needs_cleanup": true
  },
  "has_env": true,
  "issues": []
}
```

---

## 2. Contrato de Interface CLI: `source/src/vitalia_tmp_cleanup.py`

### 2.1 Assinatura da Função Central
```python
def cleanup_contexts(
    target_root: Path,
    dry_run: bool = False,
    force: bool = False,
    purge_all: bool = False,
    input_stream: Optional[TextIO] = None
) -> int:
    ...
```

- **`target_root`**: Raiz do projeto hospedeiro contendo `.vitalia/`.
- **`dry_run`**: Se `True`, simula a categorização e exibe o plano sem deletar arquivos físicos (`exit code 0`).
- **`force`**: Se `True`, executa em modo não-interativo correspondente à opção `[a]` (apaga dias anteriores e protege a sessão de hoje sem prompts).
- **`purge_all`**: Se `True`, executa em modo não-interativo correspondente à opção `[t]` (purga completa deliberada, inclusive hoje).
- **`input_stream`**: Stream de entrada para injeção de `stdin` em testes automatizados (`[TEST:BUGFIX]`).
- **Retorno (`int`)**: Código de saída POSIX (`0` para sucesso/cancelamento normal, `1` para erros de IO ou parâmetros inválidos).

### 2.2 Gramática de Opções Interativas (`[a/d/n/t]`)
| Opção | Ação Executada | Salvaguarda de 'Hoje' | Confirmação Adicional Requerida |
| :--- | :--- | :---: | :---: |
| `a` / `A` | Remove 100% dos envelopes de datas anteriores | ✅ **Protegida** | Não |
| `d` / `D` | Solicita índices (`1,2` ou `1-3`) e remove apenas os dias selecionados | ✅ **Protegida** | Não |
| `n` / `N` / `Enter` | Cancela a operação sem remover arquivos | ✅ **Intacta** | Não |
| `t` / `T` | Purga todos os envelopes | ⚠️ **Removida** | Sim (`[s/N]`) |
