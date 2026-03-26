## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `bash .specify/scripts/bash/setup-design.sh --json` from repo root and parse JSON for FEATURE_SPEC, DESIGN, FEATURE_DIR, BRANCH.

2. **Load context**: Read FEATURE_SPEC and `specs/constitution.md`. Load the design template at `.specify/templates/design-template.md` (DESIGN already copied by script). Also read `specs/.architecture/06-tech-stack.md` and `specs/.architecture/07-decisions.md` for project-wide technology context and architectural decisions that inform the design.

3. **Execute design workflow**: Follow the structure in the design template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Evaluate constitution gates after Phase 1 design is complete. If MUST principles are violated without justification, ERROR and halt.

4. **Stop and report**: Command ends after Phase 1 design. Report branch, DESIGN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context**:
   - For each NEEDS CLARIFICATION -> research task
   - For each dependency -> best practices task
   - For each integration -> patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** -> `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action -> endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `bash .specify/scripts/bash/update-agent-context.sh claude`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current design
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

## Key Rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications
- All design artifacts go in FEATURE_DIR alongside the spec
- The output file is `design.md`

## Sub-spec Handling

Sub-specs (`YYMM-NNN.N`) are independent specs that inherit no parent state. They go through the full design lifecycle independently — design artifacts are scoped entirely to the sub-spec's own `spec.md`.

## Status Sync (automatic)

After the design is complete, update the spec's YAML frontmatter:

1. Open the spec.md file in FEATURE_DIR.
2. Update the frontmatter `status` field to `"planning"`.
3. Update the frontmatter `updated` field to today's date (YYYY-MM-DD).
4. Do NOT edit any project plan files — live status is derived from
   frontmatter by `/ais.report.*` commands.
