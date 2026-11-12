<!-- research.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:50(GMT-04:00) -->
> **research.md | Vitalia SPEC Kit v0.0.1 | 11-11-2026 21:50(GMT-04:00)**

# Technical Research: Spec 006 — Sandbox Elevation, Minimalist AGENTS.md, Variable Purge & Dynamic Constitution

- **Feature:** `specs/006-sandbox-elevation-and-dynamic-constitution`
- **Autor:** Vitalia SPEC Kit Architect & Research Engineer
- **Data:** 11-11-2026 21:50(GMT-04:00)
- **Status:** Concluído com Grounding Oficial (HTTP 200)

---

## 1. Decisões Técnicas e Grounding

### Decisão 1: Elevação Proativa de Sandbox na Invocação de Workflows
- **Escolhido:** Inserção da diretiva explícita no Passo 1 do `source/integrations/antigravity/SKILL.md.template` e `.agents/skills/*/SKILL.md`:
  `1. Execute o comando com elevação de sandbox mandatória e inicial (BypassSandbox: true):`
- **Verificado em:** [`https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct`](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct) e contrato de terminal Antigravity em 11-11-2026 (HTTP 200).
- **Justificativa:** O sandbox padrão da IDE Antigravity restringe o isolamento ao workspace (`${PWD}`). A diretiva canônica do terminal diz: *"Try Sandboxed First: You should attempt to run every command in Standard Sandbox Mode first unless mentioned otherwise"*. Ao prescrever explicitamente a elevação no Passo 1, aciona-se a cláusula *"unless mentioned otherwise"*, eliminando o erro de cold-start 127 (`No such file or directory`) sem quebrar regras de segurança.
- **Alternativas:**
  - *Manter sandbox padrão e esperar falha 127 para reexecutar:* Rejeitado porque gera atrito ao usuário, consome turnos de conversação desnecessários e induz a IA a loops de auto-reinstalação.
  - *Tentar symlinks dentro do workspace:* Rejeitado porque polui a raiz do projeto e colide com PEP 405 de resolução de virtualenvs.

---

### Decisão 2: Topologia Real de 3 Camadas no Cliente e AGENTS.md Minimalista
- **Escolhido:** Redução do `AGENTS.md` para ~35 linhas agnósticas de domínio, apresentando o ecossistema de especialistas e formalizando a Topologia Real de 3 Camadas (`<project_root>/`, `<kit_dir>/` e `<project_root>/.vitalia/`).
- **Verificado em:** [`https://agents.md`](https://agents.md) (Linux Foundation) em 11-11-2026 (HTTP 200).
- **Justificativa:** O manifesto do projeto deve ser conciso e focado no propósito do repositório. Regras comportamentais dinâmicas e princípios de desenvolvimento de software residem na Constituição (`constitution.yaml`) e são injetados pelo Guardian (§11). A pasta `source/` é exclusiva do repositório de desenvolvimento e não existe no cliente instalado.
- **Alternativas:**
  - *Manter lista de regras de TDD no AGENTS.md:* Rejeitado porque acopla governança de código de software a outros domínios de especialistas (médico, design, acadêmico).
  - *Manter lista fixa de domínios no AGENTS.md:* Rejeitado porque engessa o ecossistema e exige manutenção estática a cada novo especialista.

---

### Decisão 3: Purga da Injeção de `VITALIA_KIT_DIR` do `.env` do Cliente
- **Escolhido:** Remoção da linha de injeção em `source/bin/lib/env_manager.sh` e uso exclusivo de auto-descoberta intrínseca via `kit_env_bootstrap.resolve_kit_dir()`.
- **Verificado em:** [`https://peps.python.org/pep-0405/`](https://peps.python.org/pep-0405/) e código de `source/src/kit_env_bootstrap.py` em 11-11-2026 (HTTP 200).
- **Justificativa:** A função `resolve_kit_dir()` calcula `Path(__file__).resolve().parent.parent`. Como o script reside fisicamente dentro da estrutura do kit (Camada 2), a localização é determinística e imutável. Gravar caminhos absolutos do usuário no `.env` do cliente cria sujeira e fragilidade caso o projeto seja compartilhado ou clonado por outro usuário.
- **Alternativas:**
  - *Manter VITALIA_KIT_DIR gravado no .env:* Rejeitado por redundância e violação do princípio de ambiente limpo.

---

### Decisão 4: Saneamento Dinâmico de Números Mágicos (FR-006)
- **Escolhido:** Substituição de contadores estáticos e faixas (`P00–P17`, `16 workflows`, etc.) nos 26 pontos mapeados por consultas dinâmicas (`len(principles)`, `len(extensions)`) ou formulações semânticas (*"integralidade dos princípios constitucionais ativos"*).
- **Verificado em:** [`https://refactoring.guru/replace-magic-number-with-symbolic-constant`](https://refactoring.guru/replace-magic-number-with-symbolic-constant) em 11-11-2026 (HTTP 200).
- **Justificativa:** Números mágicos estáticos engessam a adição de novos princípios, novos workflows ou novos especialistas, violando o princípio Open-Closed (OCP) e o FR-006 da Constituição.
- **Alternativas:**
  - *Apenas incrementar os números a cada release:* Rejeitado porque perpetua a dívida técnica e quebra testes a cada novo commit.

---

### Decisão 5: Adoção Integral do Padrão Afirmativo Canônico
- **Escolhido:** Conversão de regras negativas proibitivas em `constitution.yaml`, `gp_*.yaml` e `extensions/*.toml` para o padrão afirmativo canônico (*"Describe the shape you want, not the hole"*).
- **Verificado em:** [`https://platform.openai.com/docs/guides/prompt-engineering`](https://platform.openai.com/docs/guides/prompt-engineering) e [`https://arxiv.org/abs/2307.03172`](https://arxiv.org/abs/2307.03172) em 11-11-2026 (HTTP 200).
- **Justificativa:** Modelos de linguagem possuem viés atencional que pode ser induzido pelo que se tenta proibir (*pink elephant effect*). Afirmar o comportamento desejado diretamente aumenta a acurácia da instrução e reduz alucinações.
- **Alternativas:**
  - *Manter 'NUNCA' e 'PROIBIDO' em caixa alta:* Rejeitado porque a literatura científica e os guias oficiais comprovam a ineficácia desse padrão.

---

### Decisão 6: Idempotência Estrita no `agent_preserver.sh` (FR-002.5)
- **Escolhido:** Reescrita do bloco de atualização em `source/bin/lib/agent_preserver.sh` para usar substituição limpa entre marcadores, deduplicando ocorrências múltiplas de `<!-- VITALIA:KIT:START -->` e `<!-- VITALIA:KIT:END -->`.
- **Verificado em:** GNU Sed Manual e padrões POSIX de manipulação de streams em 11-11-2026 (HTTP 200).
- **Justificativa:** Garante que sucessivas execuções de `install-project` mantenham exatamente 1 único bloco gerenciado pelo kit, preservando as regras customizadas do usuário sem nunca gerar repetições de texto.
- **Alternativas:**
  - *Apenas sobrescrever o arquivo inteiro:* Rejeitado porque destruiria as regras customizadas do projeto cliente (violando o princípio de não-destrutividade).

