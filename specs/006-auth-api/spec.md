# Feature Specification: Autenticação e API REST (Automatic1)

**Feature Branch**: `006-auth-api`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Etapa 5 — camada de gestão do Admin (pode rodar em paralelo): auth, REST API p/ consumo externo". As features `001`–`005` funcionam **sem autenticação** (premissa registrada: ferramenta interna, autor = `OPERATOR_NAME`). Esta feature adiciona **autenticação** ao Admin (UI web) e uma **API REST** para consumo externo (integração/monitoração), protegendo as operações hoje abertas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autenticar-se no Admin (web) (Priority: P1)

Um operador acessa o Automatic1 Admin e precisa **autenticar-se** antes de ver/gerir setups, máquinas, execuções e provisionamento. As rotas web ficam protegidas; sessões expiram; sair encerra a sessão. A senha **nunca** fica no banco/código — vem de variável de ambiente (constituição IV).

**Why this priority**: Remove a abertura total do v1 (`001`–`005` assumiam rede interna); é o pré-requisito de segurança para expor o Admin/API.

**Independent Test**: Pode ser testado isoladamente: sem sessão, acessar uma rota web → redireciona/401; após login com a senha do ambiente, as rotas funcionam; logout invalida.

**Acceptance Scenarios**:

1. **Given** um visitante sem sessão, **When** ele abre qualquer página do Admin, **Then** é direcionado ao login (ou recebe `401`/redirect).
2. **Given** credenciais corretas (senha do ambiente), **When** o operador faz login, **Then** a sessão é criada e as rotas web ficam acessíveis.
3. **Given** credenciais incorretas ou inexistentes, **When** o operador tenta logar, **Then** o acesso é negado com mensagem clara e **nada** é registrado além do log de tentativa.
4. **Given** uma sessão ativa, **When** o operador faz logout ou a sessão expira, **Then** as rotas voltam a exigir autenticação.
5. **Given** a senha do ambiente, **When** o sistema a usa, **Then** ela nunca é exibida/logada/armazenada em texto (apenas comparação segura).

---

### User Story 2 - Consumir uma API REST autenticada (Priority: P1)

Um sistema externo (integração/monitoração) consulta os dados do Automatic1 via **API REST** usando um **token de API** (separado da sessão web), com respostas JSON claras e limites de escopo definidos.

**Why this priority**: Habilita consumo externo de forma segura, sem expor a UI; complementa a auth da US1.

**Independent Test**: Pode ser testado isoladamente: chamada sem token → `401`; com token inválido → `401`; com token válido → respostas JSON corretas dentro do escopo permitido.

**Acceptance Scenarios**:

1. **Given** uma chamada à API sem token, **When** enviada, **Then** a resposta é `401` com corpo JSON claro.
2. **Given** um token de API válido (do ambiente), **When** enviado (cabeçalho de autorização), **Then** a API responde `200` com JSON no formato documentado.
3. **Given** um token válido, **When** o cliente acessa um recurso fora do escopo do token/plano, **Then** a resposta é `403`/`404` clara.
4. **Given** a resposta da API, **When** ela contém dados, **Then** **nenhum segredo** aparece (máquinas sem credenciais; logs sanitizados — features `003`/`004`).

---

### User Story 3 - Proteger as operações de escrita (UI e API) (Priority: P2)

As ações de escrita (criar/editar/arquivar setup, máquinas, registrar execução, **provisionar**) e as chamadas **operacionais** da API exigem autenticação/autorização explícitas e ficam **auditadas** com o autor real (não mais só `OPERATOR_NAME` quando houver identidade).

**Why this priority**: As features `001`–`005` já registram autoria via operador configurado; com auth, a autoria passa a refletir a sessão/token, e todas as escritas ficam de fato protegidas.

**Independent Test**: Pode ser testado isoladamente: sem autenticação, uma ação de escrita web/API é negada; com auth, a ação ocorre e fica registrada com o autor real.

**Acceptance Scenarios**:

1. **Given** um usuário sem sessão/token, **When** ele tenta uma ação de escrita, **Then** é negado (`401`/redirect) sem efeito colateral.
2. **Given** uma ação de escrita autenticada, **When** concluída, **Then** a auditoria registra o autor real (usuário da sessão ou identidade do token).
3. **Given** tentativas de acesso inválido (login/senha/token errados), **When** repetidas, **Then** há registro/controle de tentativa sem expor detalhes sensíveis.

---

### Edge Cases

- Sem senha/token configurados no ambiente → o Admin deve **bloquear com mensagem clara** (nunca aceitar vazio/“default”).
- Sessão expirada no meio de um formulário → redireciona ao login preservando a intenção (mensagem amigável).
- Token vazado → rotação via ambiente/documentada; nenhum token no banco.
- Acesso à API sem escopo → `403`/`404` claros, sem vazar existência.
- Concorrência de logins/logouts → sessões independentes e auditadas.
- Saúde/health e login em si ficam públicos (sem auth) — demais rotas protegidas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: As rotas **web do Admin** (exceto login/health) DEVEM exigir autenticação; sem sessão → redirect ao login (ou `401`).
- **FR-002**: O sistema DEVE autenticar o operador com senha vinda de **variável de ambiente** (`AUTOMATIC1_ADMIN_PASSWORD`), comparada de forma **segura** e **nunca armazenada/exibida/logada** (Q1=A). Mecanismo: **sessão + senha única** (cookie de sessão assinado) — **sem gestão de usuários no v1**.
- **FR-003**: O sistema DEVE fornecer **logout** e **expiração de sessão**; a senha do ambiente nunca fica no banco.
- **FR-004**: O sistema DEVE expor uma **API REST** autenticada por **token de API** (cabeçalho de autorização), com respostas JSON documentadas e **sem segredos** nos dados.
- **FR-005**: A API DEVE respeitar **escopo** definido para o token (Q2=A): no v1, **somente leitura** — consultar setups, máquinas e execuções em JSON; sem operações de escrita via API nesta etapa. Fora do escopo → `403`/`404` claros.
- **FR-006**: Escritas (UI e API operacional) DEVEM exigir autenticação e registrar **autor real** na auditoria (Q3=A): **mantém-se `OPERATOR_NAME` como autor** — a auth valida a senha única/token, mas a auditoria das features `001`–`005` continua usando o operador configurado (sem gestão de usuários no v1).
- **FR-007**: Sem senha/token configurados no ambiente, o Admin DEVE bloquear com mensagem clara (nunca aceitar vazio).
- **FR-008**: Tentativas de autenticação inválidas DEVEM ser registradas (log) sem expor detalhes sensíveis; health e login permanecem públicos.

### Key Entities *(include if feature involves data)*

- **Sessão Web**: estado de autenticação do operador (cookie seguro) — não é entidade persistida no v1 (sem usuários em banco).
- **Token de API**: identidade/credencial para consumo externo — **não persistido no banco** (vem do ambiente; rotação por deploy/documentada).
- Entidades existentes (`EnvironmentSetup`, `TargetHost`, `Execution`) expostas via API conforme escopo; **sem segredos** (features `003`/`004` mantêm a regra).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das rotas web (exceto login/health) exigem autenticação; acesso sem sessão é redirecionado em < 1s.
- **SC-002**: Login com senha correta do ambiente concede acesso em < 2s; senha incorreta é negada sem expor detalhes.
- **SC-003**: 100% das chamadas de API sem token → `401`; com token inválido → `401`; com token válido → respostas JSON corretas (escopo respeitado, `403`/`404` quando fora).
- **SC-004**: Auditoria por amostragem não encontra senha/token em banco, logs ou respostas de API.
- **SC-005**: Sem `AUTOMATIC1_ADMIN_PASSWORD`/token configurados, o Admin bloqueia (0 acesso com vazio).
- **SC-006**: 100% das ações de escrita autenticadas registram autor real (conforme decisão Q3).

## Assumptions

- Ferramenta interna de baixo volume; **um operador** no v1 (sem gestão complexa de usuários) — sujeito à clarificação Q3.
- **Sem segredos no banco/repo**: senha, token de API e segredo de sessão por variáveis de ambiente (constituição IV); rotação por deploy.
- **Decisões**: Q1=A sessão + senha única (`AUTOMATIC1_ADMIN_PASSWORD`) com cookie de sessão assinado; Q2=A API **somente leitura** (token via `AUTOMATIC1_API_TOKEN`); Q3=A autoria mantém `OPERATOR_NAME` (sem usuários no v1).
- Health e página de login permanecem públicas; todo o resto protegido.
- APIs retornam **JSON** com mensagens claras; PT-BR nas mensagens voltadas a humanos.
- Manter compatibilidade: rotas/semântica das features `001`–`005` preservadas quando autenticadas.
