---
name: "ais-spec-tasks"
description: "Generate dependency-ordered task list and validate cross-artifact consistency."
handoffs:
  - label: Implement Project
    agent: ais-spec-implement
    prompt: Start the implementation in phases
    send: true
---

<!-- Generated from .specify/prompts/ais.spec.tasks.md — do not edit directly -->

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `bash .specify/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: design.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (API endpoints), research.md (decisions), quickstart.md (test scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load design.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map endpoints to user stories
   - If research.md exists: Extract decisions for setup tasks
   - Generate tasks organized by user story (see Task Generation Rules below)
   - Generate dependency graph showing user story completion order
   - Create parallel execution examples per user story
   - Validate task completeness (each user story has all needed tasks, independently testable)

4. **Pre-flight check**: If `tasks.md` already exists in FEATURE_DIR, check for completed tasks (`[x]` or `[X]`). If completed tasks are found, warn the user: "Existing tasks.md has {N} completed tasks. Regenerating will overwrite all progress." Offer options: **(A)** Overwrite — replace tasks.md entirely, **(B)** Create as `tasks-v2.md` — preserve original, **(C)** Abort. Wait for user response before proceeding.

5. **Generate tasks.md**: Use `.specify/templates/tasks-template.md` as structure, fill with:
   - Correct feature name from design.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories)
   - Phase 3+: One phase per user story (in priority order from spec.md)
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Phase: Polish & cross-cutting concerns
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Dependencies section showing story completion order
   - Parallel execution examples per story
   - Implementation strategy section (MVP first, incremental delivery)

6. **Consistency Check** (absorbed from analyze): After generating tasks.md, automatically run a validation pass:

   a. **Build semantic models**:
      - **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug from imperative phrase; e.g., "User can upload file" -> `user-can-upload-file`)
      - **Task coverage mapping**: Map each task to one or more requirements or stories (by keyword / explicit reference patterns)
      - **Constitution rule set**: Load `specs/constitution.md` and extract principle names and MUST/SHOULD normative statements
      - **Cross-spec context**: Read `specs/*/spec.md` frontmatter for inter-spec dependencies and `specs/.architecture/06-tech-stack.md` for technology decisions

   b. **Run detection passes** (focus on high-signal findings, limit to 30 findings total):

      - **Duplication**: Near-duplicate requirements; mark lower-quality phrasing for consolidation
      - **Ambiguity**: Vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria; unresolved placeholders (TODO, TKTK, ???, `<placeholder>`)
      - **Underspecification**: Requirements with verbs but missing object or measurable outcome; user stories missing acceptance criteria alignment; tasks referencing files or components not defined in spec/plan
      - **Constitution alignment**: Requirements or plan elements conflicting with a MUST principle; missing mandated sections or quality gates
      - **Coverage gaps**: Requirements with zero associated tasks; tasks with no mapped requirement/story; non-functional requirements not reflected in tasks
      - **Inconsistency**: Terminology drift (same concept named differently); data entities in plan but absent in spec (or vice versa); task ordering contradictions; conflicting requirements

   c. **Assign severity**:
      - **CRITICAL**: Violates constitution MUST, missing core artifact, or requirement with zero coverage blocking baseline functionality
      - **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
      - **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
      - **LOW**: Style/wording improvements, minor redundancy

   d. **Append Consistency Check section** to the task report output (NOT to the tasks.md file itself):

      ```markdown
      ## Consistency Check

      | ID | Category | Severity | Location(s) | Summary | Recommendation |
      |----|----------|----------|-------------|---------|----------------|

      **Coverage**: X/Y requirements mapped (Z%)
      **Issues**: N critical, N high, N medium, N low
      ```

   e. **Act on results**:
      - If CRITICAL issues found: Warn user and recommend resolving before proceeding to `/ais.spec.implement`. List specific remediation steps.
      - If only LOW/MEDIUM: Note them and proceed. User may address at their discretion.

7. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)
   - Consistency check results summary

Context for task generation: $ARGUMENTS

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **[Story] label**: REQUIRED for user story phase tasks only
   - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md)
   - Setup phase: NO story label
   - Foundational phase: NO story label
   - User Story phases: MUST have story label
   - Polish phase: NO story label
5. **Description**: Clear action with exact file path

**Examples**:

- CORRECT: `- [ ] T001 Create project structure per implementation plan`
- CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- WRONG: `- [ ] Create User model` (missing ID and Story label)
- WRONG: `T001 [US1] Create model` (missing checkbox)
- WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** - PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own phase
   - Map all related components to their story:
     - Models needed for that story
     - Services needed for that story
     - Endpoints/UI needed for that story
     - If tests requested: Tests specific to that story
   - Mark story dependencies (most stories should be independent)

2. **From Contracts**:
   - Map each contract/endpoint -> to the user story it serves
   - If tests requested: Each contract -> contract test task [P] before implementation in that story's phase

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it
   - If entity serves multiple stories: Put in earliest story or Setup phase
   - Relationships -> service layer tasks in appropriate story phase

4. **From Setup/Infrastructure**:
   - Shared infrastructure -> Setup phase (Phase 1)
   - Foundational/blocking tasks -> Foundational phase (Phase 2)
   - Story-specific setup -> within that story's phase

### Phase Structure

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each story: Tests (if requested) -> Models -> Services -> Endpoints -> Integration
  - Each phase should be a complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns

## Sub-spec Handling

Sub-specs (`YYMM-NNN.N`) are independent specs that inherit no parent state. They go through the full task generation lifecycle independently — tasks are scoped entirely to the sub-spec's own `spec.md` and `design.md`.

## Status Sync (automatic)

After tasks are generated, update the spec's YAML frontmatter:

1. Open the spec.md file in FEATURE_DIR.
2. Update the frontmatter `status` field to `"ready"`.
3. Update the frontmatter `updated` field to today's date (YYYY-MM-DD).
4. Do NOT edit any project plan files — live status is derived from
   frontmatter by `/ais.report.*` commands.
