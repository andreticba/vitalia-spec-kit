<!-- ADR-0003-installer-preflight-isolated-venv-observability.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:10(GMT-04:00) -->
> **ADR-0003-installer-preflight-isolated-venv-observability.md | Vitalia SPEC Kit v0.0.1 | 10-11-2026 19:10(GMT-04:00)**

# ADR-0003: Pre-Flight Check Unificado, Inviolabilidade do `.venv` Puro (Purga de `--system-site-packages`) e Observabilidade Passo a Passo no Ciclo de Instalação

- **Status:** Proposto (Pausa HITL Soberana)
- **Data:** 10-11-2026
- **Autor:** Vitalia Architect (`/vitalia-architect`)
- **Feature:** `specs/004-installer-preflight-and-verbosity`
- **Fontes Canônicas:**
  - [`specs/004-installer-preflight-and-verbosity/research-brainstorming.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/specs/004-installer-preflight-and-verbosity/research-brainstorming.md)
  - [`docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0001-universal-bootstrap-4-layer-topology-no-prune.md)
  - [`docs/adr/ADR-0002-modular-runtime-sensor-suite-clean-context.md`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/docs/adr/ADR-0002-modular-runtime-sensor-suite-clean-context.md)

---

## 1. Contexto e Problema

Durante a validação prática do ciclo de instalação e bootstrap do Vitalia SPEC Kit em novas máquinas e ambientes restritos (como containers, sandboxes ou sistemas de arquivos com permissões de usuário limitadas), identificaram-se fragilidades operacionais e de observabilidade:
1. **Caixa-Preta Silenciosa:** O instalador [`kit-bootstrap.sh`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/kit-bootstrap.sh) executava o provisionamento do `pip` com supressão total (`--quiet >/dev/null 2>&1`), deixando o usuário sem feedback por dezenas de segundos sem saber se o processo travou ou se prossegue normalmente.
2. **Degradação Frágil via `--system-site-packages`:** Diante de falhas no download ou compilação de pacotes isolados, o script destruía o ambiente virtual isolado e o recriava com `python3 -m venv --system-site-packages`. Essa prática viola a inviolabilidade de runtime isolado (P11) e introduz falhas em cascata quando bibliotecas fundamentais (`pyyaml`, `jinja2`, `jsonschema`, `pytest`) não existem nos pacotes do sistema global da máquina.
3. **Falhas Abruptas por Ausência de Pre-Flight de Permissões:** O instalador tentava criar diretórios cegamente em `${TARGET_KIT_DIR}` e `~/.local/bin` sem testar permissões de escrita prévias, resultando em erros fatais não-tratados (`mkdir: Read-only file system`).
4. **Verificação Semântica Rasa de Dependências:** O script apenas checava `command -v python3`, sem validar se a versão atendia a exigência mínima de Python `>= 3.10`.
5. **Lacuna de Orientação de Shell:** Ao gravar exports em `~/.bashrc` e `~/.zshrc`, o processo não comunicava ostensivamente que o shell corrente do usuário precisava recarregar suas variáveis para reconhecer os shims instalados.

---

## 2. Decisões Arquiteturais Estruturantes

### 2.1. Criação do Módulo Compartilhado de Pre-Flight (`source/bin/lib/preflight.sh`)
- Centralizar em uma biblioteca desacoplada todas as rotinas de inspeção prévia de ambiente consumidas por [`kit-bootstrap.sh`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/kit-bootstrap.sh) e [`source/bin/install-project`](file:///home/andre/projetos/assistidos/vitalia-spec-kit/source/bin/install-project).
- Rotinas obrigatórias:
  1. `check_python_version_semver`: Valida execução de Python `>= 3.10` via one-liner determinístico.
  2. `check_venv_capability`: Criação real de venv temporário para atestar a presença de `python3-venv`.
  3. `check_writable_paths`: Validação de permissão de escrita efetiva nos diretórios de destino antes de qualquer mutação em disco.
  4. `check_git_requirements`: Validação de presença do Git e pré-teste não-destrutivo de URLs de repositórios remotos de sessão e dados.

### 2.2. Purga Incondicional de `--system-site-packages` (Inviolabilidade do `.venv` Puro)
- O kit v0.0.1 veta estritamente o uso da flag `--system-site-packages`. O ambiente virtual isolado em `${VITALIA_KIT_DIR}/.venv` deve conter exclusivamente seus próprios pacotes autônomos.
- Se a instalação de dependências via `pip` falhar, o script:
  - Interrompe imediatamente a execução (`exit 1`).
  - Preserva o `.venv` intacto para inspeção forense ou limpa de forma controlada.
  - Exibe o caminho do arquivo de log com as causas exatas do erro (`/tmp/vitalia-bootstrap.log`).
  - Emite diagnóstico prescritivo detalhando causas prováveis (ausência de rede/proxy, pacotes de compilação faltantes) e comandos acionáveis.

### 2.3. Observabilidade Passo a Passo com Redirecionamento de Logs
- Adoção de formato de saída com indicadores visuais de estado padronizados (`⏳`, `✅`, `❌`, `⚠️`).
- Durante operações lentas (como criação do venv e instalação de pacotes), saídas extensas de stdout/stderr são canalizadas para arquivos temporários dedicados (`/tmp/vitalia-bootstrap.log` e `/tmp/vitalia-install.log`).
- Em caso de falha, o instalador extrai automaticamente as últimas 15 linhas do log para o console, combinando limpeza visual com rastreabilidade imediata.
- Suporte nativo à flag `-v` / `--verbose` para desativar a supressão de logs em ambientes de integração contínua (CI).

### 2.4. Comunicação Ativa de Ambiente e $PATH
- Na finalização bem-sucedida do bootstrap, o instalador imprime um banner destacado instruindo o desenvolvedor a recarregar o shell ativo:
  ```text
  ⚡ Para ativar os comandos imediatamente neste terminal, execute:
     source ~/.bashrc   # ou source ~/.zshrc
  ```

---

## 3. Consequências e Trade-offs

### Positivas
- **Previsibilidade:** Falhas de ambiente e permissões são capturadas no segundo 0, antes de criar arquivos residuais em disco.
- **Isolamento e Robustez:** Elimina o risco de contaminação por pacotes globais obsoletos do sistema operacional.
- **Experiência do Desenvolvedor (DX):** Fim da sensação de terminal travado durante etapas lentas do `pip`.
- **Rastreabilidade Imediata:** Logs em `/tmp/` permitem depuração forense sem poluir o terminal durante o uso diário.

### Trade-offs Aceitos
- Ambientes estritamente offline exigirão provisionamento prévio de wheels locais ou conexão de rede para a criação inicial do `.venv` puro, sem o fallback leniente para o sistema.

