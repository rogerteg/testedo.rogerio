# CLI Contract: Instalador Próprio do Automatic1

**Branch**: `005-installer` | **Date**: 2026-09-03 | **Spec**: [spec.md](../spec.md) | **Research**: [research.md](../research.md)

Contrato de **interface de linha de comando** do instalador (executado no host Debian pelo operador — pull). Sem API web nova.

## Uso

```bash
cd installer
sudo ./install.sh [--check] [--version] [--help]
```

- `--check` / `AUTOMATIC1_DRY_RUN=1`: valida pré-requisitos (root/sudo, SO Debian 11/12, portas 80/443) **sem aplicar mudanças**; exit `0` se pronto, `2` se pré-requisito ausente.
- Sem flag: executa bootstrap (se `AUTOMATIC1_BOOTSTRAP=1`, default) + instala apps de `AUTOMATIC1_APPS` (lista separada por espaço; default vazio).
- `--version`: imprime a versão do instalador. `--help`: uso + variáveis.

## Exit codes

| Código | Significado |
|--------|-------------|
| `0` | Sucesso |
| `1` | Erro genérico |
| `2` | Pré-requisito ausente (root, Debian, portas, docker) |
| `3` | Configuração inválida |

## Configuração (variáveis de ambiente)

`AUTOMATIC1_STATE_DIR`, `AUTOMATIC1_BOOTSTRAP`, `AUTOMATIC1_APPS`, `AUTOMATIC1_DOMAIN`, `AUTOMATIC1_TRAEFIK_EMAIL`, `AUTOMATIC1_DRY_RUN` — ver `data-model.md`/`config.example.env`.

## Saída

- Logs estruturados com prefixo `[automatic1]` (nível e mensagem).
- **Manifesto** em stdout e em `$AUTOMATIC1_STATE_DIR/manifesto.txt`: `serviço | versão | url` por item instalado.
- Nenhum segredo é impresso/gerado sem o operador decidir (constituição IV).

## Validação

- Automatizada (estrutural/sintaxe, sem host Debian): `tests/test_installer.py` + `bash -n` (quando disponível).
- E2E real (host Debian de teste): passos manuais no `quickstart.md`.
