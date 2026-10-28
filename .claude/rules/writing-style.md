---
paths:
  - "Knowledge/**"
  - "Examples/**"
  - "Exercises/**"
  - "Scenarios/**"
---

# Writing style: encyclopedic prose and LaTeX, used when they help

Everything is written from your own knowledge (no lookups). That is why equations and numbers are flagged for checking. You decide when each device below is needed; do not log those routine choices in `DECISIONS.md`.

## Voice depends on the kind of note

- **Encyclopedic voice** for `kb` notes of kind concept, reference, glossary, faq, case-study and index: third person, present tense, neutral, with a Wikipedia-style lead. The lead is the first paragraph, two to four sentences, and says what the thing is, where it is used and why it matters. Bold the term once in the lead. Do not use "you".
- **Instructional voice** for how-to, troubleshooting, checklist, `example`, `exercise` and `scenario`: direct and practical, second person is fine, steps are numbered.

## Encyclopedic rules

- Define a term at first use in a note, and wiki-link it once if a note for it exists. Do not link every mention.
- Avoid promotional or vague words ("powerful", "crucial", "simply", "obviously", "many experts say"). Attribute judgement calls to practice, not to you: "common practice is...", "designers often prefer...".
- Short paragraphs. Sentence-case headings, no skipped levels. The note title is the only `#` heading.
- End with **See also** where it helps.
- Style only: write everything in your own words. Do not copy or closely paraphrase Wikipedia or any other source, and do not use citation markers such as [1] or "citation needed". Sourcing goes in `references` and `standards`, and by naming the standard or book in the prose.

## Units and numbers

SI first, with the common board units where the field uses them (mm and mil, oz copper). Put a space between number and unit, use the degree sign for temperature, and keep units consistent within a note. In cost notes write "USD 5", not "$5", so the dollar sign is never read as math.

## LaTeX: only when an equation is needed

Obsidian renders `$...$` inline and `$$...$$` as a display block.

- Use LaTeX for a relationship with real structure (a formula, a derived expression, a ratio of several terms). Keep trivial things in plain text, such as "5 V", "0.5 mm" or "10 mΩ".
- Define every symbol with its unit directly after the equation, and name the relationship in words ("the trace resistance equation").
- Name the source by standard or book where there is one, and never reproduce a standard's own tables or text.
- No LaTeX in frontmatter, headings, tags or file names.
- Never write an equation you are unsure of. Equations written from memory are the main accuracy risk: add every equation, with the note name, to `NEEDS-VERIFICATION.md`, and give a typical range or a plain-language statement instead if you are not confident.
- Check multi-step arithmetic in worked examples with a quick local script instead of by hand. Say in `NEEDS-VERIFICATION.md` that the arithmetic was script-checked; that does not make the physics verified.

## Self-review before saving a note

- Does the lead make sense on its own?
- Is every claim basic fundamentals, attributed, or flagged in `NEEDS-VERIFICATION.md`?
- Is every term defined at first use, and every number given with its unit?
- Would the reader know what to read or do next (See also, `next`, a linked exercise)?
- Is there anything you can cut without losing teaching value?
