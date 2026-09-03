# Feature Specification: Catálogo Padrão do Automatic1 (stack de referência)

**Feature Branch**: `002-seed-real-stack`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Etapa 1 — semear o catálogo com a stack real". O Automatic1 provisiona setups de ambiente num alvo Linux/Debian + Docker Swarm (modelo de referência SetupFrancisMno/SetupOrion). Esta feature converte o catálogo (feature `001`, CRUD de setups) de um registro vazio num registro **real**: carrega o **catálogo padrão** do Automatic1 — infraestrutura base e aplicações da stack de referência — com rastreabilidade de origem/versão/hash/licença (constituição IV) e com ambiente-alvo estruturado. **Provisionamento/execução continua fora do escopo.**

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carregar o catálogo padrão de setups do Automatic1 (Priority: P1)

Um administrador, ao começar a usar o catálogo (ambiente novo, ainda sem registros), carrega o **catálogo padrão**: o conjunto de setups que o Automatic1 provisiona de fábrica num ambiente Debian + Docker Swarm — composto pela infraestrutura base e pelas aplicações da stack de referência. Cada registro carregado já vem com a **origem do asset** (fonte upstream), versão e hash (quando publicamente disponíveis) e licença/notas de compliance, de modo que o catálogo nasce com rastreabilidade, sem o administrador precisar cadastrar item por item.

**Why this priority**: É a operação central da Etapa 1 e o alicerce das demais. Converte o catálogo vazio em um registro real com proveniência auditável (constituição IV), entregando valor imediato e criando a base de dados que as próximas etapas (máquinas/execuções e provisionamento) consumirão.

**Independent Test**: Pode ser testado isoladamente: num catálogo vazio, o administrador executa a ação de carregar o catálogo padrão e confere que a lista padrão completa aparece na listagem ativa com origem/versão/hash/licença documentados.

**Acceptance Scenarios**:

1. **Given** um catálogo vazio (nenhum registro), **When** o administrador carrega o catálogo padrão, **Then** os setups padrão (infraestrutura base + aplicações da stack de referência) são adicionados e aparecem na listagem ativa.
2. **Given** a carga do catálogo padrão concluída, **When** o administrador confere os registros, **Then** cada registro padrão exibe a origem do asset documentada e, quando publicamente disponível, versão (SemVer) e hash; campos sem valor público aparecem como "não informado".
3. **Given** um registro padrão carregado, **When** o administrador abre os detalhes, **Then** vê a origem do asset (referência ao upstream) e as notas de licença/compliance.
4. **Given** a carga em execução, **When** algum dado do catálogo padrão aparenta ser segredo/credencial, **Then** o registro é bloqueado, nada é persistido e um erro claro é reportado.

---

### User Story 2 - Identificar a função e o ambiente-alvo de cada setup padrão (Priority: P2)

Um administrador consegue distinguir os setups de **infraestrutura base** (ex.: orquestração/containers, proxy, gerenciador de containers, bancos e serviços de apoio) dos de **aplicação**, e reconhece de forma consistente o **ambiente-alvo** que o Automatic1 suporta (Debian + Docker Swarm). Isso dá significado a cada registro e prepara as próximas etapas (provisionamento).

**Why this priority**: Dá estrutura semântica ao catálogo (categoria + ambiente-alvo controlado) e é pré-requisito natural para a etapa de provisionamento. O carregamento (US1) já entrega valor sozinho; a classificação entra como prioridade secundária.

**Independent Test**: Pode ser testado isoladamente: após carregar o catálogo padrão, o administrador consulta e filtra a listagem por categoria (infraestrutura vs aplicação) e pelo ambiente-alvo suportado.

**Acceptance Scenarios**:

1. **Given** o catálogo padrão carregado, **When** o administrador consulta os registros, **Then** cada setup padrão está classificado como **infraestrutura base** ou **aplicação**.
2. **Given** um setup do catálogo padrão, **When** o administrador visualiza a plataforma alvo, **Then** ela é apresentada de forma controlada e consistente (Debian + Docker Swarm), não como texto livre divergente.
3. **Given** a listagem de setups, **When** o administrador filtra por categoria ou por ambiente-alvo, **Then** apenas os registros compatíveis são exibidos.

---

### User Story 3 - Recarregar/atualizar o catálogo padrão com segurança (Priority: P3)

Quando o catálogo padrão do Automatic1 evolui (nova versão de uma aplicação, correção de origem/licença), um administrador atualiza os registros padrão **sem duplicar** e **sem perder** o que ele mesmo criou ou editou no catálogo.

**Why this priority**: Garante a integridade dos dados ao longo do tempo. Depende do carregamento (US1) e da classificação (US2); por isso entra por último, adiada para depois do valor inicial entregue.

**Independent Test**: Pode ser testado isoladamente: executar o carregamento duas vezes e confirmar que nada é duplicado; editar um registro padrão e recarregar confirmando que a edição do usuário é preservada.

**Acceptance Scenarios**:

1. **Given** o catálogo padrão já carregado, **When** o administrador carrega novamente o mesmo padrão, **Then** nenhum registro duplicado é criado e o relatório informa os registros "ignorados: já existem".
2. **Given** registros criados/editados pelo usuário no catálogo, **When** o administrador recarrega o catálogo padrão, **Then** esses registros não são sobrescritos nem removidos.
3. **Given** registros padrão já existentes (mesmo sem edição do usuário) e uma mudança no padrão de origem/versão, **When** o administrador recarrega, **Then** nenhum registro existente é alterado — a recarga é aditiva; a propagação de metadados padrão em registros já existentes fica para quando houver trilha de proveniência.
4. **Given** uma recarga concluída, **When** o administrador consulta o resultado, **Then** um relatório claro informa quantos registros foram criados/ignorados e eventuais avisos.
5. **Given** uma carga/recarga do catálogo padrão, **When** ela é concluída, **Then** a operação em massa fica registrada com autor e data (trilha de auditoria).

---

### Edge Cases

- Catálogo parcialmente populado (alguns registros padrão já existem, outros não): a carga adiciona só os ausentes.
- Nome de um registro padrão colidindo (caixa/espaços) com um registro criado pelo usuário: tratado como já existente; o registro do usuário é preservado.
- Aplicação cujo upstream não publica versão nem hash estáveis (ex.: "latest"/rolling): campos exibidos como "não informado"; nunca inventar valor.
- Origem do asset inacessível/URL movida: permanece como referência; nenhuma tentativa de download nesta feature.
- Carga interrompida no meio: a reexecução é idempotente e resolve sem duplicar.
- Duas pessoas carregando simultaneamente: regra de nome único impede duplicação; concorrência aceita como "última gravação vence".
- Itens ainda não suportados ("em breve", ex.: Flowise/UptimeKuma): não fazem parte do catálogo padrão nesta feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir que um administrador carregue o **catálogo padrão** de setups do Automatic1 por meio de uma **ação explícita na interface** (CTA no estado vazio + botão dedicado "carregar catálogo padrão"); nada é inserido sem o administrador pedir (sem carga automática).
- **FR-002**: O conteúdo do catálogo padrão DEVE replicar a **stack de referência completa** suportada pelo Automatic1: infraestrutura base (Docker, Docker Swarm, Traefik, Portainer, Postgres, MongoDB, Redis) + aplicações (Chatwoot, Evolution API, Typebot, N8N, Appsmith, Minio, RabbitMQ, PgAdmin4); itens "em breve" (ex.: Flowise, UptimeKuma) ficam fora até serem suportados.
- **FR-003**: Cada registro do catálogo padrão DEVE registrar a **origem do asset** (fonte upstream) e, quando publicamente disponível, versão (SemVer) e hash/checksum; quando o upstream não publica esses valores, DEVEM aparecer como "não informado" (nunca inventados). Notas de licença/compliance DEVEM ser registradas.
- **FR-004**: O carregamento do catálogo padrão DEVE ser **idempotente**: nunca criar registros duplicados (mesma regra de nome único da feature `001` — caixa/espaços insensíveis).
- **FR-005**: O carregamento/recarga DEVE ser **aditivo e não destrutivo**: **nunca altera nem remove registros existentes** (política "preservar sempre"); apenas adiciona os registros padrão ausentes. Atualizar registros padrão já existentes (propagação de metadados) fica para quando houver trilha de proveniência.
- **FR-006**: O sistema DEVE apresentar o **ambiente-alvo suportado** (Debian + Docker Swarm) de forma controlada e consistente nos setups padrão, identificável na listagem/detalhes.
- **FR-007**: O sistema DEVE permitir classificar cada setup padrão por **categoria** (infraestrutura base ou aplicação) e filtrar a listagem por categoria ou ambiente-alvo.
- **FR-008**: Ao concluir qualquer carga/recarga, o sistema DEVE exibir um **relatório** claro com a contagem de criados/ignorados e eventuais avisos (ex.: conteúdo bloqueado por suspeita de segredo).
- **FR-009**: Cargas/recargas em massa DEVEM ficar na **trilha de auditoria** com autor e data (mesma política da feature `001`).
- **FR-010**: A regra **anti-segredo** (constituição IV / FR-013 da feature `001`) DEVE valer para todo o conteúdo do catálogo padrão: nenhuma credencial é persistida; apenas referências/placeholders.
- **FR-011**: Executar provisionamento (baixar/instalar/rodar o setup) permanece **fora do escopo**: a carga registra apenas metadados de catálogo e rastreabilidade.

### Key Entities *(include if feature involves data)*

- **Setup de Ambiente (Environment Setup)**: registro existente (feature `001`) que representa um ambiente/setup catalogado que o Automatic1 pode provisionar. Nesta feature ganha: **ambiente-alvo** estruturado (valor controlado, v1 = Debian + Docker Swarm) e **categoria** (infraestrutura base ou aplicação) para os registros padrão; mantém origem do asset, versão (SemVer), hash e licença/compliance como rastreabilidade (constituição IV).
- **Catálogo Padrão (Standard Catalog)**: conjunto de referência dos setups que o Automatic1 provisiona de fábrica (infraestrutura base + aplicações da stack), cada um com proveniência (origem do asset, versão, hash, licença). Não é um registro editável em si: é a **fonte** da carga que gera/atualiza registros de Setup de Ambiente, preservando criações/edições do usuário.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em um catálogo vazio, um administrador popula o catálogo com a stack padrão completa por meio de uma única ação em menos de 5 minutos.
- **SC-002**: 100% dos registros do catálogo padrão possuem origem do asset documentada; versão e hash são preenchidos sempre que publicamente disponíveis (0 valores inventados).
- **SC-003**: Recarregar o catálogo padrão produz 0 duplicatas e 0 alterações/remoções de registros existentes (recarga estritamente aditiva).
- **SC-004**: 100% dos registros do catálogo padrão são identificáveis por categoria (infraestrutura vs aplicação) e pelo ambiente-alvo suportado.
- **SC-005**: Auditoria por amostragem não encontra segredo/credencial em nenhum registro do catálogo padrão.
- **SC-006**: 100% das cargas/recargas exibem um relatório claro de criados/ignorados e avisos.

## Assumptions

- **Ambiente-alvo suportado no v1**: Debian 11/12 + Docker Swarm (decisão do usuário, modelo SetupFrancisMno/SetupOrion). O catálogo padrão se refere a esse único ambiente; demais plataformas ficam fora do escopo do conteúdo padrão nesta feature.
- O **conteúdo do catálogo padrão** espelha a stack de referência: infraestrutura base (Docker, Docker Swarm, Traefik, Portainer, Postgres, MongoDB, Redis) + aplicações (Chatwoot, Evolution API, Typebot, N8N, Appsmith, Minio, RabbitMQ, PgAdmin4). Itens "em breve" (Flowise, UptimeKuma) ficam fora até serem suportados — sujeito à clarificação Q1.
- A **origem do asset** é sempre uma referência ao upstream (URL de repositório/script-fonte), nunca cópia de conteúdo não avaliado (constituição IV).
- **Provisionamento/execução** (baixar, instalar, rodar) permanece fora do escopo: a carga cria apenas registros de catálogo com metadados de rastreabilidade.
- A identidade de não-duplicação é o **nome único** (mesma regra da feature `001`, caixa/espaços insensíveis).
- **Mecanismo de carga** (Q2, resolvida): ação explícita na interface — CTA no estado vazio + botão dedicado; sem inserção automática de dados.
- **Política de atualização** (Q3, resolvida): "preservar sempre" — a recarga é **estritamente aditiva**: nunca altera nem remove registros existentes; propagação de atualizações do padrão em registros já existentes fica para quando houver trilha de proveniência.
- Sem autenticação no v1 (mesma premissa da feature `001`): o autor das operações em massa é o operador configurado.
- Nem todo upstream publica versão/hash estáveis; nesses casos os campos aparecem como "não informado".
- Idioma da interface: **português (PT-BR)**, mesma premissa da feature `001`.
