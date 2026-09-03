# Automatic1 Admin

Interface web de administração interna para o catálogo de **setups de ambiente** que o
[Automatic1] provisiona. **v1** entrega **criar + listar** (P1); detalhes, edição e
arquivamento ficam para slices futuras (veja `specs/001-environment-crud/spec.md`).
A feature **`002` (catálogo padrão)** adiciona a ação "**Carregar catálogo padrão**",
que popula o catálogo com a stack de referência do Automatic1 (Debian + Docker Swarm) e o
campo **categoria** (infraestrutura base vs aplicação) — veja `specs/002-seed-real-stack/spec.md`.

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

## Catálogo padrão (stack de referência) — feature 002

O botão "**Carregar catálogo padrão**" (na listagem e no estado vazio) insere a stack que o
Automatic1 provisiona em **Debian + Docker Swarm**: **7 infraestrutura base** (Docker Engine,
Docker Swarm, Traefik, Portainer, PostgreSQL, MongoDB, Redis) + **8 aplicações** (Chatwoot,
Evolution API, Typebot, N8N, Appsmith, MinIO, RabbitMQ, PgAdmin4).

- Cada registro padrão traz `plataforma_alvo = "Debian + Docker Swarm"`, **categoria**
  (infraestrutura base vs aplicação) e a **origem do asset** apontando para o upstream
  (referência, sem copiar conteúdo — constituição IV). Versão/hash ficam **"não informado"**
  (nada é inventado) e a licença é referência inicial conferível no upstream.
- A carga é **aditiva e não destrutiva**: recarregar **não duplica** e **nunca altera/remove**
  registros existentes (nem os do usuário). O relatório pós-carga mostra criados/ignorados/avisos.
- O manifesto vive em `app/catalogo_padrao.py` (fonte única) e a suíte de testes em
  `tests/test_catalogo_padrao.py`.

Documentação do fluxo: `specs/001-environment-crud/` (`spec.md`, `plan.md`, `research.md`,
`data-model.md`, `contracts/web.md`, `quickstart.md`, `tasks.md`) e `specs/002-seed-real-stack/`.

## Máquinas alvo e execuções — feature 003

O Automatic1 registra **onde** cada setup é provisionado:

- **Máquinas alvo** (`/maquinas`): hosts (Debian + Docker Swarm) com nome, identificação/endereço e
  status (`ativa`/`inativa`). Guardam **apenas metadados — nenhuma credencial** (constituição IV).
  Desativar/reativar é reversível e exige confirmação.
- **Execuções**: do detalhe de um setup, "Registrar execução" vincula o setup a uma máquina **ativa**
  com status (`planejada`/`em andamento`/`sucesso`/`erro`/`cancelada`) e resumo. Nesta etapa é
  **registro/estado** — nada é executado de fato (provisionamento real é etapa futura).
- **Histórico** visível no detalhe do setup e da máquina; a **última execução** do setup é derivada
  do histórico (fallback para a anotação manual da feature `001` quando não há execuções).
- **Utilização ativa**: arquivar um setup ou desativar uma máquina **com execuções** exibe aviso com a
  contagem antes da confirmação.

Documentação do fluxo: `specs/003-machines-runs/`.

## CI

GitHub Actions (`.github/workflows/ci.yml`) roda em push/PR: `uv sync --frozen` → `ruff check`
→ `pytest`.

## Deploy (Render)

O repositório contém um **`render.yaml`** (Blueprint) que cria o web service `automatic1-admin`:

- **Build**: instala `uv` e roda `uv sync --frozen`.
- **Start**: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Persistência**: `DB_PATH=/data/setups.db` + **disco persistente** montado em `/data`
  (schema criado automaticamente no startup via `init_db`).

Passos: **dashboard.render.com → New → Blueprint** → apontar para este repositório.
> ⚠️ **Disco persistente exige plano pago** (não funciona no free). Para testar grátis sem
> persistência, remova o bloco `disk` do `render.yaml` (os dados resetam a cada deploy).

## Solução de problemas

- **`uv` não encontrado**: instale em https://docs.astral.sh/uv/ e reabra o terminal.
- **Porta ocupada**: ajuste `--port` em `scripts/run.ps1`.
- **Banco corrompido/reset**: pare o servidor, apague `data/setups.db` e rode
  `.\scripts\setup-dev.ps1` (o schema é recriado no startup).
- **Erros de validação no formulário**: mensagens por campo indicam o que corrigir; os dados
  preenchidos são preservados.

[Automatic1]: https://example.com/automatic1
