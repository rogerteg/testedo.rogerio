# Feature Specification: Execução Assíncrona do Provisionamento (Automatic1)

**Feature Branch**: `008-async-provisioning`

**Created**: 2026-09-04

**Status**: Draft

**Input**: User description: "008 — execução assíncrona do provisionamento". Hoje o provisionador (`004`) executa **de forma síncrona dentro do request** (`POST /setups/{id}/provisionar` bloqueia até terminar). Esta feature move a execução para **segundo plano (assíncrono)**: o disparo retorna imediatamente, o provisionamento roda em worker e a `Execution` evolui `em_andamento → sucesso/erro`, com acompanhamento do progresso na UI/API sem travar a interface.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Disparar provisionamento sem bloquear (Priority: P1)

Um operador dispara o provisionamento de um setup numa máquina e **recebe retorno imediato** ("execução iniciada"), podendo acompanhar o andamento; a interface/request **não fica presa** até o fim do job.

**Why this priority**: Provisionamentos podem ser longos; bloquear o request degrada a UX e arrisca timeouts.

**Independent Test**: Pode ser testado isoladamente com um runner que registra progresso em etapas: o disparo retorna rápido (status/`em_andamento`) e a `Execution` é concluída por um worker.

**Acceptance Scenarios**:

1. **Given** um setup e máquina válidos, **When** o operador dispara o provisionamento, **Then** a resposta é imediata (não aguarda o fim) e a `Execution` nasce `em_andamento`.
2. **Given** a execução em andamento, **When** o operador consulta, **Then** vê o status atual e (quando houver) o log parcial — sem precisar recarregar a ação.
3. **Given** a conclusão do worker, **When** a execução termina, **Then** a `Execution` fica `sucesso`/`erro` com log completo e horários (regras da `004` mantidas).
4. **Given** um processo reiniciado com execuções órfãs (`em_andamento` sem worker), **When** o sistema inicia, **Then** elas são marcadas como `erro`/interrompidas com aviso (recuperação determinística).

---

### User Story 2 - Acompanhar progresso (UI e API) (Priority: P2)

O operador (UI) e sistemas externos (API) **consultam o status/log** de uma execução assíncrona em andamento, com atualização periódica, até a conclusão.

**Why this priority**: Sem leitura de progresso, o disparo assíncrono seria "fire and forget"; o acompanhamento dá confiança e permite detectar falhas.

**Independent Test**: Pode ser testado isoladamente: durante uma execução (runner com passos), consultar status reflete progresso; ao final, o estado é terminal.

**Acceptance Scenarios**:

1. **Given** uma execução em andamento, **When** a UI/API consulta o status, **Then** recebe `em_andamento` (+ log parcial se disponível).
2. **Given** a execução concluída, **When** consultada, **Then** o status é terminal (`sucesso`/`erro`) com log completo.
3. **Given** a página do setup/máquina, **When** há execução em andamento, **Then** a UI permite **acompanhar/atualizar** o andamento (polling) sem bloqueio.

---

### User Story 3 - Concorrência e robustez (Priority: P2)

A fila/worker respeita a regra de **uma execução `em_andamento` por par setup×máquina** (`004`) e lida com falhas de worker/reinício sem perder o histórico.

**Why this priority**: Garante SC-006 da `004` (sem corromper estado) e recuperação após falhas.

**Independent Test**: Pode ser testado isoladamente: disparo duplo do mesmo par é bloqueado enquanto o primeiro está em andamento; reinício simulado recupera órfãs.

**Acceptance Scenarios**:

1. **Given** uma execução em andamento num par, **When** há novo disparo do mesmo par, **Then** é bloqueado com mensagem clara.
2. **Given** uma execução órfã (worker morreu), **When** o sistema reinicia, **Then** ela é marcada como interrompida/erro e o par volta a aceitar novos disparos.

---

### Edge Cases

- Worker reiniciado no meio → recuperação de `em_andamento` órfãs no startup.
- Dois disparos simultâneos do mesmo par → regra de concorrência (`004`) mantém 1 ativo.
- Execução muito longa → continua em background; acompanhamento por polling; sem timeout de request.
- Runner com falha → `erro` com log (regras `004`).
- Sem runner/credencial → bloqueio antes de enfileirar (guardas `004` mantidas).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O disparo de provisionamento DEVE retornar **imediatamente** (não aguardar o fim), criando/retornando a `Execution` em `em_andamento` e processando em **segundo plano** [NEEDS CLARIFICATION: mecanismo de execução em background — (a) **fila em processo (worker em threads)** simples, sem serviço externo, com recuperação de órfãs no startup (recomendado p/ o v1), (b) **fila externa** (ex.: Redis/worker dedicado) robusta para escala, ou (c) outra?].
- **FR-002**: O sistema DEVE permitir **acompanhar** o status/log da execução em andamento (UI e API) e concluir com estado terminal (`sucesso`/`erro`) + log completo [NEEDS CLARIFICATION: modelo de acompanhamento — (a) **polling** (UI atualiza periodicamente/recarrega status; API retorna status sob demanda) (recomendado), (b) **tempo real** (SSE/websocket), ou (c) apenas refresh manual?].
- **FR-003**: A regra de **concorrência** (`004`: no máx. 1 `em_andamento` por par) DEVE continuar valendo para o disparo assíncrono.
- **FR-004**: O sistema DEVE **recuperar** execuções órfãs (`em_andamento` sem worker) no startup, marcando-as como interrompidas/erro e liberando o par.
- **FR-005**: Guardas da `004` (setup não arquivado, máquina ativa, origem `.sh`, credencial configurada) DEVEM ocorrer **antes** de enfileirar (sem efeito colateral).
- **FR-006**: Auditoria/autor, log sanitizado e `Execution` real (horários/exit_code) permanecem como na `004`; o disparo registra autor.
- **FR-007**: O acompanhamento na API/UI não expõe segredos (log sanitizado — `004`) [NEEDS CLARIFICATION: forma do contrato de disparo/acompanhamento — (a) **`202 Accepted`** no disparo + consulta de status (UI e API) por id (recomendado), (b) outros?].

### Key Entities *(include if feature involves data)*

- **Execution** (`003`/`004`): evolui de `em_andamento` para terminal pelo worker; suporta log parcial (polling).
- **Fila/Worker (conceitual)**: processa provisionamentos em background; não é entidade persistida (v1) — estado refletido na `Execution`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O disparo de provisionamento retorna em < 2s (não aguarda o job).
- **SC-002**: 100% das execuções assíncronas terminam em estado terminal (`sucesso`/`erro`) com log completo (ou são recuperadas como interrompidas em reinício).
- **SC-003**: 0 execuções órfãs persistentes após reinício (recuperadas no startup).
- **SC-004**: 100% dos disparos duplicados do mesmo par em andamento são bloqueados.
- **SC-005**: Polling (UI/API) reflete progresso (`em_andamento` → terminal) sem expor segredos.
- **SC-006**: Regressão `001`–`007` = 0.

## Assumptions

- Ferramenta interna de baixo volume → **fila em processo** (worker em threads) no v1, com recuperação de órfãs; fila externa quando houver escala (Q1).
- Acompanhamento por **polling** (UI + API por id) — simples e suficiente (Q2).
- **Disparo assíncrono é o padrão** do provisionador; testes usam worker determinístico (processar inline) para validar o fluxo sem timing.
- Sem novas credenciais/segredos; guardas e sanitização da `004` mantidas.
