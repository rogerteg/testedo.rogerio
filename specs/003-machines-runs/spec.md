# Feature Specification: Máquinas Alvo e Execuções (Automatic1)

**Feature Branch**: `003-machines-runs`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Etapa 2 — máquinas alvo e execuções (o 'utilizações ativas')". Após o catálogo (features `001`/`002`), o Automatic1 precisa registrar **onde** cada setup é provisionado. Esta feature adiciona **máquinas alvo** (hosts) e **execuções** (setup × máquina), criando o vínculo que a spec da `001` só mencionava, dando suporte real ao "aviso de utilização ativa" do arquivamento e alimentando `resultado_ultima_execucao`. **Executar o provisionamento de fato (rodar o setup na máquina) pertence à Etapa 3 (`004`)** — aqui fica o registro/modelo.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cadastrar e gerir uma máquina alvo (Priority: P1)

Um administrador cadastra uma **máquina alvo**: um host onde o Automatic1 pode provisionar setups (ex.: um servidor Debian + Docker Swarm). Ele informa nome, identificação/endereço e a plataforma/ambiente; opcionalmente descrição e status. A máquina aparece numa listagem própria, pode ser editada e desativada — **sem armazenar credenciais** (constituição IV).

**Why this priority**: É a metade "onde" do vínculo. Sem máquinas registradas não há como associar execuções; é o ponto de partida da Etapa 2 e pré-requisito do provisionamento (Etapa 3).

**Independent Test**: Pode ser testado isoladamente: o administrador cadastra uma máquina válida, vê-a na listagem, edita e desativa.

**Acceptance Scenarios**:

1. **Given** um administrador no cadastro de máquina, **When** ele informa os campos obrigatórios válidos e confirma, **Then** a máquina é criada, uma mensagem de sucesso aparece e ela surge na listagem.
2. **Given** uma tentativa de cadastro com **nome duplicado** ou sem campo obrigatório, **When** o admin confirma, **Then** o sistema exibe erro claro em nível de campo, preserva os dados e **não** cria duplicado.
3. **Given** uma máquina cadastrada, **When** o admin a edita ou a desativa, **Then** a mudança é persistida com autoria/data (auditoria).
4. **Given** qualquer tela de máquina, **When** o admin a visualiza, **Then** **nenhum** campo solicita/armazena senha, token ou credencial — apenas referências.

---

### User Story 2 - Registrar uma execução de setup numa máquina (Priority: P1)

Um administrador registra que um setup do catálogo foi **executado numa máquina alvo** (ou está planejado/em andamento/falhou), informando status e um resumo opcional. O vínculo fica visível no setup e na máquina, com autoria e data.

**Why this priority**: É a metade "o quê/quando" do vínculo — cria o histórico que a Etapa 3 consumirá e dá significado ao campo "resultado da última execução".

**Independent Test**: Pode ser testado isoladamente: dado um setup e uma máquina, o admin registra uma execução e ela aparece no histórico do setup e da máquina.

**Acceptance Scenarios**:

1. **Given** um setup do catálogo e uma máquina ativa, **When** o admin registra uma execução com status válido e confirma, **Then** o registro é criado, vinculado a ambos, com autor e data.
2. **Given** uma tentativa de registrar execução para máquina inexistente ou status inválido, **When** o admin confirma, **Then** o sistema exibe erro claro e **não** cria o registro.
3. **Given** uma execução registrada, **When** o admin consulta o setup ou a máquina, **Then** o histórico de execuções é exibido (mais recentes primeiro).
4. **Given** o histórico do setup, **When** existe ao menos uma execução, **Then** a "última execução" (status + resumo + data) é apresentada no setup, **derivada automaticamente** do histórico de execuções (Q3=A); enquanto **não** há execuções, mantém-se a anotação manual da feature `001` como fallback (sem regressão).

---

### User Story 3 - Proteger o arquivamento com "utilização ativa" (Priority: P2)

Um administrador que tenta **arquivar um setup** (feature `001`) que possui execuções registradas (ativas) recebe um **aviso** e decide conscientemente. O mesmo vale ao desativar uma máquina com execuções.

**Why this priority**: Concretiza o "aviso de utilização ativa" que a spec da `001` deixou como guarda futura; protege integridade sem bloquear o admin.

**Independent Test**: Pode ser testado isoladamente: com um setup/máquina possuindo execuções, o fluxo de arquivamento/desativação exibe o aviso antes de prosseguir.

**Acceptance Scenarios**:

1. **Given** um setup **sem** execuções registradas, **When** o admin arquiva, **Then** flui normalmente (como na feature `001`).
2. **Given** um setup **com** execução(ões) registrada(s), **When** o admin tenta arquivar, **Then** o sistema exibe aviso explícito contando as execuções antes de prosseguir.
3. **Given** uma máquina com execuções, **When** o admin tenta desativá-la, **Then** o sistema exibe aviso equivalente.
4. **Given** a confirmação do aviso, **When** o admin prossegue, **Then** a ação é concluída e registrada; ao cancelar, nada muda.

---

### Edge Cases

- Máquina com nome duplicado (caixa/espaços) → bloqueado (mesma regra da feature `001`).
- Execução referenciando setup arquivado ou máquina inativa → permitida com aviso, ou bloqueada [definir na clarificação].
- Duas pessoas registram execução ao mesmo tempo → "última gravação vence" (documentado).
- Máquina/setup sem execuções → nenhum aviso.
- Texto livre com caracteres especiais → aceito sem quebrar telas.
- Nenhuma credencial em qualquer campo (máquina/execução) — regra anti-segredo aplicada (FR-013).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir cadastrar, listar, editar e desativar **máquinas alvo**, com nome (obrigatório, único), identificação/endereço (obrigatório), plataforma/ambiente (valor controlado — Debian + Docker Swarm), status e descrição opcional.
- **FR-002**: O sistema DEVE permitir registrar **execuções** vinculando um setup do catálogo a uma máquina alvo, com status controlado e resumo opcional, registrando autor e data.
- **FR-003**: O sistema DEVE exibir o **histórico de execuções** por setup e por máquina (mais recentes primeiro). Nesta etapa a execução é **registro/estado (metadados)** — o administrador registra execuções com status controlado e resumo; **nenhuma execução real é disparada** (provisionamento real = Etapa 3 / feature `004`) (Q1=A).
- **FR-004**: O sistema NÃO DEVE armazenar **qualquer** credencial de máquina (senha/token/chave) nem referência a segredo; apenas **metadados** (nome, identificação/endereço, plataforma, status, descrição). A conexão real (Etapa 3) usará cofre/variáveis de ambiente, fora do escopo (Q2=A).
- **FR-005**: O arquivamento de um setup com execuções registradas DEVE exigir aviso explícito (contagem) antes de prosseguir; desativar máquina com execuções idem.
- **FR-006**: Regras anti-segredo e de auditoria (autor + data) DEVEM valer para máquinas e execuções.
- **FR-007**: Persistência durável das novas entidades (sobrevivem a reinícios).

### Key Entities *(include if feature involves data)*

- **Máquina Alvo (Target Host)**: host onde o Automatic1 pode provisionar setups (ex.: servidor Debian + Docker Swarm). Atributos: nome (único), identificação/endereço, plataforma/ambiente (controlado), status, descrição; sem credenciais. Relaciona-se com Execução (1:N).
- **Execução (Execution)**: registro de execução de um setup em uma máquina. Atributos: setup (FK), máquina (FK), status (controlado), resumo/log, autor e data. Relaciona-se com Setup de Ambiente (N:1) e Máquina Alvo (N:1).
- **Setup de Ambiente**: entidade existente (features `001`/`002`); passa a referenciar execuções (1:N) e a refletir sua última execução conforme clarificação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um administrador cadastra uma máquina alvo válida em menos de 2 minutos.
- **SC-002**: 100% das tentativas inválidas (nome duplicado, campo obrigatório ausente, status inválido) retornam mensagem acionável em nível de campo, sem criar registro indevido.
- **SC-003**: Registrar uma execução e vê-la no histórico do setup e da máquina leva menos de 1 minuto.
- **SC-004**: 100% das máquinas/execuções possuem auditoria (quem + quando).
- **SC-005**: Auditoria por amostragem não encontra credencial em máquina/execução.
- **SC-006**: 100% dos arquivamentos/desativações de registros com execuções exibem o aviso de "utilização ativa" antes de prosseguir.

## Assumptions

- A feature é **ferramenta de administração interna** (mesma premissa das features `001`/`002`): sem auth no v1, autor = operador configurado.
- **Ambiente-alvo suportado**: Debian 11/12 + Docker Swarm (decisão do usuário); valor controlado reutilizado da feature `002`.
- **Executar de fato o provisionamento** (rodar o setup) está fora do escopo desta feature (Etapa 3): aqui se registra o **modelo/vínculo** (Q1=A — registro/estado, sem execução real).
- **Nenhuma credencial** é armazenada nem referenciada — apenas metadados (Q2=A); a conexão (Etapa 3) usará cofre/variáveis de ambiente.
- **`resultado_ultima_execucao`**: derivado automaticamente da última execução registrada quando houver histórico; enquanto não há execuções, mantém a anotação manual da feature `001` como fallback (Q3=A, sem regressão na `001`).
- Regra de unicidade de nome (caixa/espaços) e anti-segredo herdadas das features anteriores.
- Idioma PT-BR.
