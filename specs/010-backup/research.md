# Research: Backup/Exportação do Catálogo (010-backup)

**Branch**: `010-backup` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Resolve Q1–Q3 (A/A/A). Formato: *Decision / Rationale / Alternatives*.

## D1 — Formato do snapshot (Q1=A)
- **Decision**: **JSON** ad-hoc com `formato`/`versao`/`exportado_em`/`por` + coleções
  `setups`/`maquinas`/`execucoes` (execuções com `setup_nome`/`maquina_nome`).
- **Rationale**: Legível, portátil, sem dependência; nomes desnormalizados permitem
  re-vincular em ids novos no restore.
- **Alternatives**: SQL dump nativo (frágil entre versões/schemas); binário (opaco).

## D2 — Estratégia de importação (Q2=A)
- **Decision**: **Aditiva/não destrutiva**: setups/máquinas já existentes (nome
  normalizado) são ignorados; execuções importadas só quando setup×máquina existem
  após o import; relatório `criados/ignorados`.
- **Rationale**: Seguro p/ reexecução (idempotente); sem risco de sobrescrever dados.
- **Alternatives**: restore destrutivo (replace) — rejeitado (arriscado).

## D3 — Validação no import (Q3=A)
- **Decision**: Reusa `validar_campos`/`validar_maquina` (anti-segredo FR-013 e limites);
  item inválido → contabilizado e ignorado; nada parcial corrompido.
- **Rationale**: Consistência com UI/API; constituição IV.
- **Alternatives**: import cru (sem validar) — rejeitado (backdoor p/ segredo).
