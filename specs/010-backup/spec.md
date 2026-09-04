---

description: "Feature spec for Backup/Exportação do Catálogo (010-backup)"
---

# Spec: Backup/Exportação do Catálogo

**Feature**: `010-backup` | **Branch**: `010-backup`
**Status**: Draft | **Date**: 2026-09-04

## Input / Justificativa

O catálogo (001–009) vive em SQLite local. Para **portabilidade e recuperação**
(backup/restore/migração), o operador precisa exportar o estado (setups, máquinas,
execuções) e importá-lo — sem tocar em segredos (constituição IV).

## User Stories

### US1 — Exportar snapshot (admin web)
Como administrador, quero **baixar um JSON** com setups, máquinas e execuções
(com autor/horário/meta), para backup ou migração.

- `GET /backup/exportar` → arquivo JSON (`automatic1-catalogo-<timestamp>.json`).

### US2 — Importar snapshot (admin web)
Como administrador, quero **subir um snapshot** e restaurar de forma **aditiva**
(itens existentes por nome são ignorados), com relatório de criados/ignorados.

- `POST /backup/importar` (upload multipart) → revalida anti-segredo e unicidade.

## Functional Requirements

- **FR-001**: O snapshot DEVE ter `formato`, `versao`, `exportado_em`, `por` e as
  coleções `setups`, `maquinas`, `execucoes`.
- **FR-002**: A exportação DEVE incluir execuções com referências desnormalizadas
  (`setup_nome`/`maquina_nome`) para permitir restauração com ids novos.
- **FR-003**: A importação DEVE ser **aditiva/não destrutiva**: setups/máquinas já
  existentes (nome normalizado) são ignorados; execuções só quando o par
  setup×máquina existe após o import.
- **FR-004**: A importação DEVE reaplicar anti-segredo (FR-013) e validações por
  campo; registro inválido → erro de campo com relatório (nada parcial corrompido).
- **FR-005**: Nenhum segredo DEVE sair/entrar (constituição IV).

## Non-Functional / Constraints

- Sem nova dependência; sem migração de schema (JSON ad-hoc).
- Test-first; regressão completa verde.
- Autor registrado = `OPERATOR_NAME`; reusa `validar_campos`/`validar_maquina`.

## Out of Scope

- Agendamento automático de backup (feature 012 — rotina).
- Criptografia do arquivo (assinatura/confidencialidade = responsabilidade do operador).

## Acceptance Criteria (quickstart/checklist)

- [ ] Export gera JSON com meta + 3 coleções e nomes desnormalizados nas execuções.
- [ ] Import aditivo em banco vazio cria setups/máquinas/execuções vinculadas.
- [ ] Import em banco com itens iguais os ignora (relatório correto).
- [ ] Import rejeita snapshot com segredo (sem criar itens inválidos).
- [ ] Suíte completa verde.
