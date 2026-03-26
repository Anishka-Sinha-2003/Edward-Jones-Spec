# Tasks: [FEATURE NAME]

**ID**: [YYMM-NNN] | **Spec**: [link] | **Design**: [link]

## Format

```
- [ ] [ID] [P?] [Story?] Description with file path
```

- **[P]** = parallelizable (different files, no dependency on incomplete tasks)
- **[USn]** = user story reference (required in story phases, omitted in setup/polish)

## Phase 1: Setup

- [ ] T001 Create project structure per design
- [ ] T002 Initialize project with dependencies

## Phase 2: Foundation

- [ ] T003 [Blocking prerequisite for all stories]
- [ ] T004 [P] [Another blocking prerequisite]

## Phase 3: [User Story 1 Title] (P1)

**Goal**: [What this story delivers]
**Independent test**: [How to verify in isolation]

- [ ] T005 [P] [US1] Create [Model] in src/models/[file]
- [ ] T006 [US1] Implement [Service] in src/services/[file]
- [ ] T007 [US1] Implement [endpoint/feature] in src/[file]

## Phase 4: [User Story 2 Title] (P2)

**Goal**: [What this story delivers]
**Independent test**: [How to verify in isolation]

- [ ] T008 [P] [US2] Create [Model] in src/models/[file]
- [ ] T009 [US2] Implement [Service] in src/services/[file]

## Phase N: Polish

- [ ] TXXX [P] Documentation updates
- [ ] TXXX Code cleanup and optimization

## Dependencies

- **Setup** → no dependencies, start immediately
- **Foundation** → depends on Setup; blocks all stories
- **Stories** → depend on Foundation; can run in parallel or sequential by priority
- **Polish** → depends on desired stories being complete
