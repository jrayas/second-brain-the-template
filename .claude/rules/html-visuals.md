---
paths:
  - "Visuals/**"
  - "tools/visuals/src/**"
---

# HTML pages: design, learning experience and quality

Applies to every page, visuals and lessons. Build mechanics are in `html-build.md`; lesson structure is in `lesson-pages.md`.

## What a page is

- One self-contained HTML file in `Visuals/<domain>/html/`, built from JSX sources in `tools/visuals/src/<domain>/`. Never edit a built file by hand: change the source and rebuild.
- Technology: Preact with JSX, Tailwind CSS compiled at build time, everything inlined into the one file.
- **Static first.** The content is pre-rendered into the HTML, so the page reads correctly when scripts are blocked (several Obsidian HTML viewers block scripts by default). Scripts only add interactivity.
- **No network at runtime:** no CDN, web fonts, remote images or `fetch`. Use the system font stack and inline SVG.

## Design standards

- Calm, technical, high contrast. One accent colour per domain; the same semantic colours for good, bad and warning on every page, defined once in the shared theme.
- Body text around 17 to 18 px, line height 1.6, line length 60 to 75 characters, a clear heading scale. Generous spacing; no walls of text.
- Single column on phones. On wide screens, a reading column with a sticky contents panel beside it.
- Light and dark mode through `prefers-color-scheme` (Tailwind `dark:`), with contrast checked in both.
- **Smooth scrolling:** CSS `scroll-behavior: smooth`, `scroll-mt-*` on anchored sections, switched off under `prefers-reduced-motion`.
- Motion only when it explains something; short, and stoppable.
- A print style: hide navigation and expand collapsed content.

## Learning experience

- Open with what the reader will learn and roughly how long it takes.
- Show, then explain: put the diagram or interaction before the paragraph that explains it, with a "What to notice" caption.
- Make the reader predict: ask a question, or offer a slider, before revealing the result.
- Quick checks use collapsible answers or multiple choice with instant feedback, including an explanation for each wrong choice. They are never required.
- Controls show a live readout with units, stay within safe ranges and have a reset button.
- End with a short summary, the common mistakes, and "where next" naming the next notes by their exact file names.

## Accessibility

- Landmarks (`header`, `nav`, `main`), one `h1`, headings in order, a skip link.
- Everything works by keyboard with a visible focus. Buttons are buttons; use `aria-expanded`, and `aria-live="polite"` for readouts.
- SVG has `<title>` and `<desc>`. Colour never carries meaning alone.
- Touch targets of at least 44 px; usable at 320 px width and at 200% zoom.

## Calculators

- Show the formula (plain text, Unicode or SVG, never a LaTeX library), its source (a standard named by number, never reproduced), the units, the valid range, and a warning outside it.
- The logic lives in a plain module that exports `tests` (known inputs and expected outputs). The build runs them in Node. Set `tested: true` only when they pass and the result is recorded.
- Do not build a calculator whose formula you cannot attribute. The stub needs `formula_source`.

## Required on every page

`<title>`, `lang="en-GB"`, the viewport meta tag, the companion note's name, and this notice: "Educational aid; verify against current standards and the manufacturer's rules."

## Stub notes

Every page has a stub note directly in `Visuals/<domain>/` (type `visual`, `file` holding the HTML path, `companion` pointing to the related kb note). That note's `companion` points back. The stub body is a short paragraph on what the page shows and what to look for, a line saying "Open `Visuals/<domain>/html/<file>.html` in a browser", and a link to the companion note.

## Self-review before building

It reads with scripts off. It works at 320 px. Dark mode keeps its contrast. It works by keyboard alone. Every number on it traces to a note or a stated source.
