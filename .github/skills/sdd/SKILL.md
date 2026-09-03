---
name: "sdd"
description: "Metodologia Spec-Driven Development (SDD) — especificar antes de codificar. Use quando o usuário pedir para seguir o fluxo SDD (spec → plan → tasks → implementar → lessons learned), criar ou atualizar artefatos como spec.md, plan.md, tasks.md, constitution.md, project-context.md ou lessons-learned.md, ou quando invocar esta skill (sdd / SDD)."
compatibility: "Requer projeto versionado em git e convenção de artefatos SDD (openspec/ ou specs/ conforme o projeto)"
metadata:
  author: "github/spec-kit user"
  source: "SDD-SKILL.md"
---

# SDD — Spec Driven Development Skill

> **Versão:** 1.0  
> **Compatível com:** Claude Code · Trae IDE · VS Code + Codex · Cursor · Windsurf · OpenCode · Kilo Code  
> **Idioma dos artefatos:** Português (BR) ou Inglês — conforme convenção do projeto  

---

## 1. PRINCÍPIOS FUNDAMENTAIS DO SDD

### 1.1 O Paradigma

Spec Driven Development inverte a relação tradicional entre especificação e código:

- **Abordagem tradicional:** especificações servem ao código — são andaimes descartáveis.
- **Abordagem SDD:** o código serve à especificação — a spec é o artefato primário e a única fonte de verdade.

O código é o **resultado final** de uma cadeia de artefatos vivos. Manter um sistema significa evoluir suas especificações, não apenas patchar código.

### 1.2 Os Quatro Pilares

| Pilar | Descrição |
|---|---|
| **Especificação como artefato primário** | A spec define o que deve existir. Código é sua expressão em uma stack específica. |
| **Especificações executáveis** | Precisas o suficiente para gerar sistemas funcionais sem ambiguidade. |
| **Documentação dinâmica** | Depurar = corrigir a spec que gerou código errado. Refatorar = reestruturar a spec. |
| **Colaboração humano-IA** | A IA transforma specs em código; o humano garante a intenção e revisa os artefatos. |

### 1.3 Por Que SDD Agora

- **IAs ultrapassaram o limiar crítico:** specs em linguagem natural já geram código funcional de forma confiável.
- **Complexidade cresce exponencialmente:** múltiplos serviços, frameworks e dependências exigem alinhamento sistemático.
- **Ritmo de mudança acelera:** pivôs deixam de ser exceção. Alterar uma spec propaga a mudança sistematicamente — sem reescrita manual em cascata.

### 1.4 Filosofia OpenSpec Integrada

```
→ fluído, não rígido
→ iterativo, não waterfall
→ leve, não burocrático
→ brownfield-first — serve projetos existentes, não só novos
→ escalável — de projetos pessoais a enterprises
```

---

## 2. ESTRUTURA DE ARTEFATOS SDD

Cada feature ou mudança produz um conjunto de artefatos versionados junto ao código:

```
<raiz-do-projeto>/
├── openspec/                         ← ou .spec/, .github/specs/ — conforme convenção do projeto
│   ├── constitution.md               ← princípios globais imutáveis do projeto
│   ├── project-context.md            ← [SEÇÃO VARIÁVEL — ver Seção 6]
│   ├── lessons-learned.md            ← [SEÇÃO DE APRENDIZADO — ver Seção 7]
│   ├── specs/                        ← especificações por capacidade/domínio
│   │   ├── auth-login/
│   │   │   └── spec.md
│   │   └── checkout-cart/
│   │       └── spec.md
│   └── changes/                      ← mudanças em andamento
│       └── <id-da-mudanca>/
│           ├── proposal.md
│           ├── spec.md
│           ├── plan.md
│           └── tasks.md
└── src/                              ← código-fonte
```

> **Regra:** todos os artefatos SDD são versionados em git junto com o código. Eles são documentação viva — não são descartáveis.

---

## 3. FASE 1 — ESPECIFICAR (`spec.md`)

### 3.1 Quando Criar

Antes de escrever qualquer linha de código para uma feature, mudança ou correção significativa. A spec é o ponto de partida, não a documentação posterior.

### 3.2 Estrutura Obrigatória do `spec.md`

```markdown
# [Nome da Feature/Mudança]

## Resumo
<!-- Uma ou duas frases: O que esse recurso faz, da perspectiva do usuário final. -->

## Histórias de Usuário
<!-- Narrativas de como o usuário interage com o recurso. Captura intenção, não implementação. -->
- Como [tipo de usuário], quero [ação] para que [benefício].

## Critérios de Aceitação
<!-- Condições testáveis e observáveis que definem "pronto". Escreva como fatos. -->
- [ ] [Condição observável 1]
- [ ] [Condição observável 2]

## Requisitos Funcionais
<!-- Como o sistema se comporta: interfaces, processos, manipulação de dados. -->

## Requisitos Não-Funcionais
<!-- Atributos de qualidade: desempenho, segurança, escalabilidade, acessibilidade. -->

## Casos de Borda e Tratamento de Erros
<!-- Cenários incomuns, condições de falha, comportamentos de fronteira. -->

## Fora de Escopo
<!-- O que explicitamente NÃO será feito nesta iteração. -->

## Dependências
<!-- Outras specs, serviços externos, ou features que precisam existir primeiro. -->
```

### 3.3 Checklist de Qualidade da Spec

Antes de avançar para o plano, verifique:

- [ ] Alguém consegue ler a spec e entender exatamente o que construir, sem perguntar nada?
- [ ] Cada critério de aceitação é testável de forma objetiva?
- [ ] Casos de borda e erros estão documentados explicitamente?
- [ ] Os requisitos não-funcionais (performance, segurança) estão especificados com valores concretos?
- [ ] O que está fora do escopo está declarado?
- [ ] A spec está alinhada com a `constitution.md` do projeto?

### 3.4 Boas Práticas por Tipo de Requisito

**Requisitos Funcionais:**
- Use linguagem declarativa: "O sistema DEVE..." / "O usuário PODE..."
- Cada requisito = uma responsabilidade única (SRP na spec)
- Evite "e também" — se tem dois comportamentos, são dois requisitos

**Requisitos Não-Funcionais — Templates:**
```
Performance: P95 de resposta < 200ms para [operação X] com [N] usuários simultâneos
Segurança: Todas as [entradas do tipo Y] devem ser sanitizadas antes de [operação Z]
Disponibilidade: SLA de 99.9% excluindo janelas de manutenção programadas
Acessibilidade: Conformidade WCAG 2.1 nível AA para todos os componentes de UI
```

---

## 4. FASE 2 — PLANEJAR (`plan.md`)

### 4.1 Propósito

O plano transforma os **requisitos** da spec em **decisões técnicas**. Define *como* construir, não *o que* construir. Se a stack mudar, o plano muda — a spec permanece.

### 4.2 Estrutura Obrigatória do `plan.md`

```markdown
# Plano Técnico — [Nome da Feature]

## Visão Geral da Arquitetura
<!-- Diagrama textual ou diagrama Mermaid de como os componentes interagem. -->

## Stack e Decisões Técnicas
<!-- Tabela de decisões com justificativa. Cada decisão deve remeter a um requisito da spec. -->

| Decisão | Escolha | Justificativa | Requisito |
|---|---|---|---|
| ORM | Prisma | Tipagem forte, migrações automáticas | RF-03 |
| Cache | Redis | Latência <10ms, TTL configurável | RNF-01 |

## Sequência de Implementação
<!-- Ordem lógica que respeita dependências. Fundação antes de features. -->
1. [Fase Fundação] — Schema, modelos de dados, configuração base
2. [Fase Core] — Lógica de negócio principal
3. [Fase UI/API] — Interfaces e endpoints
4. [Fase Segurança] — Validações, autenticação, autorização
5. [Fase Testes] — Unitários, integração, E2E

## Verificação da Constituição
<!-- Confirme que cada princípio relevante da constitution.md está respeitado. -->
- [ ] Princípio X: atendido via [mecanismo Y]
- [ ] Princípio Z: atendido via [mecanismo W]

## Suposições e Questões Abertas
<!-- Decisões tomadas com informação incompleta e perguntas ainda não resolvidas. -->
```

### 4.3 Boas Práticas de Planejamento por Stack

#### Front-End
- Definir design system e biblioteca de componentes antes de planejar componentes individuais
- Especificar estado global vs. local vs. server state (React Query, Zustand, Redux, etc.)
- Definir estratégia de roteamento e code-splitting
- Planejar estratégia de erro boundaries e loading states
- Definir contratos de API (schema dos responses) antes de construir o cliente

#### Back-End
- Definir camadas de arquitetura (Controller → Service → Repository ou equivalente)
- Especificar padrões de tratamento de erro e formato de resposta de API
- Planejar estratégia de migrations e rollback de banco
- Definir contratos de autenticação/autorização antes de qualquer endpoint
- Especificar logging, métricas e tracing (observability)

#### Full-Stack
- Definir onde a fronteira de responsabilidade fica (o que é do cliente vs. servidor)
- Estabelecer o contrato de API como artefato compartilhado (OpenAPI/GraphQL schema)
- Planejar estratégia de SSR/SSG/CSR e suas implicações em cache e SEO
- Definir estratégia de autenticação end-to-end (JWT, sessions, OAuth)

---

## 5. FASE 3 — TAREFAS (`tasks.md`)

### 5.1 Propósito

Converte o plano em itens de trabalho discretos, acionáveis, testáveis e estimáveis.

### 5.2 Estrutura Obrigatória do `tasks.md`

```markdown
# Tarefas — [Nome da Feature]

## Critérios de Conclusão Global
<!-- A feature está PRONTA quando... -->

## Fase 1 — Fundação
- [ ] 1.1 [Tarefa específica com entrada, saída e critério de aceite claro]
- [ ] 1.2 ...

## Fase 2 — Funcionalidade Core
- [ ] 2.1 ...

## Fase 3 — Interface (UI/API)
- [ ] 3.1 ...

## Fase 4 — Segurança e Validação
- [ ] 4.1 ...

## Fase 5 — Testes
- [ ] 5.1 Testes unitários: [lista de unidades críticas]
- [ ] 5.2 Testes de integração: [lista de integrações críticas]
- [ ] 5.3 Testes E2E: [cenários dos critérios de aceitação]

## Dependências entre Tarefas
<!-- Grafo de dependências: "2.1 requer 1.3 concluída" -->
```

### 5.3 Anatomia de uma Boa Tarefa

Uma tarefa bem definida tem:
- **Entrada:** o que precisa existir para começar
- **Ação:** o que deve ser feito (verbo no infinitivo)
- **Saída:** o que deve existir ao terminar
- **Critério de aceite:** como verificar que está correto

**Exemplo ruim:** `Implementar autenticação`  
**Exemplo bom:** `Implementar endpoint POST /auth/login que valida credenciais no banco via bcrypt, gera JWT com expiração de 24h, e retorna 401 com mensagem genérica em caso de falha (sem revelar se email ou senha estão errados)`

### 5.4 Verificação Pré-Implementação

Antes de começar a implementar, cruzar:
- [ ] Cada critério de aceitação da spec tem ao menos uma tarefa correspondente?
- [ ] Cada tarefa referencia o plano (decisão técnica relevante)?
- [ ] A sequência respeita as dependências?
- [ ] Há tarefas de testes para cada comportamento crítico?

---

## 6. FASE 4 — IMPLEMENTAR

### 6.1 Loop de Implementação

```
Para cada tarefa em tasks.md:
  1. Leia a tarefa, a spec e as decisões do plan relevantes
  2. Implemente (manual, IA-assistida ou híbrido)
  3. Verifique: o código faz o que a spec requer?
  4. Execute os testes da tarefa
  5. Marque [ x ] na tarefa
  6. Se descobrir algo que muda o design → atualize spec/plan ANTES de continuar
```

### 6.2 Quando Voltar aos Artefatos

| Situação | Ação |
|---|---|
| Caso de borda não mapeado | Atualizar `spec.md`, depois `tasks.md` |
| Decisão técnica precisa mudar | Atualizar `plan.md`, verificar impacto em tasks |
| Requisito mudou | Atualizar `spec.md` → `plan.md` → `tasks.md` em cascata |
| Bug encontrado que não é da feature atual | Criar nova spec/mudança, não corrigir silenciosamente |

### 6.3 Práticas de Implementação por Stack

#### Front-End — React/Next.js/Vue
```
✓ Componente = UI + lógica de apresentação (sem lógica de negócio)
✓ Custom hooks para lógica reutilizável e state management
✓ Server components para dados estáticos / Client components para interatividade
✓ Error boundaries em cada feature boundary
✓ Loading/skeleton states para toda operação assíncrona
✓ Formulários: validação no cliente (UX) + validação no servidor (segurança)
✓ Acessibilidade: aria-labels, roles, foco gerenciado em modais
✓ Testes: React Testing Library (comportamento, não implementação)
```

#### Back-End — Node/Python/Java/Go
```
✓ Separação estrita: Controller (HTTP) → Service (negócio) → Repository (dados)
✓ Nunca expor stack traces em respostas de produção
✓ Validação de entrada no perímetro (antes de entrar na camada de serviço)
✓ Transações explícitas para operações que envolvem múltiplas escritas
✓ Idempotência em endpoints que modificam estado
✓ Retry com exponential backoff para chamadas externas
✓ Logs estruturados (JSON) com correlation ID
✓ Testes unitários para services; testes de integração para repositórios
```

#### APIs REST
```
✓ Recursos como substantivos, verbos via HTTP method
✓ Status codes semânticos: 200/201/204/400/401/403/404/409/422/500
✓ Respostas de erro padronizadas: { error: { code, message, details? } }
✓ Paginação consistente: cursor-based (escalável) ou offset (simples)
✓ Versionamento: /v1/, /v2/ ou header Accept-Version
✓ Rate limiting documentado nos headers de resposta
```

#### Banco de Dados
```
✓ Migrations versionadas, nunca alteração manual em produção
✓ Indexes para todos os campos usados em WHERE, JOIN, ORDER BY
✓ Soft delete (deleted_at) vs hard delete: definido na spec
✓ Constraints de integridade referencial no banco (não só na aplicação)
✓ Queries N+1: sempre revisar com query analyzer antes de PR
```

---

## 7. TESTES AUTOMATIZADOS

### 7.1 Pirâmide de Testes SDD

```
         /\
        /E2E\        ← Poucos, lentos, testam fluxos completos de critérios de aceitação
       /------\
      /Integração\   ← Médios, testam contratos entre camadas e com dependências reais
     /------------\
    /   Unitários   \ ← Muitos, rápidos, testam unidades isoladas de lógica
   /________________\
```

### 7.2 Mapeamento Spec → Teste

Cada **critério de aceitação** da spec deve ter ao menos um teste E2E ou de integração cobrindo-o.  
Cada **requisito funcional** deve ter testes unitários cobrindo os caminhos feliz e de erro.  
Cada **caso de borda** listado na spec deve ter um teste dedicado.

### 7.3 Padrões de Teste por Camada

#### Testes Unitários
```
// Padrão AAA — Arrange, Act, Assert
describe('[Unidade]', () => {
  it('deve [comportamento esperado] quando [condição]', () => {
    // Arrange: configurar estado e mocks
    // Act: executar a unidade sob teste
    // Assert: verificar resultado
  });
});
```

**O que mockar:** dependências externas (DB, APIs, clock, filesystem)  
**O que NÃO mockar:** lógica de negócio da própria unidade

#### Testes de Integração
- Usar banco de dados real (test container ou banco dedicado)
- Rodar migrations antes da suite
- Limpar dados entre testes (transação com rollback ou truncate)
- Testar contratos de API: status code, schema do response, headers

#### Testes E2E
- Cobrir os happy paths dos critérios de aceitação
- Cobrir os cenários de erro críticos (login inválido, permissão negada)
- Evitar testar detalhes de UI — testar comportamento do usuário
- Usar data-testid para seleção de elementos (não classes CSS)

### 7.4 Qualidade de Testes

```
✓ Nome do teste descreve o comportamento, não a implementação
✓ Teste falha por uma única razão
✓ Teste é determinístico (mesmo resultado toda vez)
✓ Teste não depende de ordem de execução
✓ Cobertura de branches, não apenas de linhas
✓ Testes de mutação para lógica crítica de negócio
```

### 7.5 CI/CD Integration

```yaml
# Pipeline mínimo SDD-compliant
stages:
  - lint:          # ESLint, Prettier, type-check
  - unit-tests:    # Rápidos, sem I/O externo
  - integration:   # Com banco, cache, etc. (test containers)
  - e2e:           # Ambiente staging-like
  - security-scan: # SAST, dependency audit
  - build:         # Artefato de produção
  - deploy:        # Somente se todos os stages passaram
```

---

## 8. CONSTITUTION.MD — PRINCÍPIOS GLOBAIS DO PROJETO

O `constitution.md` é o artefato de mais alta precedência. Todos os planos e specs são verificados contra ele.

### 8.1 Estrutura do `constitution.md`

```markdown
# Constitution — [Nome do Projeto]

## Padrões de Tecnologia
<!-- Linguagens, frameworks e serviços que DEVEM ser usados -->
<!-- Tecnologias que são PROIBIDAS e por quê -->

## Requisitos de Segurança
<!-- Regras de autenticação e autorização -->
<!-- Padrões de criptografia e hashing -->
<!-- Política de secrets (nunca em código, sempre em variáveis de ambiente) -->
<!-- Sanitização e validação de entrada -->

## Expectativas de Performance
<!-- Targets de latência P50/P95/P99 -->
<!-- Limites de uso de memória e CPU -->
<!-- Estratégia de cache e invalidação -->

## Convenções de Código
<!-- Nomenclatura: snake_case, camelCase, PascalCase — onde aplicar cada um -->
<!-- Estrutura de pastas e módulos -->
<!-- Padrões de arquitetura obrigatórios (ex: DDD, Clean Architecture) -->
<!-- Regras de PR: tamanho máximo, cobertura mínima de testes -->

## Observability
<!-- Formato de logs (estruturado JSON) -->
<!-- Métricas obrigatórias por tipo de serviço -->
<!-- Distributed tracing: correlation IDs -->

## Conformidade e Compliance
<!-- Regulações aplicáveis: LGPD, GDPR, PCI-DSS, etc. -->
<!-- Retenção de dados e política de privacidade -->
<!-- Auditoria de acesso a dados sensíveis -->

## Processo de Desenvolvimento
<!-- Fluxo de branches (GitFlow, trunk-based, etc.) -->
<!-- Política de code review -->
<!-- Critérios de definition of done -->
```

---

## 9. PROJECT CONTEXT — SEÇÃO VARIÁVEL POR PROJETO

> **⚠️ INSTRUÇÃO PARA A IDE/AGENTE DE IA:**  
> Esta seção deve ser preenchida pela IDE ou agente de IA com base na análise do projeto existente.  
> Execute o seguinte processo ao iniciar em um projeto existente:
>
> 1. **Analise a estrutura de pastas** e identifique os padrões de organização já estabelecidos
> 2. **Leia os arquivos de configuração** (`package.json`, `pyproject.toml`, `pom.xml`, `go.mod`, etc.) para identificar a stack real
> 3. **Examine exemplos de código existente** para extrair convenções de nomenclatura, padrões arquiteturais e estilo de código
> 4. **Verifique migrations e schemas** de banco para entender o modelo de dados
> 5. **Leia testes existentes** para entender o nível e estilo de cobertura atual
> 6. **Preencha as seções abaixo** com o que foi descoberto — não invente, só documente o que existe
> 7. **Mantenha este arquivo atualizado** sempre que um novo padrão for estabelecido no projeto

---

### 9.1 Identidade do Projeto

```markdown
## Identidade do Projeto
<!-- [IDE: preencha com nome, domínio e propósito do sistema] -->

**Nome:** ___
**Domínio:** ___
**Propósito:** ___
**Fase atual:** [ ] Greenfield  [ ] Crescimento  [ ] Maturidade  [ ] Legado
```

### 9.2 Stack Real em Uso

```markdown
## Stack Real em Uso
<!-- [IDE: liste apenas o que está efetivamente instalado e em uso] -->

**Runtime/Linguagem:** ___  (versão: ___)
**Framework principal:** ___  (versão: ___)
**Banco de dados:** ___  (versão: ___)
**ORM/Query builder:** ___
**Cache:** ___
**Fila de mensagens:** ___
**Autenticação:** ___
**Infra/Cloud:** ___
**CI/CD:** ___
**Monitoramento:** ___
```

### 9.3 Convenções de Código Estabelecidas

```markdown
## Convenções Estabelecidas no Projeto
<!-- [IDE: extraia do código existente, não presuma] -->

**Nomenclatura de arquivos:** ___  (ex: kebab-case, PascalCase)
**Nomenclatura de variáveis:** ___
**Nomenclatura de funções/métodos:** ___
**Nomenclatura de classes:** ___
**Estrutura de pastas:** ___
**Padrão de imports:** ___  (ex: absolutos via @/, relativos, barrel files)
**Formatação:** ___  (Prettier/ESLint config — resumo das regras principais)
```

### 9.4 Padrões Arquiteturais do Projeto

```markdown
## Padrões Arquiteturais Identificados
<!-- [IDE: descreva o que existe, não o que seria ideal] -->

**Padrão geral:** ___  (ex: MVC, Hexagonal, Feature-based, etc.)
**State management (front):** ___
**Padrão de API:** ___  (REST/GraphQL/tRPC e convenções específicas)
**Padrão de autenticação:** ___
**Padrão de testes:** ___  (ferramentas e estrutura dos testes existentes)
**Tratamento de erros:** ___  (padrão atual de propagação e resposta)
```

### 9.5 Modelos de Dados Principais

```markdown
## Modelos de Dados Principais
<!-- [IDE: liste as entidades principais com campos críticos] -->

| Entidade | Campos-chave | Relacionamentos | Observações |
|---|---|---|---|
| ___ | ___ | ___ | ___ |
```

### 9.6 Integrações e Serviços Externos

```markdown
## Integrações Externas
<!-- [IDE: liste apenas as que já existem no projeto] -->

| Serviço | Propósito | Autenticação | SDK/Client usado |
|---|---|---|---|
| ___ | ___ | ___ | ___ |
```

### 9.7 Áreas de Atenção e Dívida Técnica Conhecida

```markdown
## Áreas de Atenção
<!-- [IDE: identifique code smells, TODOs, FIXMEs e dívida técnica óbvia] -->
<!-- Não julgue — apenas documente para que futuros trabalhos considerem -->

- ___
```

---

## 10. LESSONS LEARNED — MEMÓRIA DE APRENDIZADO DO PROJETO

> **⚠️ INSTRUÇÃO PARA A IDE/AGENTE DE IA — LEIA COM ATENÇÃO:**
>
> Esta seção funciona como **aprendizado por reforço** do projeto. É a memória persistente de decisões que funcionaram e de armadilhas que devem ser evitadas.
>
> ### Quando atualizar este arquivo:
> 1. **Após resolver um bug não-trivial** — especialmente se a causa-raiz foi uma suposição errada
> 2. **Após reverter uma decisão técnica** — documente por que a decisão original falhou
> 3. **Ao estabelecer um novo padrão** — para que não seja reinventado em cada PR
> 4. **Ao encontrar uma abordagem claramente superior** à que estava sendo usada
> 5. **Ao identificar um anti-padrão recorrente** que continua aparecendo no código
>
> ### Como atualizar:
> - Adicione a nova lição no topo da categoria relevante (mais recente primeiro)
> - Nunca remova lições — elas documentam a história de decisões do projeto
> - Se uma lição for superada por outra, marque a antiga com `[SUPERADA por #N]`
> - Use datas para rastreabilidade
> - Seja específico: cite arquivos, funções ou padrões reais quando aplicável
>
> ### Como usar ao implementar:
> - **Antes de iniciar qualquer implementação**, leia as lições da categoria relevante
> - **Antes de criar um novo padrão**, verifique se já existe uma lição sobre o tema
> - **Se repetir um erro já documentado**, adicione uma nota na lição indicando a recorrência

---

### 10.1 ✅ Padrões que Funcionam

```markdown
<!-- [IDE: adicione aqui abordagens que provaram ser eficazes neste projeto] -->
<!-- Formato: Data | Contexto | O que funcionou | Por que funcionou -->

- ___
```

### 10.2 ❌ Anti-Padrões — Não Repetir

```markdown
<!-- [IDE: adicione aqui abordagens que causaram problemas] -->
<!-- Formato: Data | Contexto | O que não funcionou | Por que falhou | Alternativa correta -->

- ___
```

### 10.3 🔄 Decisões Revertidas

```markdown
<!-- [IDE: documente decisões que foram tomadas e depois desfeitas] -->
<!-- Formato: Data | Decisão original | Motivo da reversão | Nova decisão -->

- ___
```

### 10.4 ⚡ Armadilhas de Performance

```markdown
<!-- [IDE: documente gargalos encontrados e como foram resolvidos] -->
<!-- Formato: Data | Operação problemática | Causa | Solução | Ganho medido -->

- ___
```

### 10.5 🔒 Lições de Segurança

```markdown
<!-- [IDE: documente vulnerabilidades encontradas/evitadas e como foram tratadas] -->
<!-- Formato: Data | Risco | Como foi identificado | Mitigação aplicada -->

- ___
```

### 10.6 🧪 Lições de Testes

```markdown
<!-- [IDE: documente aprendizados sobre estratégia de testes neste projeto] -->
<!-- Ex: "Mocks de X sempre precisam ser resetados entre testes — causa falsos positivos" -->

- ___
```

### 10.7 🤝 Lições de Integração

```markdown
<!-- [IDE: documente comportamentos inesperados de APIs externas, bancos, etc.] -->

- ___
```

---

## 11. COMANDOS DE REFERÊNCIA RÁPIDA

### 11.1 Fluxo para Feature Nova (Greenfield ou Brownfield)

```bash
# 1. Criar estrutura da mudança
mkdir -p openspec/changes/<id-da-feature>

# 2. Criar spec
# → Arquivo: openspec/changes/<id>/spec.md
# → Revisar contra constitution.md

# 3. Criar plano
# → Arquivo: openspec/changes/<id>/plan.md
# → Verificar alinhamento com spec e constitution

# 4. Criar tasks
# → Arquivo: openspec/changes/<id>/tasks.md
# → Verificar cobertura 100% dos critérios de aceitação

# 5. Implementar task por task
# → Marcar [x] ao concluir cada tarefa
# → Atualizar spec/plan se descobertas mudarem o design

# 6. Ao concluir: mover spec para openspec/specs/<dominio>/
cp openspec/changes/<id>/spec.md openspec/specs/<dominio>/spec.md
# → Atualizar lessons-learned.md com aprendizados
# → Arquivar ou deletar a pasta changes/<id>
```

### 11.2 Fluxo para Mudança em Feature Existente

```bash
# 1. Ler a spec existente em openspec/specs/<dominio>/
# 2. Criar openspec/changes/<id>/proposal.md descrevendo o delta
# 3. Criar spec delta (o que muda na spec existente)
# 4. Criar plan.md focado na mudança
# 5. Criar tasks.md
# 6. Implementar
# 7. Atualizar a spec original com o delta aprovado
# 8. Atualizar lessons-learned.md
```

### 11.3 Checklist Final de PR

```markdown
## Checklist SDD para Pull Request

### Artefatos
- [ ] `spec.md` atualizado e reflete o estado final implementado
- [ ] `plan.md` reflete as decisões técnicas reais (não o planejamento original que pode ter mudado)
- [ ] `tasks.md` com todas as tarefas marcadas como concluídas
- [ ] `constitution.md` não foi violada (ou foi atualizada com aprovação explícita)
- [ ] `lessons-learned.md` atualizado com aprendizados desta feature (se houver)

### Código
- [ ] Testes unitários para lógica nova
- [ ] Testes de integração para contratos de API novos ou alterados
- [ ] Testes E2E para critérios de aceitação da spec
- [ ] Cobertura de testes atende ao threshold definido na constitution
- [ ] Sem segredos, credenciais ou dados sensíveis no código
- [ ] Logs estruturados adicionados para operações críticas
- [ ] Migrations são reversíveis (down migration)

### Revisão
- [ ] O código implementa o que a spec descreve — não mais, não menos
- [ ] As decisões do plano foram seguidas (ou o plano foi atualizado com justificativa)
- [ ] Casos de borda da spec têm testes correspondentes
```

---

## 12. ANTI-PADRÕES SDD — NÃO FAÇA

| Anti-padrão | Por que é problemático | O que fazer em vez disso |
|---|---|---|
| Vibe-coding sem spec | Cada sessão de chat opera isolada, sem contexto de decisões anteriores | Criar spec antes de codificar |
| Spec como documentação posterior | A spec perde seu papel de guia de implementação | Spec é o ponto de partida, não o ponto final |
| Atualizar código sem atualizar spec | Spec diverge da realidade — perde confiabilidade | Propagar mudanças: spec → plan → tasks → código |
| Tarefas muito grandes | Impossível verificar conclusão; IA perde contexto | Quebrar em tarefas de <4h de trabalho |
| Ignorar constitution.md | Inconsistência sistêmica entre features | Verificar constitution em cada plan |
| Spec ambígua ("o sistema deve ser rápido") | IA interpreta de forma imprevisível | Valores concretos e mensuráveis nos RNFs |
| Lessons learned vazio | Repete os mesmos erros indefinidamente | Atualizar a cada bug não-trivial ou decisão revertida |
| Spec = código | Specs em pseudocódigo ou linguagem técnica eliminam o papel de comunicação com stakeholders | Specs em linguagem natural estruturada |

---

## 13. REFERÊNCIAS E FRAMEWORKS BASE

Esta skill foi construída sintetizando:

- **GitHub Spec Kit** (Microsoft/GitHub) — Metodologia SDD com fases Especificar → Planejar → Tarefas → Implementar e artefatos `constitution.md`, `spec.md`, `plan.md`, `tasks.md`
- **OpenSpec** (Fission-AI) — Framework open-source de SDD com foco em brownfield, fluido e sem phase gates rígidos; filosofia de specs como contexto persistente no repositório
- **Melhores práticas de engenharia de software** — Clean Architecture, Test Pyramid, Continuous Integration, OpenAPI, WCAG, OWASP

---

*Este arquivo é um artefato vivo. Atualize-o sempre que descobrir melhores práticas aplicáveis ao seu contexto de projeto.*

---

## Convenção de Artefatos neste Projeto (projeto01)

> **⚠️ ADAPTAÇÃO LOCAL — definida em 2026-09-02.**
> Este projeto usa o **GitHub Spec Kit** como executor do fluxo SDD. Portanto, a estrutura de artefatos da
> Seção 2 deve ser interpretada conforme a convenção abaixo (não criar uma árvore `openspec/` paralela):

```
projeto01/
├── .specify/                         ← config, scripts, templates, workflows (Spec Kit)
│   ├── memory/constitution.md        ← princípios do projeto (ver Seção 8)
│   ├── memory/project-context.md     ← contexto variável por projeto (ver Seção 9)
│   └── memory/lessons-learned.md     ← aprendizado do projeto (ver Seção 10)
├── specs/                            ← specs por feature (Spec Kit)
│   └── <NNN>-<nome>/spec.md          ← + plan.md e tasks.md gerados pelo Spec Kit
└── .github/skills/                   ← skills do agente (speckit-*, sdd)
```

**Como usar junto com o Spec Kit:**
- Prefira os comandos `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`,
  `/speckit-implement` e `/speckit-converge` para gerar e atualizar `spec.md`, `plan.md` e `tasks.md`.
- Aplique os **checklists e padrões de qualidade das Seções 3.3, 5.3, 7 e 11.3** desta skill ao revisar
  os artefatos gerados pelo Spec Kit.
- Mantenha `lessons-learned.md` e `project-context.md` sob `.specify/memory/` conforme as Seções 9 e 10.
- Se o usuário pedir explicitamente o fluxo manual SDD/OpenSpec (sem o Spec Kit), use a estrutura
  `openspec/` da Seção 2.
