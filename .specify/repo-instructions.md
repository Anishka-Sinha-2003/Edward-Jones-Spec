# AIS Spec-Driven Development Framework

Unified workflow for decomposing raw requirements (RFPs, SOWs, transcripts) into structured, implementable specifications. Language/framework-agnostic.

## Workflow

Pre-sales is optional. Run project setup once, then cycle the spec lifecycle per feature:

```
PRE-SALES (optional, per engagement):
  /ais.presales.synthesize → specs/.presales/01-what-we-heard.md
  /ais.presales.propose    → specs/.presales/02-proposal.md
  /ais.presales.scope      → specs/.presales/03-sow.md

PROJECT SETUP (once):
  /ais.setup.plan          → specs/.project-plan/
  /ais.setup.architecture  → specs/.architecture/
  /ais.setup.constitution  → specs/constitution.md

SPEC LIFECYCLE (per feature):
  /ais.spec.specify   → specs/YYMM-NNN-name/spec.md     (defining)
  /ais.spec.design    → design.md, data-model, contracts  (planning)
  /ais.spec.tasks     → tasks.md                          (ready)
  /ais.spec.implement → execute tasks phase-by-phase      (in-dev → complete)

REPORTING (anytime):
  /ais.report.standup  → specs/.project-plan/reports/YYYY-MM-DD-HHMM-standup.md
  /ais.report.status   → specs/.project-plan/reports/YYYY-MM-DD-HHMM-status.md
  /ais.report.project  → specs/.project-plan/reports/YYYY-MM-DD-HHMM-project.md
```

## Key Conventions

- **Spec IDs**: `YYMM-NNN` format (e.g., `2602-001` = Feb 2026, first spec). Sub-specs use `.N` suffix.
- **Pre-sales specs**: Pre-sales proposes specs by name. At delivery kickoff, `/ais.setup.plan` assigns `SPEC-YYMM-NNN` identifiers and creates directories.
- **Branches**: Spec work uses `YYMM-NNN-short-description` branches. Non-spec work uses `feature/`, `bugfix/`, `chore/`, `docs/` prefixes.
- **All PRs** squash-merge to main. No direct commits to main.
- **Paths**: Always use absolute paths in commands and scripts.
- **Templates**: Live in `.specify/templates/`. Commands auto-fill them.
- **Playbooks**: Live in `.specify/playbooks/`. Domain-specific patterns for pre-sales and delivery.
- **Constitution**: `specs/constitution.md` defines non-negotiable standards. All designs must comply or justify violations.
- **Status tracking**: Spec.md YAML frontmatter is canonical. Report commands derive live status from repo state.

## Directory Structure

```
.github/workflows/     # GitHub Actions CI/CD pipelines
.project-context/      # Raw inputs (gitignored, never committed)
.specify/              # Templates, scripts, playbooks
  playbooks/           # Domain-specific engagement playbooks
  scripts/bash/        # Automation scripts (return JSON)
  templates/           # Markdown templates for all artifact types
docs/
  getting-started/     # Demos: hello-world, pre-sales-demo
  reference/           # Commands, workflow, multi-tool docs
  guides/              # Pre-sales, delivery, roles, process mapping, playbooks
infra/                 # Infrastructure as Code
specs/
  constitution.md      # Non-negotiable project standards
  .presales/           # Pre-sales artifacts (01-what-we-heard, 02-proposal, 03-sow)
  .architecture/       # Wardley map, C4, ADRs, tech stack, data flow
  .project-plan/       # Charter, risks, context sources
    reports/           # Persisted reports (dated, sortable)
  YYMM-NNN-name/       # Per-spec: spec.md, design.md, tasks.md, etc.
src/                   # Application code
tests/                 # Tests mirroring src/ structure
```

## Rules

- Never modify `.project-context/` directly — it's raw input, read-only.
- Always invoke workflow steps via slash commands (`/ais.spec.specify`, etc.), not manually.
- Tasks in `tasks.md` must follow checklist format: `- [ ] [ID] [P?] [Story?] Description`
- Status is tracked in spec.md YAML frontmatter. Report commands derive live state from the repo.
- Bash scripts return JSON; commands parse the output for paths and metadata.
- Run consistency checks (built into `/ais.spec.tasks`) before implementation.
- **PR footer**: Always end PR descriptions with: `Coded with [AIS-spec](https://github.com/ais-internal/ais-spec)`
