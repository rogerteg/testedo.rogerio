# Quickstart: Catálogo Padrão do Automatic1 (validação)

**Branch**: `002-seed-real-stack` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Guia de **validação ponta a ponta** da feature. Detalhes de dados e contratos em [data-model.md](data-model.md) e [contracts/web.md](contracts/web.md) — não duplicados aqui. Implementação detalhada em `tasks.md` (fase 2).

## Pré-requisitos

- Python **3.11+** e PowerShell (convenção do projeto).
- Nenhum serviço externo. SQLite local.

## Setup (idempotente)

```powershell
# Na raiz do repositório:
.\scripts\setup-dev.ps1        # cria .venv, instala deps, cria data/setups.db
.\scripts\test.ps1             # roda a suíte pytest (deve passar)
.\scripts\run.ps1              # sobe o servidor em http://127.0.0.1:8000
```

Esperado: bootstrap reproduzível (G2) e suíte **verde** (test-first, G1).

## Cenários de validação

Cada cenário referencia o cenário de aceite da spec. Validar via UI (navegador) **e** suíte automatizada.

### C1 — Carregar o catálogo padrão em ambiente vazio (US1-AS1)
1. Com o banco sem registros, abrir `http://127.0.0.1:8000/setups`.
2. Clicar em **"Carregar catálogo padrão"** (CTA do estado vazio ou botão do cabeçalho).
- **Esperado**: redireciona para a listagem com relatório (ex.: "15 criados, 0 ignorados"); a stack padrão completa aparece com `plataforma_alvo = Debian + Docker Swarm` e badge de categoria.

### C2 — Proveniência dos registros padrão (US1-AS2/AS3)
1. Abrir um registro padrão (ex.: `N8N`) na listagem → detalhe.
- **Esperado**: `origem_asset` aponta para o upstream (ex.: `https://github.com/n8n-io/n8n`); versão/hash "não informado" (nenhum valor inventado); licença exibida quando conhecida.

### C3 — Idempotência: recarregar não duplica (US3-AS1)
1. Com o catálogo padrão já carregado, clicar novamente em **"Carregar catálogo padrão"**.
- **Esperado**: relatório "0 criados, 15 ignorados"; **nenhum** duplicado na listagem (FR-004).

### C4 — Não destrutivo: registro do usuário preservado (US3-AS2)
1. Cadastrar manualmente um setup com nome que colida com um padrão (ex.: `n8n`).
2. Clicar em **"Carregar catálogo padrão"**.
- **Esperado**: relatório indica `1 ignorado` (o `n8n` existente); o registro do usuário **não** é alterado nem removido (FR-005).

### C5 — Categoria e ambiente-alvo (US2-AS1/AS2)
1. Na listagem, filtrar por `categoria` = "Infraestrutura base" e depois "Aplicação".
- **Esperado**: apenas os compatíveis; cada registro padrão mostra categoria e a plataforma consistente `Debian + Docker Swarm`.

### C6 — Detalhe com categoria (US2 / FR-006)
1. Abrir o detalhe de um registro padrão e de um registro manual.
- **Esperado**: o padrão exibe a categoria; o manual exibe "não classificada" — sem erros.

### C7 — Anti-segredo na carga (FR-010 — automatizado)
- **Esperado (suíte)**: um item do manifesto adulterado com texto de segredo **não** é criado e é reportado em `avisos` (defesa em profundidade; em operação normal `avisos=0`).

## Critérios de aceite automatizados (mapeamento)

| Teste (proposto) | Cobre |
|------------------|-------|
| `tests/test_catalogo_padrao.py` | C1–C7 (US1–US3) + filtro por categoria |

## Fora do escopo deste guia

Provisionamento/execução real (rodar setups) **não** é validado aqui — a carga cria apenas registros de catálogo (FR-011).
