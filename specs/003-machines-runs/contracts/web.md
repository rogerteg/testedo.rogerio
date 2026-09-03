# Web Interface Contract: Máquinas Alvo e Execuções

**Branch**: `003-machines-runs` | **Date**: 2026-09-03 | **Spec**: [spec.md](../spec.md) | **Data model**: [data-model.md](../data-model.md)

Contrato da interface web server-rendered (FastAPI + Jinja2). Evolui o contrato das features `001`/`002` de forma **aditiva**.

## Rotas / Páginas

### Máquinas Alvo (US1/US3)

| Método | Caminho | Página | Descrição | Origem |
|--------|---------|--------|-----------|--------|
| GET | `/maquinas` | listagem | Lista máquinas (ativas e inativas) com resumo (nome, identificação, plataforma, status); suporta `?q=` (nome/identificação) | US1 |
| GET | `/maquinas/novo` | formulário | Cadastro de máquina (nome*, identificação*, plataforma, descrição) — **sem credenciais** | US1 |
| POST | `/maquinas` | — (redirect) | Cria a máquina (nome único); erro por campo preserva dados; `303 → /maquinas` | US1 |
| GET | `/maquinas/{id}` | detalhe | Detalhes + **histórico de execuções** da máquina | US1/US2 |
| GET/POST | `/maquinas/{id}/editar` | formulário | Edição (mesmas validações; auditoria `updated_by`/`updated_at`) | US1 |
| GET | `/maquinas/{id}/desativar` | confirmação | Confirma desativação; exibe **aviso com contagem** de execuções quando houver | US3 |
| POST | `/maquinas/{id}/desativar` | — (redirect) | `status=inativa` (exige confirmação); `303 → /maquinas/{id}` | US3 |
| POST | `/maquinas/{id}/reativar` | — (redirect) | `status=ativa` | US3 |

### Execuções (US2)

| Método | Caminho | Página | Descrição | Origem |
|--------|---------|--------|-----------|--------|
| GET | `/setups/{setup_id}/executar` | formulário | Registro de execução: seleciona máquina **ativa** + status + resumo | US2 |
| POST | `/setups/{setup_id}/executar` | — (redirect) | Cria a `Execution` (vínculo setup×máquina); `303 → /setups/{setup_id}` | US2 |

### Alterações em telas existentes (features `001`/`002`)

- `GET /setups/{id}` (detalhe): nova seção **"Histórico de execuções"** (lista) + botão "Registrar execução". A linha "Resultado última execução" passa a exibir a **última execução derivada** do histórico quando existir; senão, fallback do campo manual (`resultado_ultima_execucao`).
- `GET /setups/{id}/arquivar` (confirmação): exibe **aviso com contagem** de execuções quando o setup as possuir (US3) — sem bloquear.

## Regras de validação (server)

- **Máquina**: `nome` obrigatório/único (case/whitespace-insensitive); `identificacao` obrigatória; `plataforma_alvo` default `"Debian + Docker Swarm"`; `status ∈ {ativa, inativa}`; anti-segredo nos campos de texto (FR-004/FR-006).
- **Execução**: `setup_id` e `target_host_id` obrigatórios (FKs válidos); `status ∈ {planejada, em_andamento, sucesso, erro, cancelada}`; `resumo` opcional (≤1000) com anti-segredo.
- **Aviso "utilização ativa"**: arquivamento de setup e desativação de máquina exibem a contagem de execuções antes da confirmação (US3) — a ação só ocorre após confirmação explícita.

## Comportamentos transversais

- **Auditoria**: criação/edição/desativação registram autor + data (operador configurado).
- **Sem credenciais**: nenhum formulário de máquina contém campo de senha/token/chave.
- **Idioma**: PT-BR.
- **Feedback**: mensagens de sucesso/erro acionáveis em nível de campo (FR-014).
