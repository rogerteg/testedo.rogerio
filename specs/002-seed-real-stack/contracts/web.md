# Web Interface Contract: Catálogo Padrão do Automatic1

**Branch**: `002-seed-real-stack` | **Date**: 2026-09-03 | **Spec**: [spec.md](../spec.md) | **Data model**: [data-model.md](../data-model.md)

Contrato da interface web server-rendered (FastAPI + Jinja2). Evolui o contrato da feature `001` ([contracts/web.md](../../001-environment-crud/contracts/web.md)); mudanças são **aditivas** e não alteram rotas existentes.

## Rotas / Páginas

### Novas / alteradas (002)

| Método | Caminho | Página | Descrição | Origem |
|--------|---------|--------|-----------|--------|
| POST | `/setups/carregar-padrao` | — (redirect) | Carrega o **catálogo padrão** (US1/US3): aditivo e não destrutivo (FR-004/FR-005); em sucesso → `303 /setups?sucesso=catalogo_carregado&criados=N&ignorados=M&avisos=A` | US1, US3 |
| GET | `/setups` | listagem *(alterada)* | Parâmetro opcional `?categoria=infraestrutura_base\|aplicacao` (filtro — US2, FR-007), mantendo `?q=`. Nova coluna "Categoria" e botão/CTA "Carregar catálogo padrão" (US1). Aceita `?sucesso=catalogo_carregado` com contagens | US1–US3 |
| GET | `/setups/{id}` | detalhe *(alterada)* | Exibe a linha "Categoria" (rótulo PT-BR ou "não classificada") | US2 |

### Inalteradas (feature `001`)

`GET /setups/novo`, `POST /setups`, `GET /setups/{id}/editar`, `POST /setups/{id}/editar`, `POST /setups/{id}/arquivar` — sem mudança de contrato.

## Regras de validação (server)

- **Carga do catálogo padrão** (server-only, sem formulário do usuário):
  - Cada item do manifesto passa pela regra **anti-segredo** (`contem_segredo`) nos campos de texto; item suspeito **não é criado** e vira `avisos` (FR-010).
  - Identidade de não-duplicação: nome **único** (case/whitespace-insensitive — FR-004, mesma regra da `001`).
  - Nenhum registro existente é alterado/removido (FR-005). Sempre idempotente.
- **Filtro de listagem**: `categoria` ∈ {`infraestrutura_base`, `aplicacao`}; valor vazio/ausente = todas. `q` continua filtrando nome/plataforma.

## Relatório da carga (feedback)

A mensagem pós-carga informa, em PT-BR: quantos registros foram **criados**, quantos **ignorados** (já existiam) e eventuais **avisos** (ex.: item bloqueado por suspeita de segredo) — FR-008/FR-014.

## Comportamentos transversais

- **Auditoria**: itens criados pela carga registram `created_by`/`updated_by` = operador configurado e timestamps (FR-009).
- **Estados de UI**: estado vazio ganha CTA secundário "Carregar catálogo padrão" (além de "+ Novo setup"); botão dedicado também presente no cabeçalho da listagem para recarga.
- **Idioma**: PT-BR.
