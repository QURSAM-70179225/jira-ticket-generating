# Brief → Dev Tasks report

Generated 2026-11-05T07:01:59+00:00 with model `openai/gpt-oss-20b`.

## Client brief (numbered)

- **S1** We are FitNow and we want a modern fitness app for our members.
- **S2** It should be fast and user-friendly.
- **S3** Members should be able to book classes and see their workout history.
- **S4** We need this as a mobile app for iPhone and Android.
- **S5** Trainers can create workout plans for members.
- **S6** Members should be able to pay online for memberships.
- **S7** The app must sync with our MBS system so member data stays up to date.
- **S8** It should be secure.
- **S9** Later in the year we also want a leaderboard to keep people motivated.
- **S10** To keep costs low, this should be a web-only product, no app store apps.
- **S11** Admins should get reports.
- **S12** We want to launch soon.

## Open questions for the client

- **Q-001** [contradiction] Which platform should the app be built for: a mobile app for iPhone and Android or a web-only product?  
  Source: S4, S10 "We need this as a mobile app for iPhone and Android."; "To keep costs low, this should be a web-only product, no app store apps." · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007
- **Q-002** [missing] What is the target launch date for the project?  
  Source: S12 "We want to launch soon." · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007
- **Q-003** [missing] Which payment methods are required for online membership payments?  
  Source: S6 "Members should be able to pay online for memberships." · Blocks: TASK-005
- **Q-004** [missing] How should members access the app? Do they need an account or login?  
  Source: S3, S6 "Members should be able to book classes and see their workout history."; "Members should be able to pay online for memberships." · Blocks: TASK-002, TASK-003, TASK-005
- **Q-005** [missing] How should trainers access the system? Do they need an account or login?  
  Source: S5 "Trainers can create workout plans for members." · Blocks: TASK-004
- **Q-006** [missing] How should admins access the system? Do they need an account or login?  
  Source: S11 "Admins should get reports." · Blocks: TASK-001
- **Q-007** [undefined_term] What is the MBS system and what data does it provide?  
  Source: S7 "The app must sync with our MBS system so member data stays up to date." · Blocks: TASK-006
- **Q-008** [scope_gap] What are the rules and criteria for the leaderboard?  
  Source: S9 "Later in the year we also want a leaderboard to keep people motivated." · Blocks: TASK-007
- **Q-009** [scope_gap] What information is required to book a class?  
  Source: S3 "Members should be able to book classes and see their workout history." · Blocks: TASK-002
- **Q-010** [scope_gap] What currency and tax rules should be applied to membership payments?  
  Source: S6 "Members should be able to pay online for memberships." · Blocks: TASK-005
- **Q-011** [vague] What does 'modern' mean in terms of design or features?  
  Source: S1 "We are FitNow and we want a modern fitness app for our members." · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007
- **Q-012** [vague] What performance expectations define 'fast' for the app?  
  Source: S2 "It should be fast and user-friendly." · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007
- **Q-013** [vague] What criteria define 'user-friendly' for the app?  
  Source: S2 "It should be fast and user-friendly." · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007
- **Q-014** [vague] What security requirements must the app meet?  
  Source: S8 "It should be secure." · Blocks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007
- **Q-015** [vague] When exactly do you want the leaderboard feature to be available?  
  Source: S9 "Later in the year we also want a leaderboard to keep people motivated." · Blocks: TASK-007

## Task breakdown


### TASK-001 · Epic: Core Features
Implement the main functionality required for members, trainers and admins as described in the brief  
Source: S1: "We are FitNow and we want a modern fitness app for our members."

- **TASK-002** [Story] Book Classes — _Needs clarification_
- **TASK-003** [Story] View Workout History — _Needs clarification_
- **TASK-004** [Story] Create Workout Plans — _Needs clarification_
- **TASK-005** [Story] Pay Online for Memberships — _Needs clarification_
- **TASK-006** [Story] Sync with MBS System — _Needs clarification_
- **TASK-007** [Story] Implement Leaderboard — _Needs clarification_

## Tickets

### TASK-001 — Core Features

| Field | Value |
|---|---|
| Type | Epic |
| Parent | — |
| Status | Needs clarification (7 open question(s)) |
| Description | Implement the main functionality required for members, trainers and admins as described in the brief |
| Source reference | S1: "We are FitNow and we want a modern fitness app for our members." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- Epic: see child tickets TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007
- Project constraint: We need this as a mobile app for iPhone and Android. [S4]
- Project constraint: To keep costs low, this should be a web-only product, no app store apps. [S10]

**Open questions**

- Q-001: Which platform should the app be built for: a mobile app for iPhone and Android or a web-only product?
- Q-002: What is the target launch date for the project?
- Q-006: How should admins access the system? Do they need an account or login?
- Q-011: What does 'modern' mean in terms of design or features?
- Q-012: What performance expectations define 'fast' for the app?
- Q-013: What criteria define 'user-friendly' for the app?
- Q-014: What security requirements must the app meet?

**Python corrections (AI output not trusted)**

- Constraint S4 was on no task: added as a project constraint ("We need this as a mobile app for iPhone and Android.")
- Constraint S10 was on no task: added as a project constraint ("To keep costs low, this should be a web-only product, no app store apps.")

### TASK-002 — Book Classes

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (8 open question(s)) |
| Description | Members should be able to book classes |
| Source reference | S3: "Members should be able to book classes and see their workout history." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- Members should be able to book classes [S3: "Members should be able to book classes and see their workout history."]

**Open questions**

- Q-009: What information is required to book a class?
- Q-001: Which platform should the app be built for: a mobile app for iPhone and Android or a web-only product?
- Q-002: What is the target launch date for the project?
- Q-004: How should members access the app? Do they need an account or login?
- Q-011: What does 'modern' mean in terms of design or features?
- Q-012: What performance expectations define 'fast' for the app?
- Q-013: What criteria define 'user-friendly' for the app?
- Q-014: What security requirements must the app meet?

### TASK-003 — View Workout History

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (7 open question(s)) |
| Description | Members should be able to see their workout history |
| Source reference | S3: "Members should be able to book classes and see their workout history." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- Members should be able to book classes and see their workout history. [S3: "Members should be able to book classes and see their workout history."]

**Open questions**

- Q-004: How should members access the app? Do they need an account or login?
- Q-001: Which platform should the app be built for: a mobile app for iPhone and Android or a web-only product?
- Q-002: What is the target launch date for the project?
- Q-011: What does 'modern' mean in terms of design or features?
- Q-012: What performance expectations define 'fast' for the app?
- Q-013: What criteria define 'user-friendly' for the app?
- Q-014: What security requirements must the app meet?

**Python corrections (AI output not trusted)**

- Criterion reworded by the AI was replaced by the brief's words: "Members should be able to see their workout history" -> "Members should be able to book classes and see their workout history."

### TASK-004 — Create Workout Plans

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (7 open question(s)) |
| Description | Trainers can create workout plans for members |
| Source reference | S5: "Trainers can create workout plans for members." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- Trainers can create workout plans for members [S5: "Trainers can create workout plans for members."]

**Open questions**

- Q-005: How should trainers access the system? Do they need an account or login?
- Q-001: Which platform should the app be built for: a mobile app for iPhone and Android or a web-only product?
- Q-002: What is the target launch date for the project?
- Q-011: What does 'modern' mean in terms of design or features?
- Q-012: What performance expectations define 'fast' for the app?
- Q-013: What criteria define 'user-friendly' for the app?
- Q-014: What security requirements must the app meet?

### TASK-005 — Pay Online for Memberships

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (9 open question(s)) |
| Description | Members should be able to pay online for memberships |
| Source reference | S6: "Members should be able to pay online for memberships." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- Members should be able to pay online for memberships [S6: "Members should be able to pay online for memberships."]

**Open questions**

- Q-003: Which payment methods are required for online membership payments?
- Q-010: What currency and tax rules should be applied to membership payments?
- Q-004: How should members access the app? Do they need an account or login?
- Q-001: Which platform should the app be built for: a mobile app for iPhone and Android or a web-only product?
- Q-002: What is the target launch date for the project?
- Q-011: What does 'modern' mean in terms of design or features?
- Q-012: What performance expectations define 'fast' for the app?
- Q-013: What criteria define 'user-friendly' for the app?
- Q-014: What security requirements must the app meet?

### TASK-006 — Sync with MBS System

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (7 open question(s)) |
| Description | The app must sync with our MBS system so member data stays up to date |
| Source reference | S7: "The app must sync with our MBS system so member data stays up to date." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- The app must sync with our MBS system so member data stays up to date [S7: "The app must sync with our MBS system so member data stays up to date."]

**Open questions**

- Q-007: What is the MBS system and what data does it provide?
- Q-001: Which platform should the app be built for: a mobile app for iPhone and Android or a web-only product?
- Q-002: What is the target launch date for the project?
- Q-011: What does 'modern' mean in terms of design or features?
- Q-012: What performance expectations define 'fast' for the app?
- Q-013: What criteria define 'user-friendly' for the app?
- Q-014: What security requirements must the app meet?

### TASK-007 — Implement Leaderboard

| Field | Value |
|---|---|
| Type | Story |
| Parent | TASK-001 |
| Status | Needs clarification (8 open question(s); no testable acceptance criteria in the brief) |
| Description | Build the leaderboard feature to keep people motivated |
| Source reference | S9: "Later in the year we also want a leaderboard to keep people motivated." |
| Dependencies | None stated in the brief |
| Priority | Not specified |
| Estimate | Not specified |
| Deadline | Not specified |

**Acceptance criteria**

- Not specified (the brief gives no testable condition; see open questions)

**Open questions**

- Q-001: Which platform should the app be built for: a mobile app for iPhone and Android or a web-only product?
- Q-008: What are the rules and criteria for the leaderboard?
- Q-012: What performance expectations define 'fast' for the app?
- Q-013: What criteria define 'user-friendly' for the app?
- Q-014: What security requirements must the app meet?
- Q-002: What is the target launch date for the project?
- Q-011: What does 'modern' mean in terms of design or features?
- Q-015: When exactly do you want the leaderboard feature to be available?

## Verification (Python checks against the brief)

- Quotes checked: 51
- Issues found: 7
- AI priorities/deadlines/estimates rejected: 0
- Reworded acceptance criteria replaced with the brief's words: 1
- Tickets ready: 0 · needing clarification: 7
- Uncovered features: ['R1', 'R2', 'R3']
- Brief sentences not used anywhere: ['S2', 'S8', 'S12']
- Coverage repair needed: True

- ⚠ **unknown_feature** at question Q-006 affects: "Admins should get reports" is not an extracted feature
- ⚠ **uncovered** at work item R1: no task covers this feature/requirement
- ⚠ **uncovered** at work item R2: no task covers this feature/requirement
- ⚠ **uncovered** at work item R3: no task covers this feature/requirement
- ⚠ **sentence_unused** at brief sentence S2: "It should be fast and user-friendly." does not appear on any ticket - review by hand
- ⚠ **sentence_unused** at brief sentence S8: "It should be secure." does not appear on any ticket - review by hand
- ⚠ **sentence_unused** at brief sentence S12: "We want to launch soon." does not appear on any ticket - review by hand
