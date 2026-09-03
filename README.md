# Automatic1 Admin

Interface web de administração interna para o catálogo de **setups de ambiente** que o
[Automatic1] provisiona. **v1** entrega **criar + listar** (P1); detalhes, edição e
arquivamento ficam para slices futuras (veja `specs/001-environment-crud/spec.md`).

Stack: Python 3.11+ · FastAPI · SQLModel · SQLite · Jinja2 · pytest (uv).

## Pré-requisitos

- Python 3.11+ e [uv](https://docs.astral.sh/uv/)
- Nenhum serviço externo — o SQLite é local (`data/setups.db`)

## Setup (idempotente)

```powershell
.\scripts\setup-dev.ps1   # cria .venv, instala deps (pyproject + uv.lock), cria data/, valida import
```

## Executar

```powershell
.\scripts\run.ps1         # http://127.0.0.1:8000
```

Abra `http://127.0.0.1:8000/setups`.

## Testes

```powershell
.\scripts\test.ps1        # ou: uv run pytest
```

Test-first (constituição): a suíte cobre os cenários de aceite do v1
(`tests/test_create_setup.py`, `tests/test_list_setups.py`).

## Configuração (variáveis de ambiente)

| Variável | Default | Descrição |
|----------|---------|-----------|
| `DB_PATH` | `data/setups.db` | Caminho do banco SQLite |
| `OPERATOR_NAME` | `admin` | Autor registrado na auditoria (sem auth no v1) |
| `APP_VERSION` | `0.1.0` | Versão exibida (SemVer) |

## Regras de negócio (resumo)

- **Nome único** (ignora caixa/espaços), **plataforma alvo** e **origem do asset** obrigatórios.
- **Versão** opcional validada como **SemVer**.
- **Sem segredos/credenciais** nos dados (apenas referências/placeholders).
- Auditoria de **autor + data** em criação (sem auth no v1 → `OPERATOR_NAME`).

Documentação do fluxo: `specs/001-environment-crud/` (`spec.md`, `plan.md`, `research.md`,
`data-model.md`, `contracts/web.md`, `quickstart.md`, `tasks.md`).

## Solução de problemas

- **`uv` não encontrado**: instale em https://docs.astral.sh/uv/ e reabra o terminal.
- **Porta ocupada**: ajuste `--port` em `scripts/run.ps1`.
- **Banco corrompido/reset**: pare o servidor, apague `data/setups.db` e rode
  `.\scripts\setup-dev.ps1` (o schema é recriado no startup).
- **Erros de validação no formulário**: mensagens por campo indicam o que corrigir; os dados
  preenchidos são preservados.

[Automatic1]: https://example.com/automatic1
