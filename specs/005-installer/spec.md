# Feature Specification: Instalador Próprio do Automatic1 (cliente)

**Feature Branch**: `005-installer`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Etapa 4 — instalador próprio do Automatic1". As features `001`–`004` catalogam setups, registram máquinas/execuções e provisionam assets `.sh` remotos. Esta feature cria o **instalador cliente do Automatic1** para uma **VPS Debian 11/12 limpa**: bootstrap **idempotente** da infraestrutura base (Docker, Docker Swarm, Traefik, Portainer, Postgres, MongoDB, Redis) e **instalação das aplicações do catálogo** por scripts instaladores próprios por ferramenta — orquestrado pelo catálogo, análogo ao `SetupFrancisMno` (`install.sh` + `*.sh`), mas **versionado, sem segredos e dirigido pelo registro**. *Obs.: muda o default da constituição (PowerShell) para bash/Debian — exceção justificada e registrada.*

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fazer bootstrap da infraestrutura base numa VPS limpa (Priority: P1)

Um operador, numa **VPS Debian 11/12 recém-criada**, executa o instalador do Automatic1 e obtém a **infraestrutura base pronta**: Docker + Docker Swarm (modo cluster), Traefik (proxy/TLS) e Portainer (gerenciador), além dos serviços de apoio (Postgres, MongoDB, Redis). O processo é **reproduzível, idempotente e sem passos interativos obrigatórios** (constituição I/V).

**Why this priority**: É a metade "base" do instalador e o pré-requisito de tudo o que roda no host.

**Independent Test**: Pode ser testado isoladamente (ex.: VPS/contêiner Debian de teste): após rodar o bootstrap duas vezes, a infra base está ativa e **sem efeitos duplicados** (idempotente); o resultado é reportado com clareza.

**Acceptance Scenarios**:

1. **Given** uma VPS Debian 11/12 limpa, **When** o operador executa o bootstrap, **Then** Docker + Swarm + Traefik + Portainer (+ serviços de apoio) ficam ativos e são verificados.
2. **Given** o bootstrap já executado, **When** ele roda de novo, **Then** é **idempotente** — não duplica serviços nem quebra o estado existente.
3. **Given** uma falha (ex.: sem privilégio, porta ocupada), **When** ela ocorre, **Then** o instalador reporta erro claro e acionável com código de saída distinto de zero.
4. **Given** a execução do instalador, **When** termina, **Then** nenhum segredo/credencial é gerado, exigido ou persistido sem o operador decidir (constituição IV).

---

### User Story 2 - Instalar aplicações do catálogo via scripts instaladores próprios (Priority: P1)

Um operador instala **aplicações do catálogo** (ex.: Chatwoot, Evolution API, Typebot, N8N…) num host com a infra base pronta, por meio de **scripts instaladores próprios do Automatic1** (um por ferramenta), idempotentes, configuráveis e com verificação de versão/integridade quando disponível. O catálogo (`002`) passa a referenciar esses scripts como origem (`origem_asset`), destravando o provisionador (`004`).

**Why this priority**: É a metade "aplicações"; sem scripts instaladores próprios os itens padrão não são executáveis (`004` os bloqueia).

**Independent Test**: Pode ser testado isoladamente: instalar uma aplicação de exemplo duas vezes no host de teste → ativa, idempotente, sem duplicar.

**Acceptance Scenarios**:

1. **Given** infra base pronta e uma aplicação do catálogo, **When** o operador instala, **Then** a aplicação fica ativa (acessível via Traefik) e o script reporta sucesso.
2. **Given** a instalação repetida, **When** roda de novo, **Then** é idempotente (nada duplica).
3. **Given** configuração incompleta (ex.: domínio/porta), **When** o instalador roda, **Then** erro claro aponta o que falta; nenhuma mudança parcial destrutiva.
4. **Given** cada script instalador, **When** adotado no catálogo, **Then** `origem_asset`/versão/hash são atualizados para referenciá-lo (rastreabilidade).

---

### User Story 3 - Instalar de forma dirigida pelo catálogo e auditável (Priority: P2)

O instalador é **gerado/orquestrado a partir do catálogo/registro** (e não de scripts soltos): o operador escolhe o que instalar (infra + apps) e o instalador consome a definição do catálogo (nome, origem, versão, pré-requisitos), produzindo um **manifesto do que foi instalado** (versões, serviços, URLs) para conferência/auditoria.

**Why this priority**: Garante rastreabilidade e consistência com o Admin (o "instalador dirigido pelo catálogo" do roadmap); complementa US1/US2.

**Independent Test**: Pode ser testado isoladamente: instalar um conjunto escolhido e conferir o manifesto gerado (versões/serviços) — sem depender do Admin.

**Acceptance Scenarios**:

1. **Given** uma escolha de apps no instalador, **When** o operador instala, **Then** o instalador usa as definições do catálogo (origem/versão) para cada item.
2. **Given** a instalação concluída, **When** o operador consulta o resultado, **Then** um manifesto lista o que foi instalado (serviço, versão, URL) de forma legível e auditável.
3. **Given** um item do catálogo marcado como não instalável nesta etapa, **When** o operador o escolhe, **Then** o instalador informa e segue (sem quebrar).

---

### Edge Cases

- VPS sem privilégios/sudo → erro claro.
- Portas em uso (80/443) → diagnóstico acionável.
- Reexecução em host já provisionado → idempotente, sem duplicar (bootstrap + apps).
- Aplicação já instalada e reinstalada → atualiza sem quebrar (idempotência).
- Segredo/credencial acidental em config/script → nunca persistido/logado (anti-segredo; FR-013).
- Item do catálogo sem script instalador próprio ainda → informado, não bloqueia o resto.
- Download/falha de rede na instalação → erro claro + estado consistente (reenviável).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um **instalador cliente** executável numa VPS Debian 11/12 limpa que faça o **bootstrap idempotente** da infraestrutura base (Docker, Docker Swarm, Traefik, Portainer, Postgres, MongoDB, Redis) e instale **aplicações do catálogo** (Q1=A). Entrega: **scripts versionados no repo do Automatic1** (`install.sh` de entrada + `lib/common.sh` + `bootstrap.sh` + scripts por ferramenta em `apps/`), executados no VPS pelo operador (pull).
- **FR-002**: Cada ferramenta (infra e app) DEVE ter um **script instalador próprio do Automatic1** — idempotente, sem passos interativos obrigatórios, sem segredos embutidos, com saída clara e exit codes distintos (Q2=A). O Automatic1 passa a **possuir scripts instaladores próprios por ferramenta** (código no repo, revisado); a adoção é **incremental** (nem todas as ferramentas na primeira entrega) e, quando adotada, o catálogo/`origem_asset` passa a referenciá-los (quando hospedados).
- **FR-003**: O instalador DEVE ser **dirigido pelo catálogo**: consome nome/origem/versão/pré-requisitos dos setups e produz um **manifesto** do que foi instalado (serviço, versão, URL) para auditoria.
- **FR-004**: O instalador NÃO DEVE exigir nem persistir segredos embutidos; configuração sensível via **variáveis de ambiente/arquivo de config** (constituição IV).
- **FR-005**: A instalação DEVE ser **idempotente e reproduzível**; falhas reportam erro claro com código de saída e estado consistente (reenviável).
- **FR-006**: O catálogo (`002`) DEVE referenciar os scripts instaladores próprios como `origem_asset` (rastreabilidade/versão/hash) quando adotados.
- **FR-007**: O instalador DEVE executar **sem passos interativos obrigatórios** — **headless com arquivo de configuração + variáveis de ambiente** e defaults seguros (Q3=A). Menu interativo é opcional/extra.

### Key Entities *(include if feature involves data)*

- **Script Instalador (novo)**: por ferramenta (infra/app) — idempotente, versionado, sem segredos. Referenciado pelo catálogo como `origem_asset`.
- **Setup de Ambiente / Catálogo (`002`)**: fonte da definição (nome/origem/versão/pré-requisitos) consumida pelo instalador.
- **Manifesto de instalação (saída)**: relatório legível/auditável do que foi instalado (serviço, versão, URL) — não é entidade persistida no v1.
- **Bootstrap (infra base)**: Docker + Swarm + Traefik + Portainer + Postgres + MongoDB + Redis — como um "super-setup" idempotente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em uma VPS Debian 11/12 limpa, o bootstrap da infra base termina com sucesso em menos de 15 minutos (uma execução).
- **SC-002**: Executar bootstrap e/ou instalar qualquer app **duas vezes** produz 0 efeitos duplicados/destrutivos (idempotente).
- **SC-003**: 100% dos scripts instaladores executam sem passos interativos obrigatórios (headless) e com exit codes distintos (0 sucesso / ≠0 erro claro).
- **SC-004**: Auditoria por amostragem não encontra segredo embutido/gerado sem decisão em scripts/config/manifesto.
- **SC-005**: Instalar um conjunto de apps escolhido gera um manifesto legível listando serviço/versão/URL de cada item.
- **SC-006**: 100% das falhas (privilégio, porta ocupada, config incompleta, rede) reportam erro acionável sem deixar estado inconsistente irreversível.

## Assumptions

- **Ambiente-alvo**: Debian 11/12 + Docker Swarm (decisões já tomadas). Esta feature muda o default de runtime da constituição (PowerShell) para **bash/Debian** — exceção justificada e registrada (o produto provisiona hosts Linux).
- Instalador executado **no host** (pull pelo operador) ou via provisionador `004` (push) — integração a definir no plano.
- **Sem segredos embutidos**; configuração sensível por ambiente/arquivo (constituição IV).
- **Headless (Q3=A)**: config + variáveis de ambiente com defaults seguros; sem passos interativos obrigatórios.
- **Adoção incremental (Q2=A)**: scripts instaladores próprios entram por ferramenta; a primeira entrega cobre o framework (bootstrap de infra + apps de referência) e validação; demais ferramentas são incrementais e, quando hospedadas, o catálogo passa a referenciá-las.
- Catálogo como fonte de verdade das definições; scripts instaladores próprios adotados por ferramenta de forma incremental (nem todos na primeira entrega).
- Idioma PT-BR (saídas/mensagens) — consistente com o Admin.
