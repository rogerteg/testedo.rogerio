# Web Interface Contract: CRUD de Ambientes de Setup

**Branch**: `001-environment-crud` | **Date**: 2026-09-02 | **Spec**: [spec.md](../spec.md) | **Data model**: [data-model.md](../data-model.md)

Contrato da interface web server-rendered (FastAPI + Jinja2). A ferramenta é interna — sem API pública externa. Este contrato documenta **rotas/páginas** e **regras de validação** que a UI expõe e o front-end consome.

## Slices de entrega

| Slice | Prioridade | Escopo |
|-------|-----------|--------|
| **v1** | P1 | Listar + Cadastrar (US1, US2) |
| pós-v1 | P2 | Detalhes (US3) e Edição (US4) |
| pós-v1 | P3 | Arquivar/excluir (US5) |

As rotas de slices futuras estão listadas para referência, mas **só serão implementadas na sua slice**.

## Rotas / Páginas

### v1 (P1)

| Método | Caminho | Página | Descrição | Origem |
|--------|---------|--------|-----------|--------|
| GET | `/setups` | listagem | Lista setups ativos (exclui `arquivado`) com resumo (nome, plataforma, status, atualizado em), mais recentes primeiro; suporta busca por `?q=` (nome ou plataforma); estado vazio quando não há resultados | US2 |
| GET | `/setups/novo` | formulário | Formulário de cadastro (fields por [data-model](../data-model.md)); validação client + server | US1 |
| POST | `/setups` | — (redirect) | Cria o setup; em sucesso → `303 /setups` com mensagem; em erro de validação → re-render do formulário com erros por campo e **dados preservados** (FR-004) | US1 |

### Slices futuras (referência — não implementar no v1)

| Método | Caminho | Descrição | Slice |
|--------|---------|-----------|-------|
| GET | `/setups/{id}` | Detalhes completos (campos vazios → "não informado") | US3 (P2) |
| GET/POST | `/setups/{id}/editar` | Edição com mesmas validações; auditoria de autor/data | US4 (P2) |
| POST | `/setups/{id}/arquivar` | Exclusão lógica com confirmação explícita; reversível; aviso se houver utilização ativa | US5 (P3) |

## Regras de validação (server + client)

Aplicadas em `POST /setups` (e futuras edições). Erros sempre em nível de campo, com mensagem acionável (FR-004, FR-014).

| Campo | Regra |
|-------|-------|
| `nome` | Obrigatório; 1–120 chars; **único** (case/whitespace-insensitive — FR-002) |
| `plataforma_alvo` | Obrigatório; 1–60 chars |
| `origem_asset` | Obrigatório; 1–500 chars; não pode conter credenciais (FR-013) |
| `descricao` | Opcional; texto livre |
| `versao` | Opcional; **SemVer** quando preenchida (FR-003) |
| `hash` | Opcional; texto livre (checksum) |
| `licenca` | Opcional; texto livre |
| `status` | Opcional; default `rascunho`; valor ∈ {`rascunho`, `ativo`, `com_erro`, `arquivado`} |
| `resultado_ultima_execucao` | Opcional; texto livre (manual) |

## Comportamentos transversais

- **Auditoria**: criação registra `created_at`/`created_by`; futuras edições/arquivamento atualizam `updated_at`/`updated_by` (FR-011).
- **Estados de UI**: listagem vazia → estado vazio com CTA de cadastro; busca sem resultado → mensagem "nada encontrado" (FR-007).
- **Idioma**: PT-BR (research D5).
- **Feedback**: mensagens de sucesso/erro claras e acionáveis (FR-014).
