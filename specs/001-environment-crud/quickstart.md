# Quickstart: CRUD de Ambientes de Setup (validação)

**Branch**: `001-environment-crud` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

Guia de **validação ponta a ponta** do v1 (P1: **criar + listar**). Detalhes de dados e contratos estão em [data-model.md](data-model.md) e [contracts/web.md](contracts/web.md) — não duplicados aqui. Implementação detalhada fica em `tasks.md` (fase 2).

## Pré-requisitos

- Python **3.11+** e PowerShell (convenção do projeto).
- Nenhum serviço externo. SQLite local (sem instalação).

## Setup (idempotente)

```powershell
# Na raiz do repositório:
.\scripts\setup-dev.ps1        # cria .venv, instala deps (requirements*.txt), cria data/setups.db
.\scripts\test.ps1             # roda a suíte pytest (deve passar)
.\scripts\run.ps1              # sobe o servidor em http://127.0.0.1:8000
```

Esperado: bootstrap reproduzível (G2) e suíte **verde antes de qualquer código de produção** (test-first, G1).

## Cenários de validação (v1)

Cada cenário referencia o cenário de aceite correspondente na spec. Validar via UI (navegador) **e** suíte automatizada.

### C1 — Cadastrar setup válido (US1-AS1)
1. Abrir `http://127.0.0.1:8000/setups/novo`.
2. Preencher nome, plataforma alvo e origem do asset (obrigatórios) + campos opcionais.
3. Submeter.
- **Esperado**: `303 → /setups`; mensagem de sucesso; novo setup visível na listagem (primeiro da ordem, por `updated_at` desc).

### C2 — Nome duplicado (US1-AS2)
1. Cadastrar setup com nome `Dev Box`.
2. Tentar cadastrar outro com nome `dev box` (caixa/espacos diferentes).
- **Esperado**: erro em nível de campo ("nome já existe"); formulário **preserva** os dados; **nenhum** registro duplicado criado (FR-002/FR-004).

### C3 — Campo obrigatório ausente (US1-AS3)
1. Submeter formulário sem `plataforma_alvo`.
- **Esperado**: erro por campo indicando o que falta; registro **não** criado.

### C4 — Versão inválida (US1-AS4)
1. Informar `versao = 1.2` (SemVer incompleto).
- **Esperado**: erro explicando formato SemVer esperado; registro **não** criado (FR-003).

### C5 — Listagem e ordenação (US2-AS1)
1. Com ≥ 2 registros cadastrados, abrir `/setups`.
- **Esperado**: lista com nome, plataforma, status e data de atualização; mais recentes primeiro.

### C6 — Busca/filtro (US2-AS2/AS4)
1. Buscar por `q=windows` (filtra nome/plataforma).
- **Esperado**: apenas registros compatíveis. Busca sem resultado → mensagem "nada encontrado".

### C7 — Estado vazio (US2-AS3)
1. Com banco sem registros, abrir `/setups`.
- **Esperado**: estado vazio amigável com atalho para cadastro (FR-007).

## Critérios de aceite automatizados (mapeamento)

| Teste | Cobre |
|-------|-------|
| `tests/test_create_setup.py` | C1–C4 (US1) |
| `tests/test_list_setups.py` | C5–C7 (US2) |

## Fora do escopo deste guia (slices futuras)

Detalhes (US3), edição (US4) e arquivamento (US5) **não** são validados no v1; contratos já desenhados em [contracts/web.md](contracts/web.md).
