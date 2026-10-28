---
paths:
  - "_meta/**"
---

# Coverage audit and growth (no fixed cap)

The outline is a starting point, not a limit. The goal is that the domain covers what a competent practitioner would expect, and you keep adding until usage runs out. The order of work protects the core.

## Collect candidates as you write

Whenever you notice a missing prerequisite, a topic a note assumes but nothing teaches, a common mistake or decision worth its own note, or a gap against the domain file's coverage checklist, append one line to `_meta/domains/<domain>/CANDIDATES.md`: proposed file name, type, section, level, why, and priority.

- **P1:** a learner cannot follow existing notes without it.
- **P2:** a core topic the domain should have.
- **P3:** useful depth.

Do not write a candidate in the middle of a batch, with one exception: a missing prerequisite that blocks the note you are writing is written first.

## When to audit

- **End of each Pass A section:** list the section's notes, compare them with the domain file's plan and coverage checklist, and add candidates.
- **Pass D (gap-fill):** starts only when Passes A, B and C are complete. Work through candidates in order P1, P2, P3, until usage runs out or none remain. Before finishing, run one last audit with a fresh read of the coverage checklist.

## Relevance test (every candidate must pass)

- It is in the domain's scope and not a duplicate (search existing file names and descriptions).
- It links to at least two existing notes.
- It fits an existing section. If none fits, append a new section value for this domain (append-only, with the domain prefix), and record why in `DECISIONS.md`.
- Its file name is unique across the vault.

## Bookkeeping

Add each new file to `OUTLINE.md` under "Added during build" with its reason, tick it in `PROGRESS.md`, and give it the same validation, honesty and style rules as planned files. `REPORT.md` states how many files and sections were added and which candidates remain unwritten.
