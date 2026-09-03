# Research: CRUD de Ambientes de Setup (Automatic1)

**Branch**: `001-environment-crud` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

Fase 0 do `/speckit-plan`. Consolida as decisões técnicas e resolve os pontos sinalizados como `NEEDS CLARIFICATION` no Technical Context e as lacunas de clarificação herdadas da spec (campos exatos, permissões, idioma). Formato: *Decision / Rationale / Alternatives considered*.

---

## D1 — Stack da interface web de administração

- **Decision**: Python 3.11+ com **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic), **SQLite** e páginas **server-rendered em Jinja2**.
- **Rationale**: Confirmado com o usuário. A spec pede "interface web de admin interno" e a constituição exige simplicidade (VII/YAGNI) e test-first (III). FastAPI + SQLModel entregam um CRUD com poucas peças, validação declarativa (Pydantic) e testes fáceis (TestClient/httpx). Telas servidas (sem SPA) reduzem dependências e moventes — adequado a ferramenta interna.
- **Alternatives considered**: Django (admin pronto, porém framework maior e menos controle fino do fluxo/UI customizada); Node.js/TypeScript + Express + React (mais peças e tooling, sem ganho para admin interno de baixo volume).

## D2 — Persistência e gerenciamento de schema

- **Decision**: SQLite em arquivo local (`data/setups.db`); schema criado por `SQLModel.metadata.create_all()` em bootstrap idempotente; sem ferramenta de migração pesada no v1.
- **Rationale**: Volume baixo (dezenas–centenas de registros) e single-writer tornam SQLite suficiente. `create_all` + bootstrap reproduzível atende G2. Versionamento e eventuais migrações seguem política SemVer da constituição (VIII) quando a entidade evoluir.
- **Alternatives considered**: PostgreSQL (overkill e exige serviço externo no v1); migrações Alembic completas (adiado até haver mudança de schema real pós-v1 — YAGNI).

## D3 — Autenticação e permissões (v1)

- **Decision**: **Sem autenticação no v1** — ferramenta interna em rede confiável; acesso presumido de administradores. Autor de auditoria registrado por um operador configurável via ambiente (`OPERATOR_NAME`, padrão `admin`) em vez de identidade de login.
- **Rationale**: A spec já registra como premissa "autenticação/permissões fora do escopo v1". Exigir auth agora adicionaria gerenciamento de usuários/sessões sem necessidade concreta (YAGNI). A trilha de auditoria (FR-011) é atendida com timestamps automáticos + autor a partir do operador configurado, sem perder a capacidade futura de trocar por identidade real.
- **Alternatives considered**: Login único compartilhado (adiciona estado de sessão e senha sem necessidade no v1); RBAC completo (claramente pós-v1).

## D4 — Campos exatos da entidade (lacuna da sessão de clarificação)

- **Decision**: Manter o conjunto de campos já descrito na spec, **com "resultado da última execução" como campo opcional/manual** (texto livre, ex.: "não executado"), pois o provisionamento real está fora do escopo. Obrigatórios: **nome, plataforma alvo, origem do asset**. Opcionais: descrição, versão (SemVer), hash, licença/notas de compliance, status, resultado da última execução.
- **Rationale**: A pergunta de clarificação Q1 (campos) não foi respondida — o usuário avançou para o plano. A opção mais conservadora (equivalente à "Option B" da sessão) preserva o que a spec já declara, evitando remover campo que depois precise voltar. "Resultado da última execução" fica como anotação manual opcional até existir automação de execução.
- **Alternatives considered**: Remover o campo (Option A da clarificação) — rejeitado por ser menos conservador sem resposta explícita; enxugar versão/hash/licença — rejeitado (constituição pede registrar versões/hashes/licenças de assets reutilizados).

## D5 — Idioma da interface

- **Decision**: Interface em **português (PT-BR)**, conforme premissa da spec.
- **Rationale**: Usuário e partes interessadas são PT-BR; não há requisito de i18n no v1.
- **Alternatives considered**: Suporte multi-idioma (i18n) — adiado; sem necessidade concreta (YAGNI).

## D6 — Unicidade e validação de nome / versão

- **Decision**: Nome único com comparação **case-insensitive e ignorando espaços extras** (normalização em minúsculas/trim antes da checagem). Versão validada como **SemVer** (regex `MAJOR.MINOR.PATCH` [+pré-release/+build]) somente quando preenchida.
- **Rationale**: Atende FR-002/FR-003 com regra simples e testável na camada de validação Pydantic/schemas.
- **Alternatives considered**: Índice único case-sensitive no banco (não cobre variações de caixa/acentos de forma amigável para o usuário); biblioteca `semver` (dependência extra evitável com regex — YAGNI).

## D7 — Ciclo de vida do status

- **Decision**: Campo `status` com valores controlados: `rascunho` (padrão), `ativo`, `com_erro`, `arquivado`. No v1 o status é **informado pelo usuário no cadastro** (default rascunho); transições automáticas ficam para quando houver execução real. "Arquivado" é o estado usado pela exclusão reversível (US5, P3).
- **Rationale**: Simples e suficiente para o catálogo; alinha com a exclusão lógica/arquivamento já prevista na spec (FR-010) e evita máquina de estados sem uso (YAGNI).
- **Alternatives considered**: Estados derivados automaticamente de execução (inviável — execução fora do escopo); sem campo status (perde a classificação necessária à listagem/filtro).

## D8 — Auditoria (quem/quando)

- **Decision**: Campos `created_at`/`updated_at` (timestamps automáticos) + `created_by`/`updated_by` (string opcional, default do operador configurado — ver D3) em cada registro.
- **Rationale**: FR-011 (trilha de auditoria) atendida de forma leve e testável; compatível com v1 sem auth.
- **Alternatives considered**: Tabela de auditoria separada (histórico de mudanças) — adiada; o v1 exige autoria/data atuais, não histórico completo (YAGNI).

## D9 — Estratégia de testes

- **Decision**: pytest com `TestClient` (httpx) do FastAPI; cada teste roda contra SQLite temporário isolado (fixture). Casos: criação válida, nome duplicado (caixa/espaços), campos obrigatórios ausentes, SemVer inválida, listagem ordenada, filtro por nome/plataforma, estado vazio.
- **Rationale**: Atende G1 (test-first, red-green-refactor) e cobre os cenários de aceite das US1/US2 (P1). Os testes guiam a implementação em `/speckit-implement`.
- **Alternatives considered**: Testes apenas manuais via navegador — rejeitado (constituição exige validação automatizada, não só "funciona na minha máquina").

## D10 — Observabilidade

- **Decision**: Logging estruturado (módulo `logging`) com registro das operações de escrita (criar/editar/arquivar) e erros; versão da app exposta via `pyproject` (SemVer).
- **Rationale**: Constituição VIII; rastreável sem infraestrutura extra no v1.
- **Alternatives considered**: Métricas/tracing externos — overkill para ferramenta interna no v1.
