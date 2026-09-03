# Research: Provisionador Real (Automatic1)

**Branch**: `004-provisioner` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Fase 0 do `/speckit-plan`. Consolida as decisões (Q1–Q3 resolvidas com as opções recomendadas + refinamentos de engenharia) e o desenho técnico do executor. Formato: *Decision / Rationale / Alternatives considered*.

---

## D1 — Modo de execução e runner (Q1=A)

- **Decision**: Execução **remota via SSH** pelo Automatic1 Admin, através de uma **abstração de runner** plugável: `SSHRunner` (produção, via `paramiko`) e `FakeRunner`/adaptador simulado (testes — sem rede). Execução **síncrona com timeout** no v1; o resultado grava a `Execution` (feature `003`) com status real (`sucesso`/`erro`), saída/log, `exit_code` e horários.
- **Rationale**: Modelo de produto (o Admin dirige o provisionamento no host Debian/Docker); a abstração permite testes herméticos em CI (constituição III/G1) sem tocar máquinas reais. Síncrono no v1 = simples e auditável (YAGNI).
- **Alternatives considered**: Pull (gerar script p/ operador rodar) — mais seguro, porém sem automação real dirigida pelo Admin; agente/daemon no host — nova peça de infraestrutura (adiado); execução assíncrona em background (fila) — adiado (YAGNI no v1).

## D2 — Credenciais por ambiente (Q2=A)

- **Decision**: Credenciais de acesso lidas de **variáveis de ambiente**, nunca do banco/UI: `AUTOMATIC1_SSH_USER` (default `root`), `AUTOMATIC1_SSH_KEY` (caminho do arquivo de chave) e `AUTOMATIC1_SSH_PASSPHRASE` (opcional, **nunca logada**). O host é alcançado pela `identificacao` da máquina alvo. Ausência de credencial configurada → **bloqueio acionável** antes de qualquer conexão.
- **Rationale**: Constituição IV; simples e testável (o caso "sem credencial → bloqueio" é testável sem rede). Suporte a cofre externo fica para quando houver muitos hosts (YAGNI).
- **Alternatives considered**: Cofre externo/API de secrets (dependência/serviço — adiado); salvar credencial por host no banco (viola constituição IV — rejeitado).

## D3 — O que executar e validação de integridade (Q3=A refinada)

- **Decision**: O executor roda o **asset/script-fonte referenciado por `origem_asset`**. Fluxo do v1: (1) baixa o asset no host; (2) se `hash` (sha256) presente, verifica antes de executar — divergência **bloqueia** sem efeito colateral; (3) `hash` ausente → executa com **aviso de integridade não verificada** (registrado); (4) se `origem_asset` **não for um artefato executável** (ex.: URL de repositório, sem extensão/padrão de script), **bloqueia com erro acionável** orientando a informar o script instalador. Scripts instaladores por ferramenta chegam com a feature instalador (Etapa 4 do roadmap) — os itens padrão (`002`) que apontam para repositórios **não são executáveis** no v1 (documentado na spec).
- **Rationale**: Fiel à constituição IV (reusar asset upstream com registro/validação, nunca adotar cegamente). Evita "inventar" instalador nesta feature (isso é a feature instalador); mantém o executor honesto e testável (os caminhos de bloqueio/aviso são testáveis com FakeRunner).
- **Alternatives considered**: Compilar playbook/passo próprio de instalação por ferramenta (antecipa a feature instalador — rejeitado aqui); executar qualquer URL como `bash` sem validação (inseguro — rejeitado).

## D4 — Redação de segredos e logs (FR-005)

- **Decision**: Antes de persistir/exibir, a saída é sanitizada: valores de variáveis de ambiente conhecidas (ex.: passphrase/chave) e padrões de segredo (mesma base do `contem_segredo`) são **redigidos** (ex.: `[REDACTED]`). Log estruturado da execução com início/fim/exit code.
- **Rationale**: FR-005/SC-003; reutiliza a lógica anti-segredo existente (DRY).
- **Alternatives considered**: Não sanitizar (viola FR-005 — rejeitado).

## D5 — Concorrência e estado (FR-007/SC-006)

- **Decision**: Regra de concorrência por par setup×máquina: **no máximo uma `Execution` com status `em_andamento`** por par; nova execução é bloqueada com mensagem enquanto houver uma em andamento. Execução síncrona + guarda em banco garantem a regra de forma determinística e testável.
- **Rationale**: Evita corridas/estado inconsistente (SC-006) sem fila/threads (YAGNI no v1).
- **Alternatives considered**: Filas/workers (adiado); bloqueio otimista por timestamp (frágil — rejeitado).

## D6 — Modelo de dados (Execution evoluída)

- **Decision**: `Execution` (feature `003`) ganha colunas **aditivas nullable** para a execução real: `log` (texto), `exit_code` (int), `started_at`/`finished_at` (datetime). Migração aditiva idempotente via `PRAGMA`+`ALTER TABLE` no `init_db` (padrão da feature `002`). `EnvironmentSetup`/`TargetHost` inalterados; `resumo` continua resumindo a execução (ex.: 1ª linha / status).
- **Rationale**: Reaproveita o histórico/`003`; colunas nullable → sem quebra. Registros anteriores (`003`) permanecem válidos (`log`/`exit_code` nulos = execução registrada manualmente).
- **Alternatives considered**: Nova tabela `ExecutionLog` separada (mais normalizado, porém mais peças — YAGNI).

## D7 — Dependência nova (SSH)

- **Decision**: Adicionar **`paramiko`** (pinado) como dependência de runtime para o `SSHRunner`. Testes usam apenas `FakeRunner` → sem necessidade de rede/SSH em CI.
- **Rationale**: SSH puro em Python, multiplataforma, sem depender de binário `ssh` do sistema (Windows dev → host Linux). Constituição IV exige pin/revisão — registrada no `pyproject`.
- **Alternatives considered**: `subprocess` com binário `ssh` do sistema (depende de instalado/configurado no host do Admin — rejeitado).

## D8 — UI/rotas

- **Decision**: Ação **"⚡ Provisionar"** a partir do detalhe do setup (e da máquina): página de confirmação mostrando setup+máquina+origem+aviso de integridade (sem hash) → `POST` executa (síncrono, timeout) → redirect para o detalhe com a `Execution` real. O histórico (`003`) passa a exibir, para execuções reais, `exit_code` e log (sanitizado) com opção de expandir.
- **Rationale**: Reaproveita histórico/UI da `003`; adiciona só a superfície de disparo + exibição de log.
- **Alternatives considered**: Job em página separada com polling (adiado — síncrono no v1).

## D9 — Estratégia de testes

- **Decision**: Suíte `tests/test_provisioner.py` com `FakeRunner`: execução bem-sucedida cria `Execution` real (status/log/horários); falha → `erro` + log com motivo; hash divergente bloqueia sem efeito; sem credencial configurada → bloqueio acionável; origem não executável → erro acionável; redação de segredo no log; bloqueio de host inativo/setup arquivado; bloqueio de execução concorrente (`em_andamento`); reexecução idempotente preserva histórico. Regressão `001`–`003` = 0.
- **Rationale**: G1 (test-first); cobre US1–US3 e os cenários de segurança sem rede.
