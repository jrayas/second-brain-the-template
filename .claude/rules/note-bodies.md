---
paths:
  - "Knowledge/**"
  - "Examples/**"
---

# Body templates: kb notes and examples

Use `[[File name]]` wiki-links for every cross-reference. Do not repeat the title as plain text beyond the `#` heading.

## kb (adapt sections to `kind`, keep the order)

```markdown
# Title

**Term** is ... (the lead: two to four sentences on what it is, where it is used and why it matters; see `writing-style.md`. Instructional kinds such as how-to may open with a one-line goal instead.)

## Why it matters
## Core idea
## Step by step (or: Key concepts / Reference table)
## Common mistakes
## Checklist
## Senior notes (trade-offs, edge cases, what experience teaches)
## See also
- [[Related note name]]
```

Aim for roughly 400 to 900 words. Reference notes may be shorter; advanced concept notes longer. `kind: index` notes are maps of content: a short orientation paragraph, then links grouped by level in reading order, then the exercises, scenarios and visuals for the section, and the section's lesson page (set as the note's `companion` in Pass C).

## example

```markdown
# Title

## Problem
## Given
## Solution (numbered steps, units shown, working shown)
## Check (a sanity check on the result)
## What to take from this
## Variations to try
```

Show every unit. Every number in the worked solution goes into the domain's `NEEDS-VERIFICATION.md` unless it is simple arithmetic from the stated givens.
