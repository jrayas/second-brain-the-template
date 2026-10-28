---
paths:
  - "Visuals/**"
  - "tools/visuals/src/**"
---

# Lesson pages: one long-scroll page per section

A lesson is a guided tour of one section, built as a single HTML page that scrolls smoothly from start to finish. It is not a copy of the notes: it teaches the spine of the section in 20 to 40 minutes and sends the reader to the notes for depth. Design and accessibility rules are in `html-visuals.md`.

## Naming and links

- One lesson per section (including start-here and reference), built in Pass C after the section's notes and visuals exist.
- Stub note: `Visuals/<domain>/<Section title> lesson.md`, with `kind: lesson` and the same `section` as the section it covers. HTML file: `Visuals/<domain>/html/<section-slug>-lesson.html`, where the slug is the section value without the domain prefix.
- The stub's `companion` is the section's index note (a `kb` note with `kind: index`). The index note's `companion` is the lesson. The stub's `parent` is also the index note.

```yaml
---
type: visual
schema: 1
id: VS-2026-0002
name: Power and thermal lesson
status: review
aliases: []
description: A guided long-scroll lesson on power distribution, decoupling and thermal design.
tags: [lesson, power-integrity, thermal]
language: en-GB
parent: "[[Power and thermal index]]"
related: []
supersedes: []
review_cycle: 6-months
domain: starter
unique_id: VS-PC-2026-0002
section: starter-start-here
level: intermediate
order: 5
track: [starter-first-path]
prerequisites: []
companion: "[[Power and thermal index]]"
ai_generated: true
generated_by: claude-code
verified: false
standards: []
kind: lesson
file: Visuals/<domain>/html/power-thermal-lesson.html
tested: false
confidence: medium
created: 2026-10-21T10:30
modified: 2026-10-21T10:30
---
```

## Structure of the page

1. **Hero:** title, who it is for, estimated time, three to five learning objectives.
2. **Contents:** sticky, with the current section highlighted as the reader scrolls, and a thin progress bar.
3. **Five to nine sections.** Each has a hook (a question or a surprising fact), an explanation led by a diagram or an interaction, one quick check, and a "common mistake".
4. **Closing:** a summary, a self-test of five questions, and "where next" listing the notes, exercises and scenarios by exact file name.

## Content rules

- Draw only from the section's notes, so the lesson never contradicts them. If a lesson needs a fact that no note holds, add it to a note first (flagged for verification), then use it.
- Every number matches the note it comes from.
- Roughly 1,500 to 3,000 words of visible text, two to five interactive elements, and a page under 400 KB.
- Reuse the shared components in `tools/visuals/src/shared/`. Do not copy design code from page to page.
- Answers and explanations in quick checks come from the notes' own worked answers.
