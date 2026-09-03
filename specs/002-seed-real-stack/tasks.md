---

description: "Task list for Catálogo Padrão do Automatic1 (002-seed-real-stack)"
---

# Tasks: Catálogo Padrão do Automatic1 (stack de referência)

**Input**: Design documents from `specs/002-seed-real-stack/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/web.md

**Tests**: Testes **incluídos** — exigidos pela constituição (Princípio III — Test-First NÃO-NEGOCIÁVEL) e pela spec (SC-002/SC-003/SC-005/SC-006).

**Organization**: Tasks grouped by user story (US1–US3) + fases transversais. US1 e US3 compartilham a rota de carga (`POST /setups/carregar-padrao`).

**Status**: ✅ **Concluído** — suíte `tests/test_catalogo_padrao.py` verde (11 testes) + regressão completa (45 passed) + `ruff` limpo.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

- **Single project (FastAPI monólito)**: `app/`, `tests/`, `scripts/` na raiz do repositório
- Estrutura completa em `plan.md`; dados em `data-model.md`; contratos em `contracts/web.md`; validação em `quickstart.md`

---

## Phase 1: Foundational (Blocking Prerequisites)

- [x] T001 [P] [FOUND] Campo `categoria` em `app/models.py` (str | None, nullable, max 32)
- [x] T002 [P] [FOUND] `CATEGORIA_VALIDOS`, `CATEGORIA_LABEL` e `rotulo_categoria()` em `app/schemas.py`
- [x] T003 [P] [FOUND] `app/catalogo_padrao.py`: `AMBIENTE_PADRAO`, `CATALOGO_PADRAO` (15 itens) e `carregar_catalogo_padrao()` (aditivo, anti-segredo, auditoria)
- [x] T004 [FOUND] Migração aditiva idempotente da coluna `categoria` em `app/database.py` (`init_db`)

**Checkpoint**: Fundação pronta.

---

## Phase 2: Testes — Vermelho (Red) ⚠️

- [x] T005 [P] [US1] `tests/test_catalogo_padrao.py` — carga inicial popula manifesto (C1/C2) — vermelho antes da rota
- [x] T006 [P] [US1] Teste de relatório criados/ignorados (C1/FR-008)
- [x] T007 [P] [US2] Testes de filtro por categoria e coluna/linha categoria (C5/C6)
- [x] T008 [P] [US3] Testes de idempotência e não destrutivo (C3/C4)
- [x] T009 [P] [FOUND] Teste unitário de anti-segredo na carga (C7/FR-010)

**Checkpoint**: Vermelho confirmado antes do core da rota/UI.

---

## Phase 3: User Story 1 - Carregar o catálogo padrão (Priority: P1) 🎯 MVP

- [x] T010 [US1] Rota `POST /setups/carregar-padrao` em `app/routers/web.py` (303 → `/setups?sucesso=catalogo_carregado&criados=N&ignorados=M[&avisos=A]`)
- [x] T011 [P] [US1] Botão/CTA "Carregar catálogo padrão" em `app/templates/setups/list.html` (cabeçalho + estado vazio)
- [x] T012 [US1] Relatório PT-BR pós-carga no `GET /setups` (FR-008/FR-014)

**Checkpoint**: US1 funcional e testada.

---

## Phase 4: User Story 2 - Identificar função e ambiente-alvo (Priority: P2)

- [x] T013 [P] [US2] Coluna "Categoria" + filtro `?categoria=` em `list.html`
- [x] T014 [US2] Filtro por categoria no `GET /setups` em `app/routers/web.py` (FR-007)
- [x] T015 [P] [US2] Linha "Categoria" em `app/templates/setups/detail.html`

**Checkpoint**: US2 funcional e testada.

---

## Phase 5: User Story 3 - Recarregar com segurança (Priority: P3)

- [x] T016 [US3] Comportamento aditivo ponta a ponta (recarga não duplica, não altera registros do usuário; relatório criados/ignorados)
- [x] T017 [US3] Auditoria em massa (`created_by`/`updated_by` = operador) + log estruturado com contagens

**Checkpoint**: US3 funcional e testada.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T018 Validação `quickstart.md` (C1–C7) + pytest verde ponta a ponta (regressão feature `001` zero)
- [x] T019 [P] Documentação no `README.md` (ação "Carregar catálogo padrão", stack, natureza aditiva, campo `categoria`)
- [x] T020 Revisão de segurança (manifesto sem segredos; `origem_asset` só referências; anti-segredo na carga)
- [x] T021 Limpeza/refatoração final + conformidade com a constituição
- [x] T022 `pytest` completo verde (45 passed) + `ruff check` limpo

---

## Dependencies & Execution Order

- Foundational → Testes (red) → US1 (MVP) → US2 → US3 → Polish
- US2/US3 compartilham `app/routers/web.py` → implementadas em sequência

---

## Notes

- Registros padrão: `plataforma_alvo = "Debian + Docker Swarm"`, `status = "ativo"`, categoria preenchida, `versao`/`hash` "não informado" (nada inventado — FR-003)
- Carga aditiva: nunca altera/remove existentes (FR-005); idempotente (FR-004)
- Fonte única do conteúdo: `app/catalogo_padrao.py`
