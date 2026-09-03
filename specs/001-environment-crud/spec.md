# Feature Specification: CRUD de Ambientes de Setup (Automatic1)

**Feature Branch**: `001-environment-crud`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "crie o crud do meu projeto" — CRUD dos registros de ambientes/setups gerenciados pelo Automatic1. Interface web de administração interna. v1 entrega operações essenciais (criar + listar); editar/excluir entram como prioridade menor.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
-->

### User Story 1 - Cadastrar um novo setup de ambiente (Priority: P1)

Um administrador interno cadastra um novo "setup de ambiente": a configuração/automação que o Automatic1 provisiona em uma máquina. Ele informa nome, plataforma alvo e a origem do asset (ex.: repositório/script-fonte); opcionalmente descrição, versão, hash, licença e status. O sistema valida os dados (nome único, versão SemVer válida quando informada), persiste o registro e confirma o sucesso.

**Why this priority**: É a operação central do CRUD e a fonte dos dados que as demais telas consomem — sem cadastro, não há catálogo a listar/editar/excluir. Entrega valor imediato: o catálogo começa a existir.

**Independent Test**: Pode ser testado isoladamente: o administrador cria um setup válido e o sistema confirma a persistência. Entrega a capacidade de registrar setups no catálogo do Automatic1.

**Acceptance Scenarios**:

1. **Given** um administrador no formulário de novo setup com os campos obrigatórios preenchidos corretamente, **When** ele confirma o cadastro, **Then** o registro é criado e persistido, uma mensagem de sucesso é exibida e o novo setup aparece na listagem.
2. **Given** um administrador tenta cadastrar um setup com um nome já existente no catálogo, **When** ele confirma o cadastro, **Then** o sistema exibe um erro claro de nome duplicado, mantém os dados preenchidos no formulário e **não** cria registro duplicado.
3. **Given** um administrador submete o formulário sem um campo obrigatório (ex.: plataforma alvo), **When** ele confirma, **Then** o sistema indica em nível de campo o que está faltando e **não** cria o registro.
4. **Given** um administrador informa uma versão em formato inválido (fora do padrão SemVer), **When** ele confirma, **Then** o sistema explica o formato esperado e **não** cria o registro.

---

### User Story 2 - Listar setups de ambiente cadastrados (Priority: P1)

Um administrador abre a tela de listagem e vê todos os setups cadastrados em forma de resumo (nome, plataforma alvo, status e data da última atualização), ordenados do mais recente para o mais antigo. Ele pode buscar/filtrar por nome ou plataforma. Quando não há registros, vê um estado vazio amigável com atalho para cadastrar o primeiro.

**Why this priority**: É a segunda metade do MVP (operar/consultar o catálogo). Sem leitura, o cadastro tem pouco valor operacional; juntos, criar + listar formam uma fatia utilizável de ponta a ponta.

**Independent Test**: Pode ser testado isoladamente: com ao menos um setup cadastrado, o administrador abre a listagem e vê os registros. Entrega a capacidade de consultar o catálogo.

**Acceptance Scenarios**:

1. **Given** que existem setups cadastrados, **When** o administrador abre a listagem, **Then** todos os registros são exibidos com nome, plataforma, status e data de atualização, ordenados do mais recente para o mais antigo.
2. **Given** uma listagem com vários registros, **When** o administrador busca/filtra por nome ou plataforma, **Then** apenas os registros compatíveis são exibidos.
3. **Given** que ainda não há nenhum setup cadastrado, **When** o administrador abre a listagem, **Then** um estado vazio amigável é exibido com atalho para o cadastro.
4. **Given** que a busca/filtro não retorna resultados, **When** o administrador consulta, **Then** o sistema informa que nada foi encontrado e sugere ajustar o filtro.

---

### User Story 3 - Visualizar os detalhes de um setup (Priority: P2)

Um administrador abre um registro da listagem e vê os detalhes completos do setup: descrição, origem do asset, versão, hash, licença/notas de compliance, status, resultado da última execução e informações de autoria/atualização. Campos opcionais não preenchidos aparecem como "não informado".

**Why this priority**: Aprofunda a operação de leitura e é pré-requisito natural para editar/excluir com segurança. A listagem sozinha já entrega o MVP, então os detalhes entram como prioridade secundária.

**Independent Test**: Pode ser testado isoladamente: com um registro na listagem, o administrador abre a tela de detalhes e confere as informações completas.

**Acceptance Scenarios**:

1. **Given** um registro exibido na listagem, **When** o administrador o seleciona, **Then** a tela de detalhes mostra todas as informações cadastradas do setup.
2. **Given** um registro com campos opcionais vazios, **When** o administrador visualiza os detalhes, **Then** esses campos aparecem como "não informado" sem erros ou quebras de tela.
3. **Given** um registro com dados de autoria, **When** o administrador visualiza os detalhes, **Then** ele consegue ver quem criou/atualizou e quando.

---

### User Story 4 - Editar um setup existente (Priority: P2)

Um administrador altera os dados de um setup já cadastrado. As mesmas validações do cadastro se aplicam (nome único, SemVer válida), as alterações são persistidas e o sistema registra autoria e data da edição.

**Why this priority**: É a operação de atualização do CRUD. Foi adiada para depois da primeira entrega (v1 = criar + listar) conforme escopo definido pelo usuário, mas faz parte da feature.

**Independent Test**: Pode ser testado isoladamente: com um registro existente, o administrador edita um campo e salva; a mudança é refletida na listagem/detalhes.

**Acceptance Scenarios**:

1. **Given** um setup existente, **When** o administrador edita campos com valores válidos e salva, **Then** os novos valores são persistidos e refletidos na listagem e nos detalhes.
2. **Given** que o administrador renomeia o setup para um nome já usado por outro registro, **When** ele salva, **Then** a alteração é bloqueada com erro claro e nenhuma atualização parcial é aplicada.
3. **Given** uma edição bem-sucedida, **When** ela é salva, **Then** o sistema registra autor e data da alteração, visíveis no registro.

---

### User Story 5 - Excluir (arquivar) um setup (Priority: P3)

Um administrador remove um setup da listagem ativa. A remoção exige confirmação explícita, é reversível (arquivamento) e mantém a trilha de auditoria — nada é apagado de forma irreversível.

**Why this priority**: É a operação de exclusão do CRUD, com maior risco de perda de dados; por isso entra por último, adiada para depois da primeira entrega (v1 = criar + listar).

**Independent Test**: Pode ser testado isoladamente: com um registro ativo, o administrador solicita a remoção, confirma e o registro sai da listagem ativa permanecendo recuperável.

**Acceptance Scenarios**:

1. **Given** um setup ativo, **When** o administrador solicita a remoção, **Then** o sistema exige confirmação explícita antes de qualquer mudança.
2. **Given** a confirmação da remoção, **When** ela é concluída, **Then** o registro sai da listagem ativa, permanecendo arquivado/recuperável e auditável.
3. **Given** que o administrador cancela a confirmação, **When** nada mais é feito, **Then** o registro permanece inalterado.
4. **Given** um setup que esteja associado a uma utilização ativa registrada, **When** o administrador tenta removê-lo, **Then** o sistema exibe um aviso antes de prosseguir.

---

### Edge Cases

- Nome duplicado com diferenças apenas de maiúsculas/minúsculas ou espaços: deve ser tratado como duplicado.
- Campos obrigatórios ausentes ou versão fora do padrão SemVer: bloqueiam o salvamento com mensagem acionável.
- Listagem vazia (nenhum registro) e busca sem resultados: estados vazios amigáveis, sem erros.
- Dois administradores editam o mesmo registro ao mesmo tempo: no v1, aceita-se "última gravação vence" (documentado), sem conflito complexo.
- Tentativa de remover um setup com utilização ativa registrada: aviso antes de prosseguir.
- Texto muito longo ou com caracteres especiais em campos livres (ex.: descrição): aceito sem quebrar telas/validações.
- Registros com campos opcionais vazios: devem renderizar como "não informado", nunca como erro.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir que um administrador cadastre um novo setup de ambiente com os campos: nome (obrigatório, único), plataforma alvo (obrigatória), origem do asset (obrigatória) e opcionais descrição, versão, hash, licença/notas de compliance, status e resultado da última execução.
- **FR-002**: O sistema DEVE impedir nomes duplicados, tratando diferenças de maiúsculas/minúsculas e espaços como duplicação.
- **FR-003**: O sistema DEVE validar a versão informada como SemVer válida quando preenchida.
- **FR-004**: Submissões com campos obrigatórios ausentes ou inválidos DEVEM retornar erro claro em nível de campo, **sem** criar o registro e **preservando** os dados preenchidos.
- **FR-005**: O sistema DEVE listar os setups cadastrados com resumo (nome, plataforma, status e data da última atualização), ordenados do mais recente para o mais antigo.
- **FR-006**: O sistema DEVE permitir buscar/filtrar a listagem por nome ou plataforma.
- **FR-007**: O sistema DEVE exibir estado vazio amigável quando não houver registros ou resultados compatíveis.
- **FR-008**: O sistema DEVE exibir os detalhes completos de um único setup (incluindo origem, versão, hash, licença, status, última execução e autoria).
- **FR-009**: O sistema DEVE permitir editar um setup existente aplicando as mesmas validações do cadastro, sem atualização parcial em caso de erro.
- **FR-010**: O sistema DEVE permitir remover um setup da listagem ativa somente após confirmação explícita, mantendo o registro arquivado/recuperável (exclusão reversível) e auditável.
- **FR-011**: O sistema DEVE registrar autoria (quem) e data para criação, edição e remoção de cada registro (trilha de auditoria).
- **FR-012**: O sistema DEVE persistir os registros de forma durável (sobrevivem a reinícios).
- **FR-013**: O sistema NÃO DEVE armazenar segredos/credenciais nos dados do setup; apenas referências ou placeholders são permitidos.
- **FR-014**: Todas as mensagens de erro e feedback DEVEM ser claras e acionáveis, indicando como o usuário pode corrigir.

### Key Entities *(include if feature involves data)*

- **Setup de Ambiente (Environment Setup)**: representa um ambiente/setup catalogado que o Automatic1 pode provisionar. Atributos de negócio: nome (único, legível), descrição, plataforma alvo, origem do asset (ex.: repositório/script-fonte), versão (SemVer), hash/checksum, licença/notas de compliance, status (ex.: rascunho, ativo, arquivado, com erro), resultado da última execução, criado/atualizado (autor + data). No v1 é entidade única, sem relacionamentos obrigatórios com outras entidades.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um administrador consegue cadastrar um setup válido em menos de 2 minutos.
- **SC-002**: 100% das tentativas inválidas (nome duplicado, campo obrigatório ausente ou versão fora do padrão) retornam uma mensagem clara que permite corrigir na primeira tentativa, sem criar registro indevido.
- **SC-003**: Um administrador localiza um setup específico na listagem em até 3 interações (busca/filtro).
- **SC-004**: 100% das criações, edições e remoções possuem registro de auditoria (quem + quando).
- **SC-005**: Auditoria por amostragem não encontra segredo/credencial em nenhum registro de setup.
- **SC-006**: 90% das operações essenciais (criar/listar) são concluídas com sucesso na primeira tentativa pelo usuário.
- **SC-007**: Nenhuma remoção resulta em perda irreversível de dados (todo registro removido permanece recuperável/auditável).

## Assumptions

- A feature é uma **ferramenta de administração interna** (interface web em navegador moderno), usada em ambiente/redes de confiança. **Autenticação/permissões ficam fora do escopo v1** e podem ser adicionadas depois.
- **v1 entrega as operações essenciais — criar e listar** — conforme decisão do usuário. Editar (US4, P2) e excluir/arquivar (US5, P3) fazem parte do CRUD, porém ficam para slices/entregas seguintes ("por enquanto").
- Entidade única no v1 (YAGNI): apenas **Setup de Ambiente**; mais entidades surgem quando houver necessidade concreta.
- Convenções de negócio herdadas da constituição do projeto: os setups catalogados são automações scriptáveis e reprodutíveis, com versionamento SemVer e sem segredos embutidos; essas convenções orientam campos e validações (ex.: exigir versão, recusar segredos), sem prescrever a tecnologia da interface.
- Os campos listados da entidade são um ponto de partida razoável derivado da constituição; podem ser refinados nas fases de clarificação/planejamento.
- Persistência local durável é suficiente no v1; sem requisito de multiusuário intensivo — concorrência "última gravação vence" é aceitável.
- Executar de fato o provisionamento (rodar o setup) está **fora do escopo** desta feature: aqui o foco é apenas catalogar/gerir os registros.
- Idioma da interface não especificado; assumido **português (PT-BR)** por padrão, revisável.
- Não há sistema legado a integrar no v1; esta é a primeira feature do catálogo.
