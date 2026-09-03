---

description: "Task list for CRUD de Ambientes de Setup (Automatic1) — 001-environment-crud"
---

# Tasks: CRUD de Ambientes de Setup (Automatic1)

**Input**: Design documents from `specs/001-environment-crud/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Testes **incluídos** — solicitados pelo usuário (ordem "Setup → Testes → Core P1") e exigidos pela constituição (Princípio III — Test-First NÃO-NEGOCIÁVEL). Cada teste é escrito **antes** da implementação que valida e deve **falhar (red)** primeiro.

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

**v1 (MVP)**: User Story 1 + User Story 2 (P1 — criar + listar). Slices futuras (US3–US5) estão listadas em fases próprias e só devem ser implementadas após o v1 validado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project (FastAPI monólito)**: `app/`, `tests/`, `scripts/` na raiz do repositório
- Estrutura completa em `plan.md`; modelo de dados em `data-model.md`; contratos em `contracts/web.md`; cenários de validação em `quickstart.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialização do projeto (estrutura, dependências, scripts reproduzíveis — constituição G2)

- [x] T001 Crie a estrutura de diretórios do projeto conforme plan.md (`app/`, `app/routers/`, `app/templates/setups/`, `app/static/`, `tests/`, `scripts/`, `data/`)
- [x] T002 [P] Crie `pyproject.toml` (PEP 621): metadados (nome, versão SemVer `0.1.0`), deps runtime (fastapi, sqlmodel, uvicorn[standard], jinja2, python-multipart), deps dev (pytest, httpx) e `[tool.pytest.ini_options]` com `testpaths = ["tests"]`
- [x] T003 [P] Crie `scripts/setup-dev.ps1` (bootstrap idempotente: cria `.venv`, instala deps, cria `data/`, valida import da app)
- [x] T004 [P] Crie `scripts/run.ps1` (executa `uvicorn app.main:app --reload` em `127.0.0.1:8000`)
- [x] T005 [P] Crie `scripts/test.ps1` (executa `pytest`)
- [x] T006 [P] Crie `.gitignore` (ignora `.venv/`, `__pycache__/`, `.pytest_cache/`, `data/*.db`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura compartilhada que DEVE estar pronta antes de qualquer user story (DB, modelo, schemas, app, layout base, fixtures de teste)

**⚠️ CRITICAL**: Nenhuma user story pode começar até esta fase terminar

- [x] T007 Crie `app/__init__.py` e `app/config.py` com `Settings` (DB_PATH=`data/setups.db`, OPERATOR_NAME default `admin`, APP_VERSION lida do pyproject)
- [x] T008 [P] Crie `app/database.py` (engine SQLite, `create_all` idempotente no startup, dependência `get_session`)
- [x] T009 [P] Crie `app/models.py` com `EnvironmentSetup` (SQLModel) com os campos do `data-model.md`
- [x] T010 [P] Crie `app/schemas.py` (validação Pydantic: enum de `status` default `rascunho`, regex SemVer p/ `versao`, normalização de `nome` para unicidade, regra anti-segredo — FR-013)
- [x] T011 [P] Crie `app/main.py` (app FastAPI com templates Jinja2, static, `include_router(web)`, startup `init_db`) e `app/routers/__init__.py`
- [x] T012 [P] Crie `app/routers/web.py` com rota de health/placeholder (rotas reais nas fases de user story)
- [x] T013 [P] Crie `app/templates/base.html` e `app/static/app.css` (layout base PT-BR com blocos para conteúdo e mensagens de feedback)
- [x] T014 [P] Crie `tests/conftest.py` (fixtures: SQLite temporário isolado por teste, `TestClient`, helper `criar_setup` para semear dados)

**Checkpoint**: Fundação pronta — user stories podem começar; testes vermelhos devem ser escritos antes do core.

---

## Phase 3: Testes P1 — Vermelho (Red) ⚠️

**Purpose**: Cenários de aceite das US1/US2 (P1) escritos como testes que **falham** antes da implementação (Test-First, constituição III)

> **NOTE**: Escreva estes testes AGORA e confirme que FALHAM (red) antes de implementar o core

- [x] T015 [P] [US1] Escreva testes de criação em `tests/test_create_setup.py`: criação válida, nome duplicado (caixa/espaços), campo obrigatório ausente, versão SemVer inválida (cenários C1–C4 do quickstart) — devem falhar
- [x] T016 [P] [US2] Escreva testes de listagem em `tests/test_list_setups.py`: ordenação (mais recente primeiro), filtro por nome/plataforma, estado vazio e busca sem resultado (cenários C5–C7 do quickstart) — devem falhar

**Checkpoint**: Testes vermelhos confirmados (pytest falha pelo motivo correto).

---

## Phase 4: User Story 1 - Cadastrar um novo setup de ambiente (Priority: P1) 🎯 MVP

**Goal**: Administrador cadastra um setup via formulário com validação (nome único, SemVer, campos obrigatórios) e auditoria.

**Independent Test**: `pytest tests/test_create_setup.py` verde (criação persistida/validada; `303 → /setups`). O fluxo manual completo (quickstart C1–C4) é validado ao fim da US2 (a listagem é o destino do redirect).

- [x] T017 [US1] Implemente a rota `GET /setups/novo` (renderiza `form.html` com os campos do `data-model.md`) em `app/routers/web.py`
- [x] T018 [P] [US1] Crie o template do formulário em `app/templates/setups/form.html` (PT-BR, preserva dados preenchidos em caso de erro — FR-004)
- [x] T019 [US1] Implemente `POST /setups` em `app/routers/web.py`: valida via `app/schemas.py` (T010), trata duplicado/SemVer/campos ausentes com erro por campo, registra `created_at`/`created_by` (OPERATOR_NAME), redireciona `303 → /setups` com mensagem de sucesso (depende de T017)
- [x] T020 [US1] Adicione mensagens de sucesso/erro acionáveis (FR-014) e logging estruturado da criação em `app/routers/web.py` e exibição no `app/templates/base.html`

**Checkpoint**: User Story 1 funcional e testada isoladamente (testes verdes).

---

## Phase 5: User Story 2 - Listar setups de ambiente cadastrados (Priority: P1) 🎯 MVP

**Goal**: Administrador vê todos os setups ativos (exceto `arquivado`) em resumo, ordenados do mais recente, com busca por nome/plataforma e estados vazios.

**Independent Test**: `pytest tests/test_list_setups.py` verde (dados semeados via fixture). Fluxo manual quickstart C5–C7.

- [x] T021 [US2] Implemente a rota `GET /setups` em `app/routers/web.py`: lista setups com status != `arquivado`, ordena por `updated_at` desc, aplica filtro `?q=` em nome/plataforma (contrato em `contracts/web.md`)
- [x] T022 [P] [US2] Crie o template `app/templates/setups/list.html` (tabela resumo: nome, plataforma, status, atualizado em; estado vazio com CTA de cadastro — FR-007; mensagem "nada encontrado")
- [x] T023 [US2] Integre o fluxo ponta a ponta: confirme o redirect pós-cadastro exibindo a mensagem de sucesso na listagem e o link "novo setup"; rode a validação do `quickstart.md` (C1–C7)

**Checkpoint**: **v1 (US1 + US2) completo e validado** — MVP pronto.

---

## Phase 6: User Story 3 - Visualizar detalhes de um setup (Priority: P2) — slice futura

**Goal**: Administrador abre `/setups/{id}` e vê os detalhes completos; campos vazios aparecem como "não informado".

**Independent Test**: Teste de detalhe verde + abrir um registro na UI.

- [x] T024 [P] [US3] Escreva testes de detalhe em `tests/test_detail_setup.py` (renderiza todos os campos; campos vazios → "não informado"; id inexistente → erro amigável) — devem falhar
- [x] T025 [US3] Implemente a rota `GET /setups/{id}` em `app/routers/web.py` (detalhes completos)
- [x] T026 [P] [US3] Crie o template `app/templates/setups/detail.html` (campos opcionais vazios → "não informado")
- [x] T027 [US3] Adicione o link "detalhes" em `app/templates/setups/list.html`

**Checkpoint**: User Story 3 funcional e testada isoladamente.

---

## Phase 7: User Story 4 - Editar um setup existente (Priority: P2) — slice futura

**Goal**: Administrador edita um setup com as mesmas validações do cadastro; auditoria de `updated_at`/`updated_by`.

**Independent Test**: Teste de edição verde + editar via UI (duplicado e SemVer inválida bloqueados).

- [x] T028 [P] [US4] Escreva testes de edição em `tests/test_edit_setup.py` (edição válida, renomear p/ nome duplicado bloqueado, atualização de auditoria) — devem falhar
- [x] T029 [US4] Implemente a rota `GET /setups/{id}/editar` em `app/routers/web.py` (form pré-preenchido, reutiliza `form.html`)
- [x] T030 [US4] Implemente `POST /setups/{id}/editar` em `app/routers/web.py` (mesmas validações de T010, sem atualização parcial em erro — FR-009, registra `updated_by`/`updated_at`)
- [x] T031 [US4] Atualize `app/templates/setups/detail.html`/`list.html` com link "editar"

**Checkpoint**: User Story 4 funcional e testada isoladamente.

---

## Phase 8: User Story 5 - Excluir (arquivar) um setup (Priority: P3) — slice futura

**Goal**: Administrador arquiva um setup (status `arquivado`) com confirmação explícita; sai da listagem ativa e permanece recuperável/auditável.

**Independent Test**: Teste de arquivamento verde + arquivar via UI com confirmação (e aviso se houver utilização ativa).

- [x] T032 [P] [US5] Escreva testes de arquivamento em `tests/test_archive_setup.py` (requer confirmação; sai da listagem ativa; cancelamento não altera; aviso em utilização ativa) — devem falhar
- [x] T033 [US5] Implemente `POST /setups/{id}/arquivar` em `app/routers/web.py` (exige confirmação explícita; marca status `arquivado`; mantém registro recuperável/auditável — FR-010; avisa se houver utilização ativa registrada)
- [x] T034 [US5] Adicione o fluxo de confirmação e o link "arquivar" em `app/templates/setups/detail.html`/`list.html`

**Checkpoint**: User Story 5 funcional e testada isoladamente.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Melhorias transversais e validação final (constituição: observabilidade, segurança, qualidade)

- [x] T035 Rode a validação completa do `quickstart.md` (todos os cenários C1–C7 do v1) e confirme a suíte `pytest` verde de ponta a ponta
- [x] T036 [P] Documente uso e recuperação de falhas em `README.md` na raiz (pré-requisitos, setup, run, test, mensagens de erro esperadas)
- [x] T037 Revise segurança: nenhum segredo em código/logs (FR-013), dependências pinadas e revisadas (constituição IV), app sem auth documentada como interna
- [x] T038 Limpeza/refatoração final e revisão de conformidade com a constituição (dead code, nomes, logs estruturados)
- [x] T039 Rode `pytest` completo uma última vez e confirme 100% verde (regressão zero)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **Testes P1 (Phase 3)**: Depends on Foundational (fixtures T014); testes DEVEM falhar antes do core
- **User Stories (Phase 4+)**: All depend on Foundational completion
  - US1 + US2 (P1) = **v1/MVP** — implementadas em sequência (US1 → US2) pois compartilham `app/routers/web.py` e o redirect pós-cadastro depende da listagem
  - US3 (P2), US4 (P2), US5 (P3) = **slices futuras** — só após o v1 validado
- **Polish (Phase 9)**: Depends on todas as user stories desejadas completas

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (verificação automática isolada via `tests/test_create_setup.py`)
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Destino do redirect da US1 (validação E2E conjunta no fim do v1)
- **User Story 3 (P2)**: Depends on US2 (link de detalhe na listagem) - independently testable
- **User Story 4 (P2)**: Depends on US3 (form pré-preenchido a partir do detalhe) - mesmas validações da US1
- **User Story 5 (P3)**: Depends on US3/US4 (ação a partir do detalhe) - exclusão lógica via `status=arquivado`

### Within Each User Story

- Tests MUST be written and FAIL before implementation (red-green)
- Schemas/model antes de rotas (garantidos nas fases Foundational + ordem das tasks)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Testes P1 (T015, T016) can run in parallel
- Templates ([P]) podem ser criados em paralelo com suas rotas (arquivos distintos)
- Different user stories can be worked on in parallel by different team members **somente após** o v1 (risco de conflito em `app/routers/web.py` entre US1/US2)

---

## Parallel Example: v1 (User Story 1 + 2)

```bash
# Launch all P1 tests together (red first):
Task: "Write creation tests in tests/test_create_setup.py"
Task: "Write listing tests in tests/test_list_setups.py"

# Templates can be authored in parallel with their routes:
Task: "Create app/templates/setups/form.html"
Task: "Create app/templates/setups/list.html"
```

---

## Implementation Strategy

### MVP First (v1 = User Story 1 + User Story 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Write Phase 3: Testes P1 (red) → confirme que falham
4. Complete Phase 4: User Story 1 (create) → testes verdes
5. Complete Phase 5: User Story 2 (list) → v1 E2E validado via quickstart.md (C1–C7)
6. **STOP and VALIDATE**: MVP (criar + listar) pronto para demo/uso

### Incremental Delivery (slices futuras)

1. Complete Setup + Foundational → Foundation ready
2. v1 (US1 + US2) → Testar → Demo (MVP)
3. Add US3 (detalhes, P2) → Testar independente
4. Add US4 (editar, P2) → Testar independente
5. Add US5 (arquivar, P3) → Testar independente
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. After Foundational: escrever testes vermelhos juntos (Phase 3)
3. Após o v1 (US1+US2) validado, slices futuras podem ser distribuídas:
   - Developer A: US3 (detalhes)
   - Developer B: US4 (editar) — depende da US3
   - Developer C: US5 (arquivar)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Test-First, constituição III)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- v1 = US1 + US2 (P1); US3–US5 são slices futuras (P2/P3) — não implementar antes do v1
- Avoid: vague tasks, same file conflicts (US1/US2 no mesmo `web.py` → sequencial), cross-story dependencies that break independence

---

## Phase 10: Convergence

**Purpose**: Trabalho remanescente identificado pelo `/speckit-converge` (análise código × spec/plan/tasks × constituição) após a implementação. Anexado em 2026-09-02; IDs continuam após T039.

- [x] T040 CRITICAL: Adicione pipeline de CI (`.github/workflows/ci.yml`) que rode `uv sync` + `pytest` e um check estático (ex.: ruff) em push/PR, para que testes e checagens estáticas passem em CI antes do merge per plan G1 / Constitution Workflow (implementado: uv sync --frozen → ruff check → pytest; ruff 0.16 no grupo dev + per-file-ignores B008 p/ FastAPI; 21 testes verdes)
- [x] T041 Aplique os limites máximos de caracteres dos campos opcionais (`descricao` ≤ 2000, `versao` ≤ 64, `hash` ≤ 256, `licenca` ≤ 500, `resultado_ultima_execucao` ≤ 1000) em `app/schemas.py::validar_campos` e cubra com testes em `tests/` per data-model.md / plan constraints (implementado: LIMITES_OPCIONAIS em schemas.py + tests/test_schemas.py; 31 testes verdes)
- [x] T042 Adicione auditoria automatizada por amostragem de segredos nos registros (ex.: script `scripts/audit-secrets.ps1` ou passo de CI que varre `data/setups.db` em busca de padrões de credenciais) per SC-005 (implementado: app/security_audit.py + scripts/audit_secrets.py + scripts/audit-secrets.ps1 + tests/test_security_audit.py; 34 testes verdes)
