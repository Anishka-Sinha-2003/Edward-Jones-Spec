# Statement of Work

| Field | Value |
|-------|-------|
| **Client** | [Client name] |
| **Date** | [YYYY-MM-DD] |
| **Version** | 1.0 |
| **AIS Contact** | [Name, title] |
| **Client Contact** | [Name, title] |
| **Proposal** | [Link to proposal.md] |

---

## Purpose

[1-2 paragraphs describing the engagement purpose, referencing the agreed-upon approach from the proposal.]

---

## Scope of Services

### In Scope

| # | Deliverable | Description | Acceptance Criteria | Spec |
|---|------------|-------------|--------------------|------|
| 1 | [Deliverable name] | [What AIS will deliver] | [How client accepts it] | [Spec name] |
| 2 | [Deliverable] | [Description] | [Criteria] | [Spec name] |

### Out of Scope

- [Explicitly excluded item with rationale]
- [Excluded item]

### Assumptions

- [Scope assumption about client responsibilities]
- [Assumption about access, environments, or dependencies]
- [Assumption about change management]

---

## Spec Catalog

Formal spec entries that map to SOW deliverables. Each becomes a delivery spec (YYMM-NNN) at project kickoff via `/ais.setup.plan`.

### [Spec Name 1]

| Field | Value |
|-------|-------|
| **Purpose** | [What this spec delivers and why] |
| **Scope** | [Bullet list of what's included] |
| **Out of Scope** | [What's excluded from this spec] |
| **Dependencies** | [Other specs or external dependencies] |
| **Effort** | S / M / L / XL |
| **Deliverables** | [Which SOW deliverables this maps to] |

### [Spec Name 2]

| Field | Value |
|-------|-------|
| **Purpose** | [Purpose] |
| **Scope** | [Scope] |
| **Out of Scope** | [Exclusions] |
| **Dependencies** | [Dependencies] |
| **Effort** | |
| **Deliverables** | [SOW deliverable mapping] |

---

## Milestones and Timeline

| # | Milestone | Description | Target Date | Deliverables | Specs |
|---|-----------|-------------|------------|-------------|-------|
| M1 | [Milestone name] | [What's delivered] | [Date or TBD] | [Deliverable #s] | [Spec names] |
| M2 | [Milestone] | [Description] | | | |

---

## Pricing and Payment

> *[Placeholder — to be completed by business team]*

| Milestone | Amount | Payment Terms |
|-----------|--------|--------------|
| M1 | [Amount] | [Terms] |
| M2 | [Amount] | [Terms] |
| **Total** | **[Amount]** | |

---

## Team and Responsibilities

### AIS Team

| Role | Responsibility | Allocation |
|------|---------------|------------|
| [Role] | [What they do] | [Full-time / Part-time / As-needed] |

### Client Team

| Role | Responsibility | Availability |
|------|---------------|-------------|
| [Role] | [What we need from them] | [Expected availability] |

---

## Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|----|------|-----------|--------|------------|-------|
| R-001 | [Risk] | Medium | High | [Mitigation] | [AIS / Client] |

---

## Change Management

[Process for handling scope changes, additional requirements, or reprioritization during the engagement.]

- Change requests require written documentation
- Impact assessment (effort, timeline, cost) provided within [N] business days
- Changes to spec scope require mutual agreement
- [Additional change management terms]

---

## Clarifying Questions

### QA — Resolved Assumptions

| # | Question | Resolution | Resolved Date |
|---|----------|-----------|---------------|
| 1 | [Previously open question] | [How it was resolved] | [Date] |

### QC — Pending Client Items

| # | Question | What It Blocks | Target Date |
|---|----------|---------------|------------|
| 1 | [Still-open question] | [Impact] | [When needed] |

---

## Information Gaps

| Gap | Impact | Resolution Plan |
|-----|--------|----------------|
| [Remaining gap] | [What it affects] | [How and when to resolve] |

---

## Delivery Methodology

This engagement follows the AIS spec-driven development methodology:

1. **Project setup**: `/ais.setup.plan` reads this SOW as a T1 source, creates spec directories with YYMM-NNN identifiers, and produces the project plan
2. **Architecture**: `/ais.setup.architecture` generates the solution architecture and technical decisions
3. **Spec lifecycle**: Each delivery spec progresses through specify → design → tasks → implement
4. **Status tracking**: Progress is derived from repo state and reported via `/ais.report.status`

---

## Signatures

| Party | Name | Title | Signature | Date |
|-------|------|-------|-----------|------|
| **AIS** | | | | |
| **Client** | | | | |
