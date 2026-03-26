# Contributing

This document outlines how we manage our work, branches, pull requests, and merge responsibilities to keep the project maintainable, predictable, and stable.

---

# 1. How We Work: Spec-Driven Development

All feature work follows the **AIS spec-driven development workflow**. Raw project inputs are decomposed into a plan, architecture, and constitution during project setup. Individual features are then developed through a repeatable lifecycle: specify, design, task, implement.

See the **[README](README.md)** for the full command reference and workflow diagram, and **[docs/workflow.md](docs/workflow.md)** for the visual flowchart.

---

# 2. Project Structure

```
/(repo root)
|
├── .claude/                           # Claude Code configuration
│   ├── commands/                      # AIS workflow commands (ais.*)
│   └── settings.json                  # Agent settings
|
├── .project-context/                  # Raw project inputs (gitignored)
│   └── .archive/                      # Processed files moved here
|
├── .specify/                          # AIS workflow engine
│   ├── playbooks/                     # Technology-specific implementation guidelines
│   ├── scripts/                       # Automation scripts
│   └── templates/                     # Markdown templates for specs, designs, tasks
|
├── docs/                              # Documentation (Markdown)
│   ├── workflow.md                    # AIS workflow diagram
│   ├── {quickstart}.md               # Developer quick start guide
│   ├── {architecture guides}.md      # Architecture description documents
│   ├── {other guides}.md             # Other useful guides
│   └── media/                         # Images and media linked from docs
│       └── *.png, *.jpg, ...
|
├── infra/                             # Infrastructure as Code
│   ├── modules/                       # Reusable IaC modules
│   ├── environments/                  # Environment-specific variable files
│   └── layers/                        # Infrastructure layers (see below)
|
├── .github/                           # GitHub configuration
│   ├── workflows/                     # GitHub Actions CI/CD pipelines
│   │   └── ci.yml                     # Lint, test, build on PRs and pushes to main
│   └── pull_request_template.md       # Default PR description template
|
├── source/                            # Application source code
│   ├── apis/                          # RESTful APIs
│   ├── web/                           # Web front-ends (SPA, SSR)
│   ├── agents/                        # AI agents
│   ├── mcp-servers/                   # MCP servers
│   └── {other}/                       # Other application types as needed
|
├── specs/                             # Spec-driven development output
│   ├── constitution.md                # Non-negotiable project standards
│   ├── .project-plan/                 # Project plan and SPEC catalog
│   │   └── reports/                   # Persisted reports (dated, sortable)
│   ├── .architecture/                 # Solution architecture artifacts
│   └── YYMM-NNN-feature-name/        # Per-component spec working area
│       ├── spec.md                    # Feature specification
│       ├── design.md                  # Technical design
│       ├── tasks.md                   # Dependency-ordered task list
│       ├── research.md                # Research findings
│       ├── data-model.md             # Data model documentation
│       ├── contracts/                 # API contracts
│       └── quickstart.md             # Component quick start
|
├── tests/                             # Tests (mirrors source/ structure)
│   ├── apis/
│   ├── web/
│   └── {other}/
|
├── tools/                             # Development and deployment scripts
├── CONTRIBUTING.md                    # This file
└── README.md                          # Project overview and AIS command reference
```

### Infrastructure Layers (When Applicable)

Infrastructure code uses a layered approach. The specific IaC tool (Terraform, Bicep, Pulumi, etc.) depends on the project, but the layering pattern is consistent:

| Layer Range | Purpose | Deploy Frequency |
|-------------|---------|-----------------|
| **000** | Pre-existing resources (already in the environment) | Reference only |
| **100-00 to 100-30** | Baseline infrastructure (networking, core services) | Infrequent |
| **100-40-{workload}** | Workload-specific resources | With each workload deploy |
| **200** | Development-only resources (sandboxes, emulators) | As needed |

### CI/CD Pipelines

Pipeline definitions live in `.github/workflows/`. The CI workflow (`ci.yml`) runs on all PRs to `main` and pushes to `main`:

| Job | Purpose |
|-----|---------|
| **Markdown Lint** | Validates formatting across all `.md` files (specs, docs, contributing) |
| **PowerShell Lint** | Runs PSScriptAnalyzer on `.specify/scripts/` |

Both checks are required to pass before a PR can merge. Concurrency is managed per-branch — pushing a new commit cancels the previous in-progress run. Lint rules are configured in `.markdownlint.jsonc` at the repo root.

---

# 3. Spec Versioning and Branching

## 3.1 Spec IDs

Specs use **YYMM-NNN** identifiers based on creation date:

- `2602-001` = February 2026, first spec
- `2602-002` = February 2026, second spec
- `2603-001` = March 2026, first spec

**Sub-specs** use dot notation: `2602-001.1`, `2602-001.2`

## 3.2 Branch Naming

Branch names **match the spec ID** with a short description suffix:

```
YYMM-NNN-short-description
```

Examples:
- `2602-001-core-api-data-model`
- `2602-002-dashboard-ui`
- `2602-001.1-oauth-flow`

For non-spec work, use conventional prefixes:

- `feature/<short-description>`
- `bugfix/<short-description>`
- `chore/<short-description>`
- `docs/<short-description>`

Use matching labels on your PR (`feature`, `bugfix`, `chore`, `docs`, `breaking-change`).

## 3.3 Feature Directory

Each spec branch gets a corresponding directory under `specs/`:

```
specs/2602-001-core-api-data-model/
  spec.md
  design.md
  tasks.md
  ...
```

The `create-new-feature` script automates branch creation, numbering, and directory setup.

---

# 4. Backlog Management

Work is tracked through the **project plan** (`specs/.project-plan/`) and individual spec task lists (`specs/YYMM-NNN-feature/tasks.md`).

- The project plan contains the **SPEC catalog** — the master list of all components with owners, scope, dependencies, and effort estimates.
- Each spec's `tasks.md` contains the implementation task breakdown, generated by `/ais.spec.tasks`.
- `/ais.github.sync` creates GitHub milestones and issues from the spec catalog and task lists for tracking in GitHub Projects.

### Priority and Ordering

- Specs are ordered by dependency (the project plan documents the dependency map and critical path).
- Tasks within a spec are dependency-ordered; tasks marked `[P]` can be parallelized.
- Work on the highest-priority unblocked spec first.

---

# 5. Branch and Pull Request Management

## 5.1 Branch Policy

The `main` branch follows these rules:

- All changes require a pull request.
- Each pull request requires **one approval** from a member of the designated maintainer group.
- Direct commits to `main` are not permitted.
- We prefer **Squash and Merge** when integrating changes into `main`.

## 5.2 Pull Request Expectations

Before opening a pull request:

- Ensure your branch is up to date with `main`.
- Keep the pull request scoped to one logical feature or fix (typically one spec or one task group).
- Provide a clear description of what was changed and why.
- Reference the spec ID in the PR title or description (e.g., `SPEC-2602-001: Core API data model`).
- Remove unrelated or accidental changes.

During review:

- Address feedback directly in the PR.
- Push updates as needed.
- Use the PR conversation for questions or clarification.

## 5.3 Responsibilities of the Developer Raising the PR

The developer who opens the pull request is responsible for the **entire lifecycle**:

### Before merging

- Shepherd the PR through review.
- Ensure the branch stays updated with `main`.

### After approval

- Perform the merge using Squash and Merge.
- Confirm the merge completes cleanly.

### After merging

- Monitor CI/CD pipelines triggered by the change.
- Investigate and resolve issues caused by the merge.
- Submit follow-up PRs if needed.

Ownership ends **only when `main` is stable** after the change.

## 5.4 Asking Questions

If anything is unclear, ask in the pull request or team channel.
Early clarification prevents rework.

---

# 6. Code and Quality Standards

## 6.1 Constitution Compliance

Every project maintains a **constitution** (`specs/constitution.md`) that defines non-negotiable standards: technology choices, quality gates, and integration patterns. All designs and implementations must comply with the constitution. If a violation is necessary, it must be justified and documented.

## 6.2 General Guidelines

- **Keep changes small and focused.** One spec, one PR. Break large specs into sub-specs if needed.
- **Follow existing patterns.** Before introducing a new pattern, check the constitution and existing code.
- **Write tests.** Tests live in `tests/` mirroring the `source/` structure.
- **Document decisions.** Architecture Decision Records (ADRs) live in the architecture artifacts. If you make a significant technical choice, record it.
- **Migrations must be idempotent and backwards-compatible** to support rolling deploys.
- **Secrets and credentials** must never be committed. Use environment variables or secret managers.

## 6.3 Commit Messages

Write clear, concise commit messages. Since we squash-merge, the PR title and description become the commit message on `main` — make them count.

---

# 7. Summary

By following this operating model, we maintain:

- A clean, stable `main` branch
- A predictable, spec-driven flow of work
- Clear traceability from requirements through specs to implementation
- Reduced WIP and higher throughput
- Clear ownership at each stage
- A consistent experience for all contributors
