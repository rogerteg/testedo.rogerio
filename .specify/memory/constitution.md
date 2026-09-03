<!-- Sync Impact Report
  Version change: (placeholder template) → 0.1.0
  Modified principles: none (initial adoption; replaces empty template scaffold)
  Added sections: Core Principles (8); Technical & Security Constraints;
                  Development Workflow & Quality Gates; Governance
  Removed sections: none
  Deferred TODOs: none
-->
# Automatic1 Constitution

## Core Principles

### I. Automation & Reproducibility
Everything that assembles or configures an environment MUST be expressed as code and
automation — never as undocumented manual steps. Setups MUST be reproducible from a clean
machine, idempotent (safe to run more than once), and deterministic regardless of who runs
them. Rationale: the product IS environment setup automation; manual drift is the primary
failure mode.

### II. Code Quality
Code MUST be clear, reviewed, and maintainable: meaningful names, small cohesive units,
documented non-obvious decisions, and no dead code. Every change MUST pass code review before
merge. Rationale: automation code is trusted infrastructure and must be auditable.

### III. Test-First (NON-NEGOTIABLE)
Tests MUST be written before the implementation they validate: define expected behavior,
confirm the test fails for the right reason, then implement (red-green-refactor). Environment
setups MUST be validated in automated tests/CI rather than only on a developer's machine.
Rationale: provisioning errors are costly and hard to detect without executable verification.

### IV. Security
Secrets MUST NEVER be committed to the repository. Use least-privilege credentials, store
secrets in approved secret managers, and pin and review dependencies and third-party scripts
before use. Rationale: setup tooling routinely handles privileged credentials and network
downloads, making it a high-risk attack surface.

### V. Performance & Efficiency
Automations MUST avoid needless work: prefer idempotent, incremental operations, minimize
network round-trips and downloads, and keep total setup time reasonable. Optimize only where
measurement shows a bottleneck, and document known costs. Rationale: setup time is multiplied
across every machine and every re-run.

### VI. Consistent UX / Experience
Automation MUST produce clear, consistent output: a predictable interface (commands,
arguments, exit codes), meaningful progress feedback, and actionable error messages that tell
the user how to recover. Rationale: operators and end users depend on the tool to know what
happened and what to do next.

### VII. Simplicity & YAGNI
Start with the simplest solution that works. Do NOT add features, abstractions, or dependencies
speculatively; add them only when a concrete need exists, and justify each addition. Rationale:
each extra moving part increases setup fragility and maintenance burden.

### VIII. Observability & Versioning
Automation MUST log what it does in a structured, greppable way and report success or failure
unambiguously. All artifacts, scripts, and configs MUST follow Semantic Versioning
(MAJOR.MINOR.PATCH); breaking changes require a documented migration path. Rationale:
reproducibility requires knowing which version produced a given state.

## Technical & Security Constraints

- Environment setup MUST be fully scriptable and runnable headlessly: no interactive steps
  unless strictly required, and then with clear prompts and safe defaults.
- Reuse upstream setup assets explicitly (e.g., projects in the style of
  `SetupFrancisMno`): record sources, versions/hashes, and license/compliance notes rather than
  silently copying unvetted content.
- Document the target platform and primary scripting language; this project defaults to
  PowerShell (`ps`) unless a task explicitly requires another runtime.
- No secrets in code or logs; sensitive values MUST come only from environment variables or an
  approved secret manager.
- Supply-chain review is required before adopting any new third-party tool, script, or
  dependency.

## Development Workflow & Quality Gates

- Balanced workflow: changes go through review, and automated tests plus static checks MUST
  pass in CI before merge.
- Each feature follows the Spec Kit loop: specify → plan → tasks → implement → converge, with
  the constitution checked at review time.
- Every environment script MUST include an automated validation path; "it worked on my machine"
  is not sufficient evidence.
- Usage, prerequisites, and failure-recovery documentation ship with each feature.

## Governance

This constitution supersedes ad-hoc practices; all principles are binding unless amended.
Amendments MUST be proposed in a pull request, reviewed, and recorded here with a version bump
per the policy below. Compliance is verified during spec/plan/task review and code review; a
reviewer MUST call out any change that conflicts with a principle.

- Versioning policy: MAJOR for removal or redefinition of principles; MINOR for new principles
  or materially expanded guidance; PATCH for clarifications, wording, and typo fixes.
- Amendment procedure: propose change → review → ratify → record new version and date in the
  footer and in the Sync Impact Report.
- Compliance review: all PRs/reviews MUST verify constitution compliance; complexity MUST be
  justified; use the generated skills and the `.specify` workflow for runtime development
  guidance.

**Version**: 0.1.0 | **Ratified**: 2026-09-02 | **Last Amended**: 2026-09-02
