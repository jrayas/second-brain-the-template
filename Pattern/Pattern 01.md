# CLAUDE.md: Second Brain the Project

## Purpose

This vault is for planning and documenting projects properly, from first idea to finished result. It holds **documentation and planning only, not code**. Its second job is to capture the facts a resume needs (tools, my role, actions, metrics) while they are fresh, so a good summary can be exported to the Resume Vault when a project closes.

## Ground rules

1. **No code.** Do not write, paste or generate code, scripts, queries or plugins. Describe approaches in words. If code would genuinely help, say so and ask me first.
2. **Never invent results.** Every metric, test outcome or claim must come from me or from a logged test. Label estimates as estimates. If a number is missing, ask.
3. **Always separate my work from the team's.** Record what I personally did.
4. **Name things specifically.** Exact components, software, versions and standards, not "a sensor" or "some software".
5. **Ask one question at a time** when information is missing, and make it specific.
6. **Use British English.**
7. **Never delete or overwrite** a project note without being asked. Add dated entries instead.

## Vault structure

```
Second Brain the Project/
├── CLAUDE.md
├── Templates/                    # One full set of 00 to 07 templates per subject
│   ├── Electronics/
│   ├── Electrical/
│   └── Computer Science/
├── Knowledge/                    # Guides on good documentation and capturing metrics
├── Projects/
│   ├── Electronics/
│   ├── Electrical/
│   └── Computer Science/
│       └── YYYY Project Name/
│           ├── 00 Overview.md
│           ├── 01 Requirements.md
│           ├── 02 Plan.md
│           ├── 03 Design.md
│           ├── 04 Log.md
│           ├── 05 Testing.md
│           ├── 06 Results.md
│           └── 07 Resume Summary.md
└── Archive/                      # Closed or abandoned projects
```

If a folder or note is missing, tell me and ask before creating it. Use tags for anything that crosses subjects. Pick one home folder per project.

## What each note holds

- **00 Overview**: frontmatter (title, subject, status, tags, dates, role, tools), the problem in one sentence, the goal, and success criteria.
- **01 Requirements**: what the project must do, constraints (budget, time, standards, safety), and assumptions.
- **02 Plan**: milestones with dates, tasks, dependencies, risks and a parts or resources list.
- **03 Design**: approach, options considered, decisions made and why, block diagrams described in words or linked images, and specific components and tools.
- **04 Log**: dated entries. What I did, what happened, problems, fixes and next steps. Append only.
- **05 Testing**: what was tested, how, expected versus actual, and pass or fail.
- **06 Results**: measured outcomes with numbers, before and after comparisons, and what I would change.
- **07 Resume Summary**: the export, written only at close-out (see below).

## Project status

Projects begin here only after the idea has been approved in the Planning vault. Use `status` in the Overview frontmatter: `planning`, `in-progress`, `testing`, `complete`, `paused`, `abandoned`.

When I change status, check the notes that stage needs are filled in and tell me what is missing. For example, a project cannot move to `testing` with no Requirements, and cannot be `complete` with no Results.

## Capturing resume evidence as we go

While I log work, quietly watch for resume material and prompt me to record it:

- Any number: sizes, speeds, accuracy, power, cost, time saved, counts, users.
- Before and after comparisons.
- Tools, standards and methods used, with exact names.
- Decisions I made on my own and problems I solved.
- Anything delivered early, under budget or recognised by someone.

When I log something vague (for example "improved the circuit"), ask one specific follow-up ("improved by how much, measured how?") and add the answer to Results.

## Workflows

**New project.** If I bring a plan shipped from the Planning vault, use it as the starting content for Overview, Requirements and Plan, and ask only about what is missing. Otherwise ask what it is, why, and what done looks like. Create the folder and fill 00 Overview and 01 Requirements from my answers. Draft 02 Plan only after I confirm the requirements.

**Daily or weekly log.** I tell you what I did. Turn it into a dated entry in 04 Log, update the Plan if milestones moved, and prompt me for any missing evidence.

**Close-out and resume export.** When I say a project is finished:

1. Check 05 Testing and 06 Results are complete. Ask about any gaps.
2. Write `07 Resume Summary.md` in exactly the format the Resume Vault expects (below), using only facts recorded in this vault.
3. Mark it `status: ready` only if the minimum bar is met (problem, my role, specific tools, 2 to 4 actions, a result with a number or clear outcome, tags). Otherwise mark it `draft` and list what is missing.
4. Tell me to copy the note into the Resume Vault under `Library/<Subject>/`. Do not write to the Resume Vault yourself.

## Resume Summary format

```yaml
---
title:
subject: Electronics | Electrical | Computer Science
status: draft | ready
tags: []
dates:
role:
tools: []
outcome:
metrics:
---
```

Below the frontmatter: a two-line overview, then 3 to 5 resume-ready bullets (one or two lines each, strong verb, what, how, result).

## Tag conventions

- Lowercase and hyphenated: `embedded-systems`, `pcb-design`, `power-electronics`.
- Three kinds: **skills** (`signal-processing`), **tools** (`matlab`, `kicad`), **domain** (`iot`, `renewable-energy`).
- One tag per concept. Reuse existing tags before making new ones.
- Prefer the words job ads use.

## Output style

- Lead with the result, then the detail.
- Keep notes scannable: short sections, specifics over adjectives.
- Dates in YYYY-MM-DD.
- If something is ambiguous, ask one question rather than guessing.
