---
paths:
  - "Knowledge/**"
  - "Examples/**"
  - "Exercises/**"
  - "Scenarios/**"
  - "Visuals/*.md"
---

# Frontmatter: one validated example per type

> The examples below keep file names and wording from the first build (a printed-circuit-board domain). Only their shape matters: copy the property order and the value types, and use your own domain slug, sections and tracks. The `starter` domain, its sections and its track are placeholders until the first real domain replaces them.

These examples were checked against the schema pack. Follow the property order and the quoting exactly. Shared conventions: `schema: 1`, a generated `id`, `name` equal to the file name, `status: review`, `language: en-GB`, `domain` equal to the active domain, `unique_id` right after it, `created` and `modified` last.

**kb**, file `Knowledge/<domain>/Decoupling capacitor placement.md`:

```yaml
---
type: kb
schema: 1
id: KB-2026-0001
name: Decoupling capacitor placement
status: review
aliases: [bypass capacitors]
description: Where to place decoupling capacitors and how to route them so they work.
tags: [decoupling, power-integrity, layout]
language: en-GB
parent: "[[Power and thermal index]]"
related: ["[[Return paths and current loops]]"]
supersedes: []
review_cycle: 6-months
domain: starter
unique_id: KB-PC-2026-0001
section: starter-start-here
level: intermediate
topic: decoupling
order: 40
track: [starter-first-path, starter-first-path]
prerequisites: ["[[Power distribution basics]]"]
next: "[[Plane capacitance and stack-up]]"
companion: "[[Decoupling loop area]]"
ai_generated: true
generated_by: claude-code
verified: false
standards: []
kind: how-to
audience: self
confidence: medium
created: 2026-10-21T10:00
modified: 2026-10-21T10:00
---
```

**example**, file `Examples/<domain>/Sizing a decoupling capacitor for a microcontroller rail.md`:

```yaml
---
type: example
schema: 1
id: EG-2026-0001
name: Sizing a decoupling capacitor for a microcontroller rail
status: review
aliases: []
description: A worked example choosing capacitor values and positions for a 3.3 V microcontroller rail.
tags: [decoupling, power-integrity]
language: en-GB
related: []
supersedes: []
review_cycle: 6-months
domain: starter
unique_id: EG-PC-2026-0001
section: starter-start-here
level: intermediate
order: 45
track: [starter-first-path]
prerequisites: ["[[Decoupling capacitor placement]]"]
ai_generated: true
verified: false
standards: []
demonstrates: "[[Decoupling capacitor placement]]"
difficulty: intermediate
confidence: medium
created: 2026-10-21T10:00
modified: 2026-10-21T10:00
---
```

**exercise**, file `Exercises/<domain>/Where should the capacitor go.md`:

```yaml
---
type: exercise
schema: 1
id: EX-2026-0001
name: Where should the capacitor go
status: review
aliases: []
description: Decide which of three capacitor positions gives the smallest current loop.
tags: [decoupling, layout]
language: en-GB
related: []
supersedes: []
review_cycle: 6-months
domain: starter
unique_id: EX-PC-2026-0001
section: starter-start-here
level: intermediate
order: 46
track: [starter-first-path]
prerequisites: []
ai_generated: true
verified: false
standards: []
difficulty: intermediate
time_minutes: 10
tests: ["[[Decoupling capacitor placement]]"]
answer_verified: false
confidence: medium
created: 2026-10-21T10:00
modified: 2026-10-21T10:00
---
```

**scenario**, file `Scenarios/<domain>/The board passes every test but fails EMC at 240 MHz.md`:

```yaml
---
type: scenario
schema: 1
id: SC-2026-0001
name: The board passes every test but fails EMC at 240 MHz
status: review
aliases: []
description: A board passes functional test but fails radiated emissions at one frequency.
tags: [emi-emc, debugging]
language: en-GB
related: []
supersedes: []
review_cycle: 6-months
domain: starter
unique_id: SC-PC-2026-0001
section: starter-start-here
level: senior
order: 90
track: [starter-first-path]
prerequisites: []
ai_generated: true
verified: false
standards: []
decision_type: diagnosis
difficulty: senior
time_minutes: 20
tests: ["[[Return paths and current loops]]"]
senior_signal: Checks return paths and cable common-mode current before changing the layout.
answer_verified: false
confidence: low
created: 2026-10-21T10:00
modified: 2026-10-21T10:00
---
```

**visual stub**, file `Visuals/<domain>/Decoupling loop area.md` (paired with `Visuals/<domain>/html/decoupling-loop-area.html`):

```yaml
---
type: visual
schema: 1
id: VS-2026-0001
name: Decoupling loop area
status: review
aliases: []
description: Interactive diagram comparing good and bad decoupling capacitor placement.
tags: [decoupling, layout]
language: en-GB
related: []
supersedes: []
review_cycle: 6-months
domain: starter
unique_id: VS-PC-2026-0001
section: starter-start-here
level: intermediate
order: 41
track: [starter-first-path]
prerequisites: []
companion: "[[Decoupling capacitor placement]]"
ai_generated: true
verified: false
standards: []
kind: diagram
file: Visuals/<domain>/html/decoupling-loop-area.html
tested: false
confidence: medium
created: 2026-10-21T10:00
modified: 2026-10-21T10:00
---
```

## Property guidance

- `domain` is the domain slug and equals the note's folder under its type folder. `section` and every `track` value start with that slug and a hyphen.
- `parent` points to the section's index note (a `kb` note with `kind: index`), so every note is reachable from the domain's start-here note.
- `order` uses gaps of 10 (10, 20, 30, and so on) and is unique within a `section`, across all note types.
- `prerequisites`, `next`, `companion`, `demonstrates` and `tests` hold quoted wiki-links to files that exist. `demonstrates` and `tests` must point to `kb` notes. A kb note and its visual point at each other through `companion`.
- `description` is one sentence, 160 characters at most. `references` and `standards` hold plain strings (standards by name only).
