# Data Model / Config: API de Escrita (007)

**Branch**: `007-write-api` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

**Sem novas entidades nem migração.** Entidades existentes (`EnvironmentSetup`, `TargetHost`, `Execution`) são alvos das escritas via API com as mesmas regras da UI.

## Configuração nova

| Variável | Default | Descrição |
|----------|---------|-----------|
| `AUTOMATIC1_WRITE_API_TOKEN` | — | Token da API de escrita (Bearer); separado do de leitura (`006`) |

- Token de leitura em escrita → `403`; ausente/outro → `401`; sem token configurado → escrita bloqueada (`401`/nunca vazio).
- Autor das escritas = `OPERATOR_NAME` (auditoria igual à UI).

## Notas
- Nenhuma credencial persistida; respostas/erros sem segredos.
- Endpoints de leitura (`006`) inalterados — escritas são **aditivas**.
