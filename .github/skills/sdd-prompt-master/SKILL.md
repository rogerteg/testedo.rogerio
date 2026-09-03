---
name: "sdd-prompt-master"
description: "Master prompts de início de sessão SDD (Spec-Driven Development). Use quando o usuário quiser iniciar uma sessão de desenvolvimento de feature nova a partir de PRD (Modo 1), alterar módulo existente (Modo 2), iniciar projeto greenfield (Modo 3), retomar uma sessão em andamento, ou pedir o template de contexto de sessão SDD. Complementa a skill sdd (SDD-SKILL.md)."
compatibility: "Requer projeto versionado em git e convenção de artefatos SDD (openspec/ ou specs/ conforme o projeto)"
metadata:
  author: "github/spec-kit user"
  source: "SDD-PROMPT-MASTER.md"
---

# SDD Master Prompt — Início de Sessão de Desenvolvimento

> **Como usar:** Copie o bloco abaixo, preencha as seções marcadas com `[...]` e cole como primeira mensagem para o agente de IA na IDE (Trae, VS Code + Codex, Claude Code, Cursor, etc.).  
> Escolha o **Modo** que corresponde à sua situação atual.

---

## ════════════════════════════════════════
## MODO 1 — Feature Nova a partir de PRD
## ════════════════════════════════════════

```
## CONTEXTO DA SESSÃO — SDD Mode

Leia o arquivo `SDD-SKILL.md` antes de qualquer ação.
Em seguida, leia o `constitution.md` do projeto (se existir).
Em seguida, leia o `project-context.md` e o `lessons-learned.md` (se existirem).

---

### Situação
Vou iniciar o desenvolvimento de uma feature nova derivada de um PRD existente.

### Referência no PRD
[Informe: nome do arquivo PRD / link / seção / Sprint / ID da história de usuário]
Exemplo: "PRD_Sistema_Financeiro.md — Sprint 2 — US-07: Emissão de boleto bancário"

### Objetivo desta sessão
[Descreva em 1–3 frases o que deve estar funcionando ao final da sessão]
Exemplo: "Ao final, o endpoint POST /invoices deve gerar um boleto via API Gerencianet, 
persistir no banco e retornar o PDF em base64."

### Escopo desta sessão
[O que está DENTRO do escopo hoje]
- ...

[O que está FORA do escopo hoje — será feito em outra sessão]
- ...

### Ponto de partida
[ ] Greenfield — nenhum código existe ainda para esta feature
[ ] Existe código parcial em: [informe o caminho, ex: src/modules/invoices/]
[ ] Existe uma spec anterior em: [informe o caminho]

---

### Instrução para o agente

**Passo 1 — Contexto do projeto**
Se o `project-context.md` não existir ou estiver incompleto, analise o projeto e preencha 
a Seção 9 do SDD-SKILL.md antes de prosseguir.

**Passo 2 — Criar a spec**
Com base na referência do PRD indicada acima e no objetivo desta sessão, crie:
`openspec/changes/[id-curto-da-feature]/spec.md`

A spec deve incluir:
- Origem: referência ao PRD (Sprint/US/seção)
- Resumo técnico da feature
- Histórias de usuário refinadas (com detalhes técnicos)
- Critérios de aceitação testáveis e objetivos
- Requisitos funcionais com nível de detalhe suficiente para implementação
- Requisitos não-funcionais com valores concretos (latência, limites, etc.)
- Casos de borda e tratamento de erros
- O que está fora do escopo

Apresente a spec para minha revisão ANTES de avançar para o plano.

**Passo 3 — Aguardar aprovação**
Só avance para o plan.md após eu confirmar que a spec está correta.

**Passo 4 — Criar o plano**
Crie `openspec/changes/[id]/plan.md` com:
- Arquitetura da solução alinhada à constitution.md e ao project-context.md
- Decisões técnicas com justificativa e referência ao requisito da spec
- Sequência de implementação (Foundation → Core → API/UI → Segurança → Testes)
- Verificação da constitution
- Suposições e questões abertas

Apresente o plano para minha revisão ANTES de avançar para as tarefas.

**Passo 5 — Criar tasks**
Crie `openspec/changes/[id]/tasks.md` com tarefas específicas, executáveis e testáveis.
Cada tarefa deve ter critério de aceite claro.
Verifique que 100% dos critérios de aceitação da spec têm ao menos uma tarefa correspondente.

Apresente as tasks para minha revisão ANTES de implementar.

**Passo 6 — Implementar**
Implemente tarefa por tarefa, marcando [x] ao concluir cada uma.
Se descobrir algo que mude o design, PARE e informe antes de continuar.
Ao final, atualize o `lessons-learned.md` com qualquer aprendizado relevante.
```

---

## ════════════════════════════════════════
## MODO 2 — Alteração em Módulo Existente
## ════════════════════════════════════════

```
## CONTEXTO DA SESSÃO — SDD Mode (Brownfield Change)

Leia o arquivo `SDD-SKILL.md` antes de qualquer ação.
Em seguida, leia o `constitution.md`, `project-context.md` e `lessons-learned.md`.

---

### Situação
Vou alterar um módulo/feature que já existe no projeto.

### Módulo/Feature alvo
[Informe o nome do módulo e o caminho no código]
Exemplo: "Módulo de autenticação — src/modules/auth/"

### Spec existente (se houver)
[Informe o caminho da spec atual, ou "não existe spec documentada"]
Exemplo: "openspec/specs/auth/spec.md"

### O que precisa mudar
[Descreva claramente a mudança desejada — pode ser baseado no PRD, em um bug, em feedback]
Exemplo: "Adicionar suporte a 2FA via TOTP. O PRD está em docs/PRD_Auth_v2.md, seção 4.3."

### Motivação
[ ] Nova funcionalidade do PRD — Referência: [seção/US]
[ ] Correção de bug — Descrição: [descreva o bug]
[ ] Refatoração / melhoria técnica — Objetivo: [descreva]
[ ] Requisito regulatório/segurança — Detalhes: [descreva]

### Restrições da mudança
[O que NÃO pode ser quebrado / qual é o impacto aceitável em outras partes]
Exemplo: "Sessões existentes não podem ser invalidadas. API de login deve manter o mesmo contrato."

---

### Instrução para o agente

**Passo 1 — Leitura do estado atual**
Leia a spec existente (se houver), o código do módulo alvo e os testes existentes.
Identifique o que existe atualmente vs. o que precisa mudar.
Verifique o `lessons-learned.md` por lições relevantes ao módulo ou tipo de mudança.

**Passo 2 — Criar o proposal**
Crie `openspec/changes/[id-curto]/proposal.md` com:
- Estado atual: o que existe hoje
- Estado desejado: o que deve existir após a mudança
- Delta de requisitos: o que muda na spec (não reescreva tudo — só o delta)
- Riscos e impactos em outras partes do sistema
- Critérios de aceitação da mudança

Apresente o proposal para minha revisão ANTES de avançar.

**Passo 3 — Aguardar aprovação**
Só avance após eu confirmar o proposal.

**Passo 4 — Criar plan.md e tasks.md**
Focados apenas no delta — não replaneje o que já existe e funciona.
Inclua obrigatoriamente tarefas de testes de regressão para o que pode ter sido impactado.

Apresente para revisão ANTES de implementar.

**Passo 5 — Implementar**
Tarefa por tarefa. Se descobrir dependências ocultas ou impactos não previstos, PARE e informe.

**Passo 6 — Atualizar artefatos**
- Atualize a spec original em `openspec/specs/[dominio]/spec.md` com o delta aprovado
- Atualize `lessons-learned.md` com qualquer aprendizado da mudança
```

---

## ════════════════════════════════════════
## MODO 3 — Início de Projeto Greenfield
## ════════════════════════════════════════

```
## CONTEXTO DA SESSÃO — SDD Mode (Greenfield)

Leia o arquivo `SDD-SKILL.md` antes de qualquer ação.

---

### Situação
Estou iniciando um projeto do zero.

### Descrição do sistema
[Descreva o sistema em 3–5 frases: o que faz, para quem, qual o problema que resolve]

### Referência de requisitos
[ ] Tenho um PRD em: [caminho/link]
[ ] Tenho uma descrição informal — vou descrever aqui:
    [Descreva os requisitos iniciais]
[ ] Ainda não tenho requisitos — quero que o agente me ajude a elaborá-los

### Stack desejada (se já decidida)
- Front-end: [ou "a definir"]
- Back-end: [ou "a definir"]
- Banco: [ou "a definir"]
- Infra: [ou "a definir"]

### Restrições conhecidas
[Performance, segurança, budget, prazo, regulações, etc.]

---

### Instrução para o agente

**Passo 1 — Constitution**
Com base na descrição e stack fornecidas, proponha um `constitution.md` para o projeto.
Aguarde minha aprovação antes de avançar.

**Passo 2 — Project Context**
Preencha a Seção 9 do SDD-SKILL.md (project-context.md) com a stack e convenções decididas.

**Passo 3 — Primeira Spec**
Identifique qual é o núcleo mínimo do sistema (a feature mais fundamental).
Crie a spec para essa feature primeiro.
Siga o fluxo: spec → plan → tasks → implementação.

**Regra para este projeto:**
A cada nova feature, sempre criar spec → plan → tasks antes de qualquer código.
```

---

## ════════════════════════════════════════
## COMPLEMENTO — Retomada de Sessão
## ════════════════════════════════════════

> Use este bloco quando retomar o trabalho em uma sessão já iniciada anteriormente.

```
## RETOMADA DE SESSÃO — SDD Mode

Leia o arquivo `SDD-SKILL.md` antes de qualquer ação.
Em seguida, leia `constitution.md`, `project-context.md` e `lessons-learned.md`.

### Feature/mudança em andamento
[Informe o ID e nome]
Exemplo: "openspec/changes/invoice-generation/"

### Estado dos artefatos
- spec.md: [ ] aprovada  [ ] em revisão
- plan.md: [ ] aprovado  [ ] em revisão  [ ] não criado
- tasks.md: [ ] criado   [ ] não criado

### Última tarefa concluída
[Informe o número e descrição da última tarefa que foi marcada como concluída]
Exemplo: "Tarefa 2.3 — Service de validação de dados do boleto"

### Próximo passo esperado
[O que você quer fazer nesta sessão]
Exemplo: "Continuar a partir da tarefa 2.4"

### Observações
[Qualquer contexto relevante sobre o estado atual — problemas encontrados, decisões tomadas, etc.]

---

### Instrução para o agente
Leia os artefatos da feature em andamento.
Confirme o estado atual antes de agir.
Retome pelo próximo passo indicado, verificando consistência com spec e plan.
```

---

## Notas de Uso

### Regras que o agente deve sempre seguir durante a sessão:
1. **Nunca avançar de fase sem aprovação** — spec → plano → tasks → código são checkpoints
2. **Nunca alterar código silenciosamente** — se uma descoberta muda o design, informar antes de agir
3. **Consultar lessons-learned antes de implementar** qualquer padrão novo para este projeto
4. **Atualizar lessons-learned ao final** da sessão se houver aprendizados

### Onde colocar o PRD e outros documentos de requisitos:
- PRDs, roadmaps, documentos de negócio → `docs/` ou onde já estão (Notion, Confluence, etc.)
- A `spec.md` de cada feature **referencia** o PRD mas não o substitui
- Formato de referência na spec: `## Origem: [nome do arquivo] — [seção/Sprint/US-ID]`

### Hierarquia de precedência dos artefatos:
```
constitution.md        ← máxima precedência — nunca violar
  ↓
project-context.md     ← padrões do projeto — seguir sempre
  ↓
lessons-learned.md     ← consultar antes, atualizar depois
  ↓
spec.md (feature)      ← o que construir
  ↓
plan.md                ← como construir
  ↓
tasks.md               ← o que fazer agora
  ↓
código                 ← resultado final
```

---

## Convenção neste Projeto (projeto01)

> **⚠️ ADAPTAÇÃO LOCAL — definida em 2026-09-02.**
> Este projeto executa o fluxo SDD com o **GitHub Spec Kit**. Ao usar os templates acima nesta sessão:
>
> - **Leia primeiro** a skill `sdd` (`.github/skills/sdd/SKILL.md`) e sua nota de adaptação local.
> - **Prefira os comandos `/speckit-*`** (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`,
>   `/speckit-implement`, `/speckit-converge`) para criar e evoluir `spec.md`, `plan.md` e `tasks.md`
>   em `specs/<NNN>-<nome>/` — em vez de criar a árvore `openspec/changes/` manualmente.
> - **Artefatos de memória** (`constitution.md`, `project-context.md`, `lessons-learned.md`) vivem em
>   `.specify/memory/` (não em `openspec/`).
> - Os **checkpoints com aprovação** (spec → plan → tasks → código) e as **regras das "Notas de Uso"**
>   continuam valendo; aplique-os aos artefatos gerados pelo Spec Kit.
> - Se o usuário pedir explicitamente o fluxo manual OpenSpec (sem o Spec Kit), use os caminhos
>   `openspec/changes/<id>/...` conforme os templates acima.
