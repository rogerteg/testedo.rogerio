# Feature Specification: Provisionador Real (Automatic1)

**Feature Branch**: `004-provisioner`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Etapa 3 — provisionador real". O Automatic1 Admin já cataloga setups (`001`/`002`) e registra máquinas alvo e execuções como estado (`003`). Esta feature faz o Automatic1 **executar de fato** um setup numa máquina alvo (Debian + Docker Swarm): consume o catálogo (origem do asset/versão/hash), roda de forma **idempotente** com **validação de integridade** quando o hash existe (supply-chain, constituição IV), registra **log estruturado e status real** na `Execution` (feature `003`) — sem expor segredos. É o v2 do produto (o "instalador" dirigido pelo catálogo).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Executar um setup numa máquina alvo (Priority: P1)

Um operador, a partir de um setup do catálogo e de uma máquina alvo ativa, dispara o **provisionamento real**. O Automatic1 executa o setup na máquina de forma idempotente e segura, atualizando a `Execution` com status, saída/log e horários reais. Falhas são claras e acionáveis (constituição V/VI).

**Why this priority**: É o núcleo da Etapa 3 e o salto do catálogo para a operação real; sem isso, máquinas/execuções (`003`) são apenas metadados.

**Independent Test**: Pode ser testado isoladamente com um executor simulado/fixture (sem máquina real): disparar uma execução resulta em `Execution` com status real e log estruturado.

**Acceptance Scenarios**:

1. **Given** um setup do catálogo e uma máquina alvo **ativa**, **When** o operador dispara a execução, **Then** o Automatic1 executa o setup (idempotente) e registra a `Execution` com status (`sucesso`/`erro`), saída/log e horários.
2. **Given** uma falha durante a execução (asset indisponível, hash divergente, timeout, erro do comando), **When** ela ocorre, **Then** a `Execution` fica com status `erro`, o log estruturado registra o motivo e **nenhum** segredo aparece no log.
3. **Given** a mesma execução disparada mais de uma vez, **When** repetida, **Then** o comportamento é **idempotente** (sem efeitos duplicados/destrutivos).
4. **Given** uma máquina **inativa** ou um setup arquivado, **When** o operador tenta executar, **Then** o sistema bloqueia com mensagem clara.

---

### User Story 2 - Acompanhar e reexecutar (Priority: P2)

Um operador consulta o **resultado detalhado** (log/status) da execução real no histórico (setup e máquina) e pode **reexecutar** um setup na mesma máquina.

**Why this priority**: Complementa a US1 com leitura/retry; a execução já entrega valor sozinha.

**Independent Test**: Pode ser testado isoladamente: após uma execução real, o histórico exibe o log/status; reexecutar atualiza o histórico com nova execução.

**Acceptance Scenarios**:

1. **Given** uma execução real concluída, **When** o operador abre o histórico (setup/máquina), **Then** vê status, log/saída, horários e autor.
2. **Given** uma execução com erro, **When** o operador reexecuta (após corrigir), **Then** uma nova `Execution` é criada com o novo resultado (histórico preservado).

---

### User Story 3 - Executar com segurança (Priority: P1 — transversal)

Toda execução real respeita a constituição IV: credenciais de acesso vêm de **cofre/variáveis de ambiente** (nunca do banco), o asset é validado por **hash quando disponível** antes de rodar, e logs nunca contêm segredos (redação automática).

**Why this priority**: Executar código em máquinas é superfície de alto risco; segurança é pré-requisito, não adicional.

**Independent Test**: Testável isoladamente com fixture: cenários de hash divergente (bloqueia), ausência de credencial configurada (bloqueia com mensagem) e log sem segredo.

**Acceptance Scenarios**:

1. **Given** um asset com hash registrado, **When** o hash verificado diverge do esperado, **Then** a execução **é bloqueada** antes de rodar, com erro claro e nenhum efeito colateral.
2. **Given** acesso à máquina não configurado (credencial ausente no cofre/ambiente), **When** o operador executa, **Then** o sistema bloqueia com mensagem acionável, **sem** pedir/salvar segredo no banco.
3. **Given** a saída/log da execução, **When** ela contém algo que pareça segredo, **Then** o log exibido/armazenado tem o trecho **redigido**.

---

### Edge Cases

- Máquina inativa ou setup arquivado → bloqueio com mensagem.
- Sem credencial configurada para o host → bloqueio claro (nunca gravar segredo).
- Hash ausente (upstream sem hash) → executa com aviso de "integridade não verificada" (política de supply-chain).
- Asset/URL indisponível ou download falho → status `erro` com motivo no log.
- Timeout/execução longa → limites com feedback; sem travar a interface.
- Repetição/reexecução → idempotente; histórico sempre preservado.
- Concorrência (duas execuções do mesmo setup×máquina) → serializada/regra definida.
- Segredo acidental em log/saída → redigido antes de persistir/exibir.
- Falha parcial no meio → status `erro`, sem estado inconsistente (idempotência permite reexecução segura).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir que um operador **execute** um setup do catálogo numa máquina alvo **ativa**, de forma idempotente, e registre a `Execution` (feature `003`) com status real, saída/log e horários (Q1=A). A execução é **remota via SSH** pelo Automatic1 Admin, através de um **runner** (abstração plugável): adaptador SSH em produção e adaptador **simulado** em testes (sem rede). Execução síncrona com timeout no v1.
- **FR-002**: O sistema DEVE **bloquear** execução quando a máquina estiver inativa ou o setup arquivado, com mensagem clara.
- **FR-003**: O sistema DEVE executar apenas o **asset referenciado** pelo setup (origem), aplicando **validação de integridade (hash)** quando disponível; hash divergente → bloqueia antes de rodar; hash ausente → executa com aviso.
- **FR-004**: Credenciais de acesso DEVEM vir de **variáveis de ambiente** mapeadas pelo host (ex.: `AUTOMATIC1_SSH_USER`/`AUTOMATIC1_SSH_KEY` por host) ou arquivo de config SSH — **nunca do banco/UI**; ausência de credencial → **bloqueio acionável** antes de qualquer conexão (Q2=A).
- **FR-005**: Logs de execução NÃO DEVEM conter segredos — redação automática de trechos sensíveis antes de persistir/exibir.
- **FR-006**: O histórico (`003`) DEVE exibir o resultado real (status, log/saída, horários, autor) e permitir **reexecução** (nova `Execution`, histórico preservado).
- **FR-007**: O sistema DEVE aplicar limites (timeout) e feedback claro, e **bloquear** execução concorrente do mesmo par setup×máquina (regra: no máximo uma execução `em_andamento` por par). **O que é executado (Q3=A refinada)**: o **asset/script-fonte referenciado por `origem_asset`**, verificado por `hash` (sha256) quando presente; `hash` ausente → executa com aviso de integridade não verificada. Se `origem_asset` **não** for um artefato executável (ex.: URL de repositório), a execução é **bloqueada com erro acionável** orientando a informar o script instalador — os scripts instaladores por ferramenta serão fornecidos com a feature instalador (Etapa 4 do roadmap).
- **FR-008**: Auditoria/autor nas execuções reais (feature `003` mantida).

### Key Entities *(include if feature involves data)*

- **Execution** (feature `003`, evoluída): ganha dados da execução real — horários de início/fim, saída/log (texto maior), código de saída e gatilho (autor). Imutável em status; reexecução cria novo registro.
- **Setup de Ambiente** / **Target Host**: entidades existentes — fonte (origem/versão/hash) e alvo da execução.
- **Executor (conceitual)**: responsável por rodar o setup de forma idempotente com limites, validação e redação — não é entidade persistida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um operador dispara uma execução real e vê o resultado (status + log) em menos de 1 minuto após a conclusão.
- **SC-002**: 100% das execuções com hash divergente são bloqueadas antes de qualquer efeito colateral.
- **SC-003**: 100% das falhas registram `erro` com log estruturado contendo o motivo; auditoria por amostragem não encontra segredo em nenhum log.
- **SC-004**: 0 credenciais persistidas no banco; toda execução usa cofre/ambiente.
- **SC-005**: Reexecutar é idempotente e preserva 100% do histórico anterior.
- **SC-006**: Execuções concorrentes do mesmo par não corrompem estado (regra definida e testada).

## Assumptions

- Ferramenta de administração interna; operador = autor configurado (sem auth no v1, `OPERATOR_NAME`).
- Ambiente-alvo suportado: **Debian 11/12 + Docker Swarm** (decisão já tomada).
- **Nenhuma credencial** é armazenada no banco (constituição IV) — acesso via cofre/variáveis de ambiente (detalhe na clarificação Q2).
- O **hash** do asset só é validado quando presente; a política de "sem hash → aviso" segue a constituição (revisar asset antes de adotar).
- **Executabilidade (Q3=A)**: a execução exige que `origem_asset` aponte para um **artefato executável** (script). Os itens do catálogo padrão (`002`) que apontam para repositórios upstream **não são executáveis** até existirem scripts instaladores (feature instalador); o executor responde com erro acionável nesses casos.
- Idiomas: PT-BR.
