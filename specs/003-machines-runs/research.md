# Research: Máquinas Alvo e Execuções (Automatic1)

**Branch**: `003-machines-runs` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Fase 0 do `/speckit-plan`. Resolve as clarificações da spec (Q1–Q3) e consolida as decisões técnicas. Formato: *Decision / Rationale / Alternatives considered*.

---

## D1 — Natureza da execução nesta etapa (Q1=A)

- **Decision**: A execução é **registro/estado (metadados)** — o administrador registra manualmente execuções (setup × máquina) com status controlado e resumo opcional. **Nenhuma execução real é disparada** (sem SSH/comandos); o provisionamento real é a Etapa 3 (`004`).
- **Rationale**: Cria o modelo e o histórico que a Etapa 3 consumirá sem tocar máquinas de produção (risco/segurança), mantendo o escopo pequeno e testável (YAGNI + constituição IV).
- **Alternatives considered**: Disparar execução real já nesta etapa (antecipa `004` — rejeitado: credenciais, executor e risco); só criar modelo sem UI (rejeitado: sem valor visível).

## D2 — Credenciais de máquina (Q2=A)

- **Decision**: Máquinas guardam **apenas metadados** (nome, identificação/endereço, plataforma, status, descrição). **Nenhum campo armazena nem referencia credencial** (sem "usuário", senha, token ou nome de chave). Conexão real (Etapa 3) usará cofre/variáveis de ambiente.
- **Rationale**: Constituição IV (segredos nunca no repositório/banco); metadados bastam para o catálogo de hosts.
- **Alternatives considered**: Referências a segredos gerenciados externamente (ex.: nome da chave no cofre) — adiado até a Etapa 3 ter necessidade concreta (YAGNI).

## D3 — `resultado_ultima_execucao` (Q3=A, sem regressão na `001`)

- **Decision**: **Derivação em tempo de leitura**. O detalhe do setup apresenta a "última execução" a partir da **mais recente `Execution`** (status + resumo + data + autor) quando existir histórico; quando **não** houver execução, exibe o campo manual `resultado_ultima_execucao` da feature `001` como fallback. **A coluna não é removida nem reescrita** — sem migração de dados e sem quebrar testes/UI da `001`.
- **Rationale**: Atende Q3=A (fonte única derivada do histórico quando existe) sem regressão: setups sem execução continuam exatamente como na `001`.
- **Alternatives considered**: Remover a coluna e migrar dados (quebraria a `001` e exigiria migração sem ganho agora); campo duplicado manual+histórico com divergência (rejeitado).

## D4 — Entidades novas e persistência

- **Decision**: Duas entidades: **`TargetHost`** (máquina alvo; tabela `target_host`) e **`Execution`** (execução; tabela `execution`), esta com FKs `setup_id` (→ `environment_setup.id`) e `target_host_id` (→ `target_host.id`), status controlado e `resumo`. Tabelas novas são criadas por `create_all` no `init_db()` — **nenhuma alteração** em `environment_setup` (sem migração aditiva desta vez).
- **Rationale**: `create_all` cobre tabelas novas idempotentemente (G2); nenhuma coluna existente muda (regressão zero). FKs simples + consultas manuais (como o restante do código) — sem relationships/ORM complexo (YAGNI).
- **Alternatives considered**: Reutilizar `status` de máquina no `EnvironmentSetup` (conceitos distintos — rejeitado); ORM `relationship` com cascade (complexidade sem necessidade — rejeitado).

## D5 — Ciclo de vida de máquina e de execução

- **Decision**: Máquina tem `status ∈ {ativa, inativa}`. Ativa → inativa somente via ação "Desativar" com **confirmação e aviso** quando houver execuções (US3); reativação via ação "Reativar". Listagem mostra todas (ativas e inativas) com pill de status. Execução é **imutável** no v1 (apenas criação + histórico) — sem editar/excluir (YAGNI). Setup continua com `status` próprio (features `001`/`002`); arquivamento de setup com execuções exibe **aviso com contagem** na tela de confirmação (sem bloquear — spec US3).
- **Rationale**: Espelha o padrão de exclusão reversível/confirmação da `001`; mantém semântica simples.
- **Alternatives considered**: Bloquear arquivamento/desativação quando há execuções (spec pede aviso, não bloqueio — rejeitado); máquina sem estado inativa (impossível desativar — rejeitado).

## D6 — Validação e segurança

- **Decision**: Novas validações em `app/schemas.py` reutilizando `contem_segredo` e a regra de nome único (case/whitespace-insensitive): `validar_maquina` (nome/identificação obrigatórios; plataforma default controlada; anti-segredo) e `validar_execucao` (setup/máquina obrigatórios, status válido, anti-segredo no resumo). Status de máquina/execução com conjuntos e rótulos PT-BR controlados.
- **Rationale**: FR-004/FR-006; aproveita código existente (DRY) e mantém as mensagens acionáveis (FR-014).
- **Alternatives considered**: Validação nova do zero por rota (duplicaria regras — rejeitado).

## D7 — UI/rotas

- **Decision**: Páginas próprias de máquinas (listar/novo/editar/detalhe/desativar) e criação de execução a partir do **detalhe do setup** (form com seleção de máquina ativa + status + resumo). Histórico de execuções renderizado no detalhe do setup e no detalhe da máquina. Aviso de arquivamento com contagem na tela de confirmação da `001` (ampliada).
- **Rationale**: Fluxo centrado no setup ("registrar que este setup rodou naquela máquina"); histórico consultável pelos dois lados do vínculo.
- **Alternatives considered**: Página central de execuções (mais telas sem ganho — rejeitado); modal JS (mantém-se server-rendered — rejeitado).

## D8 — Estratégia de testes

- **Decision**: pytest/TestClient (mesmas fixtures). Suíte nova em `tests/test_maquinas_execucoes.py`: CRUD de máquina (criar/listar/detalhe/editar/desativar, duplicado, obrigatórios, anti-segredo), criação de execução com vínculo + histórico nos dois lados, aviso de arquivamento/desativação com execuções, derivação da última execução no detalhe do setup e fallback manual, regressão da `001`/`002` zero.
- **Rationale**: G1 (test-first) e cobertura dos cenários US1–US3 (quickstart C1–C7).
