<!-- research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:10(GMT-04:00) -->
> **research-brainstorming.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:10(GMT-04:00)**

# Síntese de Concepção e Brainstorming — Spec 006: Elevação Proativa de Sandbox, AGENTS.md Minimalista Agnóstico, Padrão Afirmativo e Saneamento Exaustivo do FR-006

- **Data:** 11-11-2026 21:10(GMT-04:00)
- **Status:** CONCLUÍDO (Consenso Alcançado via Nexus Socrático)
- **Feature:** `specs/006-sandbox-elevation-and-dynamic-constitution`
- **Domínio Detectado:** `arquitetura_de_aplicacao` / `infraestrutura_e_governanca`

---

## 1. Resumo Executivo e Decisões de Arquitetura

Durante o ciclo de validação pós-Spec 005, a execução real de `/vitalia-session-start` revelou que a tentativa inicial de execução dos hooks continuava disparando erro 127 no terminal (`No such file or directory`) devido à instrução reativa de elevação de sandbox ("reexecute com elevação caso dê 127").

Uma auditoria profunda e exaustiva no repositório revelou quatro frentes adicionais de melhoria crítica e alinhamento normativo:
1. **Reintrodução Inadvertida de Contadores Estáticos (Violação do FR-006 da Spec 003):** Ocorrências de `P00–P17`, `P00 a P20`, `16 workflows`, `14 lentes`, `6 catálogos` em código, prompts e testes.
2. **Meta-Leakage de Ferramentas Legadas e Proibições Negativas:** Menções no `AGENTS.md` a scripts descontinuados como `sdd_judge.py` e proibições de `kit-bootstrap.sh`, que provocam o efeito psicológico e de atenção conhecido como *Pink Elephant* (ancoragem semântica em conceitos proibidos).
3. **Monocultura de Software e Contaminação de Camadas:** O `AGENTS.md` atual impunha jargões exclusivos de engenharia de software (TDD, matrizes de falsificação) e uma "Topologia de 4 Camadas" derivada do repositório de código-fonte (`source/`), ignorando que o Kit atende a múltiplas verticais (Saúde Clínica, Pesquisa Científica, Design de Produto e Engenharia) e que no projeto instalado existem estritamente **3 Camadas** (a pasta `source/` não existe no ambiente do cliente).
4. **Violações do Padrão Afirmativo (*Instead of saying what not to do, say what to do instead*):** Ampla proliferação de proibições negativas empilhadas (`NUNCA`, `PROIBIDO`, `JAMAIS`, `Nenhum`) ao longo de `constitution.yaml`, extensões e perfis de governança.

### Decisões Alinhadas no Brainstorming:
1. **Decisão 1 — Elevação Proativa de Sandbox:** Padronizar o Passo 1 do `SKILL.md.template`, as skills em `.agents/skills/` e o `AGENTS.md` com ordem direta e imperativa: executar os hooks mandatória e inicialmente com `BypassSandbox: true`, acionando a exceção explícita *"unless mentioned otherwise"* da IDE Antigravity.
2. **Decisão 2 — AGENTS.md Minimalista Agnóstico (~35 linhas):** Reformulação enxuta, agnóstica de domínio, focada em orquestração, sem jargões de software, com framing 100% afirmativo e sem números mágicos.
3. **Decisão 3 — Descontaminação da Topologia (3 Camadas Reais):** Declarar apenas as 3 Camadas do ambiente instalado: Workspace (`project_root`), Kit Global (`kit_dir`, padrão `~/.vitalia-spec-kit/`) e Memória Persistente (`${project_root}/.vitalia/`). A pasta `source/` é estritamente restrita ao repositório de desenvolvimento e ausente no runtime do cliente.
4. **Decisão 4 — Purga de `VITALIA_KIT_DIR` do `.env`:** Remover a injeção de `VITALIA_KIT_DIR` no `.env` do projeto hospedeiro, confiando na auto-descoberta intrínseca do `kit_env_bootstrap.resolve_kit_dir()` via `Path(__file__).resolve().parent.parent` e `~/.vitalia-spec-kit/`.
5. **Decisão 5 — Saneamento Exaustivo Ponto a Ponto do FR-006:** Erradicar números mágicos e contadores estáticos em todos os pontos do código (governança, prompts, perfis, renderizadores, instalador e testes), tornando todas as asserções e loops 100% dinâmicos.
6. **Decisão 6 — Adoção do Padrão Afirmativo em Todo o Kit:** Substituir proibições negativas por prescrições afirmativas em `constitution.yaml`, `gp_*.yaml` e `extensions/*.toml`, incluindo a eliminação da proibição de `kit-bootstrap.sh`.
7. **Decisão 7 — Protocolo Estrito de Grounding:** Reordenar a diretiva: *"Toda citação de versão, documentação, endpoint ou alegação científica exige confirmação de link ativo (HTTP 200) seguida de leitura integral da fonte."*, mantendo barreira síncrona para que o orquestrador aguarde o relatório do Sub-Agente antes de emitir conclusões.
8. **Decisão 8 — Estratégia de Falsificação P05 (Combinação A+B):** Teste comportamental com injeção dinâmica de princípios constitucionais mock (`P99`) em runtime + linter estático contra números mágicos e ranges fixos em `source/`.

---

## 2. Texto Completo do `AGENTS.md` Minimalista Proposto

```markdown
<!-- AGENTS.md | Vitalia SPEC Kit v0.0.1 | DD-MM-YYYY HH:MM(GMT-04:00) -->
> **AGENTS.md | Vitalia SPEC Kit v0.0.1 | DD-MM-YYYY HH:MM(GMT-04:00)**

# AGENTS.md — Vitalia SPEC Kit

> [!IMPORTANT]
> **Governança Dinâmica via Guardian (§11 Context Lifting)**  
> As diretrizes deste projeto não residem em instruções estáticas. Cada workflow injeta em runtime a sua constituição integral, lentes especializadas e guardrails de fase em `guardian_json.sources.constitution.principles`.

## Topologia do Ambiente (3 Camadas)

1. **Workspace do Projeto (`project_root`):** Raiz do projeto resolvida pelo módulo do Kit (`kit_env_bootstrap.find_project_root()`) ou consultada em `guardian_json.env_summary.project_root`.
2. **Kit Global da Máquina (`kit_dir` — padrão ~/.vitalia-spec-kit/):** Diretório do Kit isolado resolvido por `kit_env_bootstrap.resolve_kit_dir()` ou consultado em `guardian_json.env_summary.kit_dir`, operando sobre seu próprio interpretador em `.venv/bin/python3`.
3. **Memória Persistente do Projeto (`${project_root}/.vitalia/`):** Diretório de memória persistente ancorado na raiz do projeto, contendo o histórico multi-máquina em `memory/session/` (mutado exclusivamente pelo motor de contexto) e os dados operacionais em `memory/data_storage/`.

## Ciclo Operacional

1. **Elevação Proativa de Sandbox:** Execute os comandos de hooks mandatória e inicialmente com elevação (`BypassSandbox: true`). Isso aciona a exceção explícita *"unless mentioned otherwise"* das regras do sistema Antigravity, eliminando o erro 127 no primeiro turno.
2. **Início e Encerramento:** Inicie sessões com `/vitalia-session-start` para recuperar o estado ativo da Memória 3-Tier e encerre com `/vitalia-session-end` para compilar aprendizados.
3. **Roteamento de Especialistas:** Demandas que exijam atuação verticalizada devem ser classificadas e despachadas através de `/vitalia-route` para os especialistas registrados no catálogo ativo.
4. **Separação de Preocupações:** O campo `prompt` guia a interação imediata da fase. O `guardian_json` provê as regras e princípios invioláveis do ambiente.
5. **Grounding e Verificação:** Toda citação de versão, documentação, endpoint ou alegação científica exige confirmação de link ativo (HTTP 200) seguida de leitura integral da fonte.
```

---

## 3. Matriz Ponto a Ponto de Saneamento do FR-006 (Zero Números Mágicos em Todo o Código)

Abaixo está o mapeamento exaustivo de cada ocorrência de violação ao **FR-006 da Spec 003** (*Dinamicidade Constitucional sem Números Mágicos*) encontrada no código do repositório, acompanhada da prescrição exata de saneamento para implementação:

| ID | Arquivo e Linha | Código / Texto Atual (Hardcoded) | Padrão de Saneamento Dinâmico (Substituição) |
| :- | :--- | :--- | :--- |
| **FR006-01** | `source/profiles/constitution.yaml` (L5) | `# Princípios: P00–P17 (18 princípios, 12 domínios)` | `# Princípios da Constituição Ativa do Vitalia SPEC Kit` *(Remover contadores estáticos)* |
| **FR006-02** | `source/profiles/gp_architect.yaml` (L29) | `- "Confrontar a concepção (research-brainstorming.md) contra 100% da Constituição ativa (P00–P17 sem poda)."` | `- "Confrontar a concepção (research-brainstorming.md) contra 100% da Constituição ativa injetada pelo Guardian."` |
| **FR006-03** | `source/profiles/agents_catalog.yaml` (L28) | `Executa inspeção constitucional massiva contra P00 a P17 via Sanduíche Constitucional,` | `Executa inspeção constitucional massiva contra a totalidade dos princípios da Constituição ativa via Sanduíche Constitucional,` |
| **FR006-04** | `source/extensions/judge.toml` (L45) | `confrontando-os rigorosamente contra a totalidade dos princípios constitucionais (P00 a P20),` | `confrontando-os rigorosamente contra a totalidade dos princípios constitucionais injetados em guardian_json.sources.constitution.principles,` |
| **FR006-05** | `source/extensions/task-verifier.toml` (L58) | `Extraia o catálogo de princípios constitucionais aplicáveis em guardian_json.sources.constitution.principles (P00 a P20).` | `Extraia o catálogo de princípios constitucionais aplicáveis em guardian_json.sources.constitution.principles.` |
| **FR006-06** | `source/extensions/analyze.toml` (L69) | `da Constituição (P00–P17 sem poda),` | `da Constituição ativa injetada pelo Guardian,` |
| **FR006-07** | `source/extensions/architect.toml` (L53) | `presentes em guardian_json.sources.constitution.principles (P00 a P17).` | `presentes em guardian_json.sources.constitution.principles.` |
| **FR006-08** | `source/extensions/architect.toml` (L56) | `1. **Auditoria de Conformidade Constitucional (P00–P17):**` | `1. **Auditoria de Conformidade Constitucional:**` |
| **FR006-09** | `source/src/rendering/constitution_renderer.py` (L58) | `lines.extend(["```", "", "---", "", "## 📑 Domínios e Princípios Invioláveis (P00–P17)", ""])` | `lines.extend(["```", "", "---", "", f"## 📑 Domínios e Princípios Invioláveis ({len(principles)} Princípios Ativos)", ""])` *(Dinâmico via `len`)* |
| **FR006-10** | `source/src/hooks/guardian_context.py` (L7) | `# - Todos os 16 workflows operam com 100% da Constituição (P00–P17) e dos catálogos solicitados,` | `# - Todos os workflows canônicos operam com 100% da Constituição ativa e dos catálogos solicitados,` |
| **FR006-11** | `source/src/hooks/guardian_context.py` (L39) | `"""Compilador de Context Engineering 100% Sem Poda para os 16 workflows do Vitalia SPEC Kit."""` | `"""Compilador de Context Engineering 100% Sem Poda para os workflows canônicos do Vitalia SPEC Kit."""` |
| **FR006-12** | `source/bin/install-project` (L212) | `log_ok "Antigravity IDE: 16 skills ativas configuradas com pureza total em .agents/skills/"` | `local count; count="$(find "${SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type d -name 'vitalia-*' \| wc -l)"; log_ok "Antigravity IDE: ${count} skills ativas configuradas com pureza total em .agents/skills/"` |
| **FR006-13** | `source/bin/install-project` (L268) | `echo "   AGY: 16 skills em .agents/skills/"` | `local count; count="$(find "${SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type d -name 'vitalia-*' \| wc -l)"; echo "   AGY: ${count} skills em .agents/skills/"` |
| **FR006-14** | `source/integrations/antigravity/SKILL.md.template` (L23) | `...injetado para o seu workflow (Constituição P00–P17 completa, phase_guardrails, phase_profiles, Catálogos e Histórico).` | `...injetado para o seu workflow (Constituição completa ativa, phase_guardrails, phase_profiles, Catálogos e Histórico).` |
| **FR006-15** | `source/AGENTS.md` (L19) / `.agents/AGENTS.md` (L19, L73) | `Guardian → Injeta constituição integral (P00–P17 sem poda em 100% dos workflows) e lentes gp_*.yaml` | `Guardian → Injeta constituição integral ativa e lentes de fase sem poda` |
| **FR006-16** | `source/AGENTS.md` (L40-41) / `.agents/AGENTS.md` (L40-41, L94-95) | `├── extensions/ (16 *.toml sem poda)`<br/>`├── profiles/ (6 catálogos + 14 gp_*.yaml sem poda)` | `├── extensions/ (*.toml canônicos)`<br/>`├── profiles/ (catálogos e lentes de fase)` |
| **FR006-17** | `tests/test_runtime_and_guardian.py` (L17) | `CANONICAL_16_WORKFLOWS = ["session-start", "spec-specify", ...]` *(Lista estática com 16 nomes)* | `CANONICAL_WORKFLOWS = sorted([p.stem for p in (REPO_ROOT / "source" / "extensions").glob("*.toml")])` *(Descoberta dinâmica de workflows)* |
| **FR006-18** | `tests/test_runtime_and_guardian.py` (L86) | `8. guardian_json.sources.constitution.principles contém todos os 18 princípios (P00–P17) sem poda;` | `8. guardian_json.sources.constitution.principles contém a totalidade dos princípios constitucionais sem poda;` |
| **FR006-19** | `tests/test_runtime_and_guardian.py` (L128) | `expected_principles = {f"P{i:02d}" for i in range(18)}` *(Range estático 18)* | `with open(REPO_ROOT / "source" / "profiles" / "constitution.yaml", "r", encoding="utf-8") as f: const_data = yaml.safe_load(f)`<br/>`expected_principles = set(const_data.get("principles", {}).keys())` |
| **FR006-20** | `tests/test_runtime_and_guardian.py` (L174) | `f"Workflow {wf} pruned constitution! Expected 18 principles, got {len(principles)}: ..."` | `f"Workflow {wf} pruned constitution! Expected {len(expected_principles)} principles, got {len(principles)}: ..."` |
| **FR006-21** | `tests/test_runtime_dual_venv.py` (L231) | `assert len(toml_files) == 16, f"Esperados 16 workflows, encontrados {len(toml_files)}"` | `assert len(toml_files) > 0, "Nenhum workflow TOML encontrado em source/extensions/"` *(Valida 100% dos arquivos encontrados sem acoplamento a contador fixo)* |
| **FR006-22** | `tests/test_contracts_and_handoff.py` (L117, L141) | `assert len(pairs) == 20, f"Expected 6 catalogs + 14 lenses = 20 YAML files, got {len(pairs)}"` | `expected_yaml_files = list((REPO_ROOT / "source" / "profiles").glob("*.yaml"))`<br/>`assert len(pairs) == len(expected_yaml_files), ...` *(Comparação dinâmica)* |
| **FR006-23** | `tests/test_bootstrap_and_install.py` (L17, L36) | `CANONICAL_16_WORKFLOWS = [...]`<br/>`CANONICAL_14_LENSES = [...]` | Listas dinâmicas derivadas de `glob("source/extensions/*.toml")` e `glob("source/profiles/gp_*.yaml")`. |
| **FR006-24** | `tests/test_bootstrap_and_install.py` (L249) | `assert len(vitalia_skills) == 16, f"Expected 16 vitalia-* skills, found {len(vitalia_skills)}"` | `expected_count = len(list((REPO_ROOT / "source" / "extensions").glob("*.toml")))`<br/>`assert len(vitalia_skills) == expected_count, ...` |
| **FR006-25** | `source/tests/test_context_lifting_integrity.py` (L18) | `ou se omitir princípios invioláveis da Constituição (P00 a P17).` | `ou se omitir princípios invioláveis da Constituição ativa.` |
| **FR006-26** | `tests/test_context_engine_3tier.py` (L161-162) | `"decision": "Zero Poda incondicional nos 16 workflows",`<br/>`"rationale": "Preserva fidelidade integral dos 18 princípios P00-P17"` | `"decision": "Zero Poda incondicional nos workflows canônicos",`<br/>`"rationale": "Preserva fidelidade integral da totalidade dos princípios constitucionais"` |

---

## 4. Tabela Completa: Violações do Padrão Afirmativo no Kit e Versões de Substituição

*(Incluindo a purga da proibição de `kit-bootstrap.sh` e das restrições de `sdd_judge.py` no `AGENTS.md`).*

| Arquivo e Linha | Texto Atual (Negativo / Proibição) | Versão de Substituição (Afirmativa / Prescritiva) |
| :--- | :--- | :--- |
| **`source/AGENTS.md` (L33) / `.agents/AGENTS.md` (L33, L85)** | `É TERMINANTEMENTE PROIBIDO e vetado ao agente de IA executar ./kit-bootstrap.sh ou tentar reinstalar o kit por iniciativa própria diante de falhas de permissão ou sandbox quando o kit já estiver presente em disco.` | `O kit opera sob o interpretador isolado em ${VITALIA_KIT_DIR}/.venv. Comandos de hooks internos são executados diretamente com elevação (BypassSandbox: true), eliminando falhas de permissão e sandbox.` *(No novo AGENTS.md minimalista, essa menção a bootstrap é totalmente suprimida).* |
| **`source/AGENTS.md` (L32) / `.agents/AGENTS.md` (L32, L84)** | `NUNCA execute comandos CLI do script legado sdd_judge.py no terminal. Quando qualquer workflow solicitar a validação adversarial... execute diretamente na IDE como Sub-Agente...` | `Auditorias de conformidade executam nativamente na IDE através de Sub-Agentes especializados com emissão de relatório físico e aprovação HITL soberana.` *(No novo AGENTS.md minimalista, simplificado para o ciclo operacional).* |
| **`source/AGENTS.md` (L28) / `.agents/AGENTS.md` (L28, L80)** | `NUNCA cite versões ou links sem teste prévio (HTTP 200) e leitura integral da documentação.` | `Toda citação de versão, documentação, endpoint ou alegação científica exige confirmação de link ativo (HTTP 200) seguida de leitura integral da fonte.` |
| **`source/profiles/constitution.yaml` (L47-49)** | `Nunca implementar código sem tasks.md aprovado. Pipeline obrigatório: specify → plan → tasks → implement → converge.` | `A implementação de código ocorre exclusivamente sob tasks.md formalmente aprovado, seguindo o pipeline estrito: specify → plan → tasks → implement → converge.` |
| **`source/profiles/constitution.yaml` (L104, L115-117)** | `Nenhuma lógica produtiva... é implementado sem teste... É ESTRITAMENTE PROIBIDO usar asserções puramente sintáticas/estáticas isoladas (como assert path.is_file())...` | `Toda lógica produtiva, script ou contrato exige teste automatizado correspondente na Matriz de 4 Modalidades com Cenário de Falsificação explícito que comprove falha funcional prévia. A conclusão é atestada exclusivamente por comportamento executável de caixa-preta.` |
| **`source/profiles/constitution.yaml` (L131)** | `Nenhum segredo entra em commits, logs ou outputs de console. Migrações de banco são não-destrutivas e idempotentes.` | `Commits, logs e outputs de console contêm exclusivamente dados sanitizados e públicos. Chaves e segredos residem unicamente em variáveis de ambiente (.env) ou vaults seguros.` |
| **`source/profiles/constitution.yaml` (L158-159)** | `Agentes não acessam ferramentas fora de seu domínio declarado (default-deny).` | `Agentes operam estritamente com as ferramentas e escopos declarados em seu respectivo catálogo de domínio.` |
| **`source/profiles/constitution.yaml` (L199-205)** | `Nenhum nome de modelo LLM hardcoded... sendo terminantemente proibidos meta-campos... Nenhum machine_id hardcoded...` | `Modelos de LLM derivam de variáveis de ambiente (.env). Contratos de schemas adotam exclusivamente o subset OpenAPI 3.0 limpo. Identificadores de máquina derivam dinamicamente de VITALIA_MACHINE_NAME ou do hash do hostname.` |
| **`source/profiles/constitution.yaml` (L216-219)** | `Output de LLMs nunca executado sem validação... Agentes não executam ações destrutivas sem confirmação HITL. Stack trace nunca vaza para o cliente.` | `Outputs de LLMs são executados após validação formal de schema. Ações de impacto estrutural exigem confirmação humana (HITL). Respostas a clientes contêm mensagens genéricas seguras, com stack traces restritos a logs internos.` |
| **`source/profiles/constitution.yaml` (L230-233)** | `Nenhum endpoint de dado de saúde é público... sem stack trace para o cliente...` | `Endpoints de dados de saúde operam sob autenticação JWT obrigatória, autorização granular por recurso, rate limiting e sanitização de schema.` |
| **`source/profiles/constitution.yaml` (L273)** | `Modificações parciais que tornam arquivos inconsistentes são vetadas.` | `Toda modificação preserva a consistência e integridade sintática integral do arquivo editado.` |
| **`source/profiles/gp_brainstorming.yaml` (L29)** | `STOP -> SCAN -> ASK (máx 3 perguntas) -> WAIT: proibido gerar spec/plan/tasks/código durante a ideação.` | `Ciclo estrito de ideação: execute STOP -> SCAN -> ASK (máx 3 perguntas) -> WAIT, mantendo o foco exclusivamente no alinhamento de premissas e requisitos antes de qualquer especificação formal.` |
| **`source/profiles/gp_session-end.yaml` (L32)** | `Regra da Cerca Elétrica: NUNCA editar ou commitar diretamente em .vitalia/memory/session/ via ferramentas da IDE ou git commit manual.` | `Regra da Cerca Elétrica: toda gravação, mutação e sincronização de histórico em .vitalia/memory/session/ é realizada exclusivamente através do utilitário vitalia_context_engine.py.` |
| **`source/profiles/gp_session-consolidate.yaml` (L32)** | `Regra da Cerca Elétrica: NUNCA editar diretamente .vitalia/memory/session/README.md ou context.md...` | `Regra da Cerca Elétrica: o README.md e os artefatos de memória são gerados exclusivamente pelo motor de contexto (vitalia_context_engine.py --action consolidate).` |
| **`source/profiles/gp_spec-tasks.yaml` (L29)** | `Proibição de Testes Rasos: nenhuma tarefa de teste pode ter como critério apenas assert path.is_file()...` | `Critério de Testes Comportamentais: tarefas de teste devem declarar explicitamente o Cenário de Falsificação e validar a execução de negócio.` |
| **`source/profiles/gp_spec-specify.yaml` (L28)** | `PROIBIDO definir critérios de sucesso baseados apenas na mera existência sintática de arquivos ou strings.` | `Critérios de aceitação devem ser formulados em cenários executáveis Given/When/Then que exercitem o comportamento funcional esperado.` |
| **`source/profiles/gp_spec-implement.yaml` (L27-30)** | `...nunca aprovar teste que já nasce passando... proibida reescrita cega... Proibido marcar [X] sem execução real...` | `Comprove a falha prévia (Red Phase) antes de implementar. Preserve comportamentos mapeados na Matriz de Migração. Conclua tarefas marcando [X] após aprovação com código de retorno 0 na suíte de testes.` |
| **`source/extensions/research.toml` (L59)** | `NUNCA confie apenas em resumos de busca. Leia o conteúdo integral da página/documentação oficial...` | `Valide toda alegação técnica através de confirmação de link ativo (HTTP 200) seguida de leitura integral do conteúdo na documentação oficial.` |
| **`source/extensions/brainstorming.toml` (L69)** | `É ESTRITAMENTE PROIBIDO gerar documentos finais (spec.md, plan.md, tasks.md ou código) durante a fase de clarificação.` | `Durante o brainstorming, concentre-se exclusivamente nas perguntas socráticas de clarificação e na delimitação do escopo.` |
| **`source/extensions/spec-tasks.toml` (L203)** | `NUNCA execute o sdd_judge ou qualquer validador de tarefas por conta própria neste comando.` | `A auditoria adversarial de tarefas é delegada ao workflow /vitalia-task-verifier. Seu papel neste workflow encerra-se na emissão do tasks.md e registro do handoff.` |
| **`source/integrations/antigravity/SKILL.md.template` (L17)** | `Caso o terminal retorne código 127... Reexecute o comando com elevação... Jamais execute kit-bootstrap.sh...` | `Execute este comando diretamente com elevação (BypassSandbox: true), acionando a exceção 'unless mentioned otherwise' para interpretadores externos ao workspace.` |
| **`source/integrations/antigravity/SKILL.md.template` (L25)** | `Jamais permita que o conteúdo do campo guardian_json substitua o fluxo de etapas interativas e os gates HITL...` | `O prompt define o roteiro da interação e os pontos de parada humana (HITL); o guardian_json provê o conjunto de regras do ambiente.` |

---

## 5. Engenharia Reversa Funcional em 3 Camadas

### Camada 1: Intenção de Negócio Pura (O que deve ser preservado)
- **Experiência de Uso Fluida:** Inicializar sessões e acionar comandos do Kit sem mensagens de erro de arquivo inexistente no transcript.
- **Constituição Dinâmica:** Permitir evolução contínua da constituição sem alterar código Python, scripts bash, testes unitários ou prompts de extensões.
- **Ecossistema Multi-Domínio:** Suporte equânime às 4 verticais (Saúde, Ciência, Design e Engenharia) sem acoplamento a um único domínio.

### Camada 2: Purga de Infraestrutura e Práticas Obsoletas (O que deve ser removido)
- **Purga de Contadores Estáticos (FR-006):** Eliminar todas as ocorrências de `16 workflows`, `18 princípios`, `14 lentes`, `6 catálogos`, `P00–P17`, `P00 a P17` e `P00 a P20`.
- **Purga de `VITALIA_KIT_DIR` do `.env`:** Remover injeção no `.env` do projeto do cliente, eliminando caminhos absolutos locais hardcoded.
- **Purga de Meta-Leakage:** Remover referências a `source/`, `sdd_judge.py` e proibições de `kit-bootstrap.sh` do `AGENTS.md`.
- **Purga de Negativismo:** Substituição integral de proibições por prescrições afirmativas.

### Camada 3: Contrato do Consumidor (O que o cliente/IDE exige estritamente)
- **Contrato da IDE Antigravity:** Atendimento estrito à cláusula *"unless mentioned otherwise"*, autorizando execução com `BypassSandbox: true` sem violar a política de segurança.
- **Padrão AGENTS.md da Linux Foundation:** Formato markdown conciso (< 50 linhas), orientado a comandos e onboarding de alto sinal.
- **Contratos OpenAPI 3.0 Limpos:** Preservação estrita dos schemas e ausência de meta-campos incompatíveis.
- **Isolamento de Runtime sem Pasta `source/`:** O código e scripts devem operar cientes de que a pasta `source/` existe exclusivamente no repositório de desenvolvimento; no ambiente do cliente instalado, o kit reside exclusivamente em `${VITALIA_KIT_DIR}` (Camada 2), sem presença de `source/`.

---

## 6. Classificação na Matriz de Testes (P05) e Cenários de Falsificação

| Modalidade | Componente / Alvo | Cenário de Falsificação (O que fará o teste falhar) |
| :--- | :--- | :--- |
| **`[TEST:BUGFIX]`** | `source/integrations/antigravity/SKILL.md.template` e `.agents/skills/*/SKILL.md` | Falha se o template ou as skills geradas não declararem a instrução expressa de `BypassSandbox: true` no Passo 1, ou se mantiverem instrução puramente reativa pós-127. |
| **`[TEST:NEW]`** | Injeção Dinâmica Constitucional (`tests/test_dynamic_constitution_resilience.py`) | Falha se a adição de um princípio arbitrário (`P99`) no dicionário de princípios fizer `constitution_renderer.py`, `guardian_context.py` ou os linters falharem por esperar uma quantidade fixa de princípios. |
| **`[TEST:REFACTOR]`** | `tests/test_runtime_and_guardian.py`, `tests/test_runtime_dual_venv.py`, `tests/test_contracts_and_handoff.py`, `tests/test_bootstrap_and_install.py` | Falha se os testes de suíte continuarem comparando contra constantes estáticas (`range(18)`, `len == 16`, `len == 20`) em vez de comparar contra os arquivos reais descobertos em disco via `constitution.yaml` e `glob("*.toml")`. |
| **`[TEST:REFACTOR]`** | `source/src/rendering/constitution_renderer.py` e `source/bin/install-project` | Falha se o renderizador emitir cabeçalho Markdown com faixa estática `(P00–P17)` em vez de contagem dinâmica, ou se o instalador logar mensagem estática de "16 skills". |
| **`[TEST:REFACTOR]`** | `source/bin/lib/env_manager.sh` e `source/src/kit_env_bootstrap.py` | Falha se o instalador continuar gravando `VITALIA_KIT_DIR` no `.env` do projeto, ou se o `resolve_kit_dir()` falhar em resolver o Kit na ausência da chave no `.env`. |
| **`[TEST:REFACTOR]`** | Linter do Padrão Afirmativo (`tests/test_affirmative_patterns_linter.py`) | Linter estático que falha caso encontre palavras proibidas (`NUNCA`, `sdd_judge.py`, `kit-bootstrap.sh`, `proibido gerar`, `Topologia de 4 Camadas`) em `source/AGENTS.md` ou `source/profiles/constitution.yaml`. |

---

## 7. Requisitos Funcionais Preliminares da Spec 006

- **FR-001 (Elevação Proativa de Sandbox na Skill):** Atualizar `SKILL.md.template`, regenerar `.agents/skills/*/SKILL.md` com diretiva imperativa de `BypassSandbox: true`.
- **FR-002 (AGENTS.md Minimalista Agnóstico):** Implementar o novo `source/AGENTS.md` minimalista de 3 Camadas, framing afirmativo e agnóstico às 4 verticais.
- **FR-003 (Purga de `VITALIA_KIT_DIR` do `.env`):** Purgar a gravação de `VITALIA_KIT_DIR` em `env_manager.sh` e refatorar `resolve_kit_dir()` para priorizar auto-localização intrínseca e `~/.vitalia-spec-kit/`.
- **FR-004 (Saneamento do Padrão Afirmativo em Todo o Kit):** Aplicar as substituições afirmativas da Tabela 4 em `constitution.yaml`, `gp_*.yaml` e `extensions/*.toml`.
- **FR-005 (Dinamicidade Constitucional sem Números Mágicos — FR-006):** Executar integralmente a Matriz 3 (FR006-01 a FR006-26) em `constitution_renderer.py`, `install-project` e em toda a suíte de testes `tests/`.
- **FR-006 (Protocolo de Grounding com Barreira Síncrona):** Padronizar a regra afirmativa de link ativo HTTP 200 seguido de leitura integral, e blindar o workflow de pesquisa para que sínteses exijam consumo do relatório verificado.

---

## 8. Rastro de Pesquisa e Grounding (P03 — URLs Validadas HTTP 200)

| # | Afirmação / Evidência Técnica | Fonte Canônica | URL Validada (HTTP 200) | Status |
| :- | :--- | :--- | :--- | :---: |
| 1 | Diretriz *"Instead of just saying what not to do, say what to do instead"* | OpenAI Prompt Engineering Guide | https://platform.openai.com/docs/guides/prompt-engineering | Ativo (200) |
| 2 | Diretriz *"Tell Claude what to do instead of what not to do"* | Anthropic Prompt Engineering Overview | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview | Ativo (200) |
| 3 | Regras operacionais devem focar em affordances afirmativas e comandos | Anthropic — Be Clear and Direct | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct | Ativo (200) |
| 4 | `CLAUDE.md` / `AGENTS.md` como onboarding enxuto; barreiras críticas via ferramentas | Anthropic Claude Code Overview | https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview | Ativo (200) |
| 5 | Curva em U de atenção e perda de recuperação de instruções no meio (*Lost in the Middle*) | Liu et al. (Stanford / UC Berkeley / TACL 2024) | https://arxiv.org/abs/2307.03172 | Ativo (200) |
| 6 | Princípios constitucionais como lentes dinâmicas de auto-crítica, não texto estático | Bai et al. (Anthropic Constitutional AI) | https://arxiv.org/abs/2212.08073 | Ativo (200) |
| 7 | Análise mecanicista de negações e ativação de conceitos proibidos em camadas médias | arXiv:2605.03052 (*Language Models Process Negation*) | https://arxiv.org/abs/2605.03052 | Ativo (200) |
| 8 | Especificação aberta do padrão `AGENTS.md` (formato livre, conciso, focado no agente) | Linux Foundation / Agentic AI Foundation | https://agents.md/ | Ativo (200) |

---

## 9. Próximo Passo

Síntese de concepção concluída e registrada. A transição determinística deve ser registrada via `vitalia_handoff.py` para permitir que o `/vitalia-route` despache a demanda para a especificação técnica formal (`/vitalia-spec-specify`).
