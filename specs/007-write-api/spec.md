# Feature Specification: API de Escrita (Automatic1)

**Feature Branch**: `007-write-api`

**Created**: 2026-09-04

**Status**: Draft

**Input**: User description: "007 — API de escrita/operacional (evoluir a read-only da feature 006)". A API REST (`006`) hoje é **somente leitura**. Esta feature adiciona **operações de escrita** (criar setups/máquinas, registrar execuções) via API, autenticadas por **token próprio de escrita**, reutilizando as mesmas regras de validação/anti-segredo/auditoria da UI (features `001`–`004`) — para integração externa sem expor a UI.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Criar setups e máquinas via API (Priority: P1)

Um sistema externo cria **setups** (com as mesmas validações da UI: nome único, campos obrigatórios, SemVer, anti-segredo) e **máquinas alvo** (sem credenciais) via API autenticada por **token de escrita**, recebendo respostas JSON claras.

**Why this priority**: É a escrita fundamental — permite alimentar o catálogo/máquinas por integração sem passar pela UI.

**Independent Test**: Pode ser testado isoladamente: `POST /api/setups` e `/api/maquinas` com token de escrita criam registros válidos; inválidos retornam erros por campo sem criar.

**Acceptance Scenarios**:

1. **Given** um token de escrita válido, **When** um cliente envia um setup/máquina válido (JSON), **Then** o registro é criado e a resposta é `201` com o recurso (JSON).
2. **Given** dados inválidos (nome duplicado, campo obrigatório ausente, SemVer inválida, segredo em campo), **When** enviados, **Then** a resposta é erro claro (`400`/`409`/`422`) com mensagem por campo e **nada** é criado.
3. **Given** uma máquina com campo de credencial, **When** enviada, **Then** é rejeitada (constituição IV) — nunca aceita credencial.
4. **Given** uma chamada de escrita **sem** token (ou com token de leitura apenas), **When** enviada, **Then** a resposta é `401`/`403` clara.

---

### User Story 2 - Registrar execução via API (Priority: P1)

Um sistema externo registra uma **execução** (setup × máquina ativa) com status e resumo (feature `003`), pelas mesmas regras da UI.

**Why this priority**: Habilita alimentar o histórico de execuções de fora (ex.: runners externos/CI).

**Independent Test**: Pode ser testado isoladamente: `POST /api/execucoes` cria a execução e ela aparece no histórico (setup/máquina).

**Acceptance Scenarios**:

1. **Given** setup e máquina ativa válidos, **When** o cliente registra uma execução (JSON), **Then** `201` e o registro aparece no histórico.
2. **Given** máquina inexistente/inativa ou status inválido, **When** enviado, **Then** erro claro (`400`/`404`/`409`) e **nada** é criado.
3. **Given** resumo com segredo, **When** enviado, **Then** rejeitado (anti-segredo) sem criar.

---

### User Story 3 - Operar com segurança e auditoria (Priority: P2)

Toda escrita via API exige **token de escrita** (separado do de leitura), registra **autor** na auditoria (mantém `OPERATOR_NAME`) e não expõe segredos em respostas/erros.

**Why this priority**: Garante que a superfície de escrita externa seja segura e auditável (FR-004/006 da feature `006` estendidos).

**Independent Test**: Pode ser testado isoladamente: escrita com token de leitura → `403`; com token de escrita → operação concluída e autor registrado.

**Acceptance Scenarios**:

1. **Given** um token de **leitura** (`006`) usado numa escrita, **When** enviado, **Then** `403` (escopo) — sem efeito.
2. **Given** uma escrita autenticada concluída, **When** verificada, **Then** a auditoria registra o autor configurado (`OPERATOR_NAME`) — igual à UI.
3. **Given** erros da API, **When** retornados, **Then** **nenhum segredo** aparece no corpo/erro.

---

### Edge Cases

- Token de escrita ausente/inválido → `401`; token de leitura usado em escrita → `403`.
- Sem `AUTOMATIC1_WRITE_API_TOKEN` configurado → escrita bloqueada (FR-007 estendido; nunca aceitar vazio).
- Payload JSON malformado → `422` claro.
- Concorrência: criar setup com mesmo nome simultaneamente → regra de unicidade (app-level) pode duplicar em corrida (aceito/documentado, como na UI).
- Rejeitar credencial em qualquer campo (anti-segredo) e **nunca** persistir.
- Erros por campo em PT-BR (consistente com a UI).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE expor operações de **escrita** via API (JSON): criar **setup**, criar **máquina alvo** e **registrar execução** (Q1=A). Editar/arquivar/desativar e disparar provisionamento via API ficam para escopo posterior.
- **FR-002**: Escritas DEVEM exigir um **token de escrita** (cabeçalho `Authorization: Bearer`), separado do token de leitura (`006`) — **novo `AUTOMATIC1_WRITE_API_TOKEN`** (Q2=A).
- **FR-003**: As escritas DEVEM reutilizar as **mesmas validações** da UI (`validar_campos`/`validar_maquina`/`validar_execucao` + unicidade + anti-segredo) e registrar **autor** (`OPERATOR_NAME`).
- **FR-004**: Respostas JSON claras: `201` (criado, com recurso), `422` (validação) com **erros por campo** `{"campo": "mensagem"}`, `409` (duplicado), `401`/`403` (auth/escopo), `404` (inexistente) — sem segredos (Q3=A).
- **FR-005**: Criar máquina via API NÃO DEVE aceitar credenciais (constituição IV) — mesmos campos/regras da UI.
- **FR-006**: Sem token de escrita configurado (`AUTOMATIC1_WRITE_API_TOKEN`) → escrita bloqueada (nunca aceitar vazio).

### Key Entities *(include if feature involves data)*

- Entidades existentes (`EnvironmentSetup`, `TargetHost`, `Execution`) — alvos das escritas via API.
- **Token de Escrita**: credencial para escrita (`AUTOMATIC1_WRITE_API_TOKEN`) — não persistida (ambiente), separada do token de leitura.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Criar um setup/máquina válido via API retorna `201` em < 1s.
- **SC-002**: 100% das tentativas inválidas (duplicado, obrigatório ausente, SemVer, anti-segredo, credencial em máquina) retornam erro claro por campo e **nada** é criado.
- **SC-003**: 100% das escritas exigem token de escrita; token de leitura em escrita → `403`; sem token → `401`.
- **SC-004**: 100% das escritas registram autor (`OPERATOR_NAME`) — auditoria consistente com a UI.
- **SC-005**: Auditoria por amostragem não encontra segredo em corpo/erro/resposta da API.
- **SC-006**: Sem `AUTOMATIC1_WRITE_API_TOKEN` → escrita bloqueada (0 escrita com token vazio).

## Assumptions

- Ferramenta interna; **um operador** (autoria = `OPERATOR_NAME`, decisão da feature `006` mantida).
- API **JSON**; mensagens de validação **PT-BR** por campo (consistente com a UI).
- Token de escrita por **variável de ambiente** (`AUTOMATIC1_WRITE_API_TOKEN`, constituição IV); rotação por deploy. Token de leitura usado em escrita → `403`; sem/outro token → `401`.
- **Decisões**: Q1=A (criações + registrar execução); Q2=A (token de escrita separado); Q3=A (erros por campo, `422` validação / `409` duplicado).
- Manter compatibilidade: endpoints de leitura (`006`) inalterados; escritas **aditivas**.
- Disparar provisionamento real via API e editar/arquivar via API ficam para escopo posterior (conforme clarificação Q1).
