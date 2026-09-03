# Research: Catálogo Padrão do Automatic1 (stack de referência)

**Branch**: `002-seed-real-stack` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Fase 0 do `/speckit-plan`. Consolida as decisões técnicas e resolve os pontos sinalizados na spec e as lacunas deixadas em aberto (mecanismo de carga, escopo do conteúdo, política de recarga). Formato: *Decision / Rationale / Alternatives considered*.

---

## D1 — Mecanismo de carga do catálogo padrão

- **Decision**: **Ação explícita na interface** — formulário `POST /setups/carregar-padrao` disparado por um CTA no estado vazio e por um botão dedicado na listagem ("Carregar catálogo padrão"). Nenhuma inserção automática no primeiro uso (spec Q2 → opção A).
- **Rationale**: Mantém o controle total do administrador sobre a escrita de dados (nada é inserido sem pedido), é fácil de testar via `TestClient` e reaproveita o padrão de feedback por redirect (303) já usado no CRUD da feature `001`.
- **Alternatives considered**: Carga automática no 1º uso (insere dados sem ação explícita — rejeitado); script/comando separado da web (passo manual extra e fora do fluxo do admin — rejeitado; o produto é uma ferramenta web interna).

## D2 — Política de recarga: aditivo e não destrutivo (sem "atualizar padrão intacto")

- **Decision**: A carga/recarga é **estritamente aditiva**: para cada item do manifesto padrão, se já existir um setup com o mesmo nome normalizado (caixa/espaços insensíveis), **não faz nada** (ignorado); caso contrário, cria. Nenhum registro existente é alterado ou removido. Relatório com `criados` / `ignorados` / `avisos`.
- **Rationale**: Sem uma trilha de proveniência (ex.: flag "veio do catálogo padrão" + histórico de edições) é impossível distinguir, com segurança, um "registro padrão intacto" de um "registro padrão editado pelo usuário" — a spec Q3 escolheu "preservar sempre". A variante aditiva pura garante 0 sobrescritas/remoções por construção (SC-003) e mantém a idempotência trivial (recarregar = nada a criar → `criados=0`). Atualizar metadados de registros já existentes fica para quando existir trilha de proveniência (documentado na spec, FR-005).
- **Alternatives considered**: Atualizar registros padrão "intactos" (exigiria proveniência/versão do padrão no registro — complexidade não justificada agora, YAGNI); padrão como fonte de verdade sobrescrevendo edições (viola "preservar sempre" — rejeitado).

## D3 — Ambiente-alvo estruturado e campo `categoria`

- **Decision**: Adicionar campo **`categoria`** (opcional, enum: `infraestrutura_base` | `aplicacao`) ao `EnvironmentSetup`, preenchido pelos registros do catálogo padrão; registros criados manualmente ficam sem categoria ("não classificada"). A plataforma alvo dos registros padrão usa o **valor controlado** `"Debian + Docker Swarm"` no campo existente `plataforma_alvo` (que permanece texto livre para registros manuais — sem quebra da feature `001`).
- **Rationale**: FR-006/FR-007. Categoria + plataforma controlada dão significado e filtrabilidade sem remodelar a validação existente de `plataforma_alvo` (evita migração/regressão na feature `001`). Campo único e simples (YAGNI), sem nova entidade.
- **Alternatives considered**: Nova entidade `Categoria`/`AmbienteAlvo` com relacionamento (overkill para dois valores fixos); transformar `plataforma_alvo` em enum fechado (quebraria registros manuais existentes e a regra da 001 — rejeitado).

## D4 — Conteúdo do catálogo padrão (manifesto)

- **Decision**: Manifesto com a **stack de referência completa** (spec Q1 → opção A): **7 infraestrutura base** (Docker Engine, Docker Swarm, Traefik, Portainer, PostgreSQL, MongoDB, Redis) + **8 aplicações** (Chatwoot, Evolution API, Typebot, N8N, Appsmith, MinIO, RabbitMQ, PgAdmin4). Cada item: `nome`, `categoria`, `plataforma_alvo="Debian + Docker Swarm"`, `origem_asset` (URL oficial do upstream), `descricao` (curta), `status="ativo"`, `licenca` (quando bem estabelecida; senão "não informado"); **`versao`/`hash` sempre "não informado"** — o upstream usa `latest`/rolling e **nenhum valor é inventado** (FR-003).
- **Rationale**: Espelha a stack do SetupFrancisMno (referência aprovada) e atende a constituição IV (reusar asset upstream registrando fonte, não copiar conteúdo não avaliado). `origem_asset` aponta para o upstream oficial (rastreabilidade); não há download/instalação nesta feature (FR-011).
- **Alternatives considered**: Fatia menor (só infra ou subconjunto de apps) — rejeitada na clarificação Q1; copiar scripts dos instaladores para o repo (viola constituição IV — rejeitado).

## D5 — Migração aditiva do schema (coluna `categoria`)

- **Decision**: Em `init_db()`, após `create_all`, executar **migração aditiva idempotente** em SQLite: verificar via `PRAGMA table_info(environment_setup)` se a coluna `categoria` existe e, se não, `ALTER TABLE environment_setup ADD COLUMN categoria VARCHAR(32)` (nullable). Sem migrations pesadas (YAGNI).
- **Rationale**: Bancos existentes criados pela feature `001` (ex.: `data/setups.db`) não ganham a coluna com `create_all`; a checagem via PRAGMA é barata, idempotente e reproduzível (constituição G2). Campos novos são nullable → sem quebra de leitura/escrita antiga.
- **Alternatives considered**: Alembic/migração formal (adiado até haver mudança de schema real recorrente — YAGNI); dropar e recriar o banco (perde dados — rejeitado).

## D6 — Anti-segredo na carga (FR-010)

- **Decision**: Ao carregar cada item do manifesto, os campos de texto passam pela checagem `contem_segredo` (mesma função da feature `001`, exposta em `app/security_audit`/`schemas`); se algum item sinalizar segredo, ele **não é criado** e entra em `avisos`. O manifesto em si é código revisado, sem segredos → em operação normal `avisos=0`; a checagem é defesa em profundidade e testável.
- **Rationale**: Reaproveita regra existente (SC-005) sem duplicar lógica; garante que mesmo conteúdo futuro malicioso/errado na lista não persista credencial.
- **Alternatives considered**: Pular a checagem por ser dado controlado (reduz garantia da FR-010 — rejeitado).

## D7 — Rotas/contrato e filtro por categoria

- **Decision**: Nova rota `POST /setups/carregar-padrao` (303 → `/setups?sucesso=catalogo_carregado&criados=N&ignorados=M`). Listagem (`GET /setups`) ganha parâmetro opcional `?categoria=infraestrutura_base|aplicacao` (além de `?q=`), coluna "Categoria" e botões de carga. Ambiente-alvo é filtrável pelo `?q=` (texto casa com `plataforma_alvo`) — suficiente para a US2.
- **Rationale**: Reaproveita o padrão de mensagens/redirect da feature `001`; mudança mínima e testável no contrato web.
- **Alternatives considered**: Página dedicada de importação (mais telas sem ganho — rejeitado); filtro separado por plataforma (duplicaria o `?q=` — rejeitado).

## D8 — Auditoria das operações em massa

- **Decision**: Cada item criado pela carga registra `created_by`/`updated_by` = operador configurado (`OPERATOR_NAME`) e timestamps automáticos; log estruturado da carga com contagens (FR-009). Sem autenticação no v1 (mesma premissa da feature `001`).
- **Rationale**: FR-009/FR-011; consistente com o CRUD existente.
- **Alternatives considered**: Nova entidade de "lote/importação" com auditoria própria (complexidade desnecessária no v1 — YAGNI).

## D9 — Estratégia de testes

- **Decision**: pytest + `TestClient` (mesmas fixtures da feature `001`). Casos: carga inicial popula todos os itens do manifesto (categoria/plataforma/origem presentes); **idempotência** (2ª carga → `criados=0`); **não destrutivo** (registro do usuário com nome colidindo não é alterado); **anti-segredo** (item do manifesto adulterado com segredo é bloqueado e reportado em avisos); **filtro por categoria**; UI mostra CTA/botão de carga; teste da migração aditiva idempotente (init_db roda duas vezes sem erro).
- **Rationale**: Atende G1 (test-first) e cobre os cenários de aceite das US1–US3.
- **Alternatives considered**: Testar contra banco em arquivo real (mais lento/frágil — mantém-se SQLite em memória como a feature `001`).
