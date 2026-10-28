---
paths:
  - "tools/visuals/**"
---

# HTML build: sources to one offline file

Each page is built from JSX into a single self-contained HTML file. This recipe was verified in a scratch build: one 21.7 KB file, readable with scripts off, interactive with scripts on, no runtime errors, no external references.

## Layout

```
tools/visuals/
  package.json  package-lock.json     (exact versions)
  build.mjs                           (you write it)
  src/shared/                         (components, theme and base CSS, written once)
  src/<domain>/<page>.jsx             (page sources; optional <page>.logic.js for calculators)
  dist/                               (temporary, gitignored)
  test-results.json                   (build and test results per page)
```

The repository `.gitignore` excludes `node_modules/` and `tools/visuals/dist/`. Built files go only to `Visuals/<domain>/html/`.

## Toolchain (the only network use besides official docs)

Install with `npm install --save-exact`, inside `tools/visuals/` only. Tested together: `preact` 11.0.1, `preact-render-to-string` 6.8.1, `esbuild` 0.28.2, `tailwindcss` 4.3.3, `@tailwindcss/cli` 4.3.3, plus `jsdom` as a dev dependency for tests. If you install newer versions, rerun the sample build and tests before relying on them. As a supply-chain precaution, prefer versions published at least two weeks ago (`npm view <package> time`). If Node or npm is missing or the install fails, do **not** fall back to CDN scripts: record it in `DECISIONS.md`, skip Passes B and C, finish the text passes, and say so in `REPORT.md`.

## Build recipe

1. **Client bundle:** esbuild API with `bundle: true`, `jsx: 'automatic'`, `jsxImportSource: 'preact'`, `format: 'iife'`, `minify: true`, `target: 'es2019'`, `write: false`. The entry calls `hydrate(<Page />, document.getElementById('root'))` from `preact`.
2. **Server bundle:** the same JSX options with `platform: 'node'` and `format: 'esm'`, written to `dist/`. Import it and call `render` from `preact-render-to-string` on the same page component to get the static HTML.
3. **CSS:** `npx @tailwindcss/cli -i <input.css> -o <out.css> --minify`. The input has `@import "tailwindcss";`, an `@source` line pointing at the sources, and the smooth-scroll rules: `scroll-behavior: smooth`, switched off inside `@media (prefers-reduced-motion: reduce)`. Tailwind's `dark:` variant compiles to `prefers-color-scheme`.
4. **Assemble:** doctype, `lang="en-GB"`, charset, viewport, title, a `<style>` with the compiled CSS, `<div id="root">` holding the static HTML, and a `<script>` holding the client bundle with every `</script` written as `<\/script`.
5. **Write** the file to `Visuals/<domain>/html/<name>.html`.

## Page contract

A page source exports a default `Page` component. It may also export `meta` (title and companion note name), `tests` (for calculators: known inputs with expected outputs) and `smoke(document)` (one headless interaction).

## Build checks (the build fails if any is false)

- No `http://` or `https://` in any `src`, `href` or `url()`, no `<script src`, and no `fetch`, `XMLHttpRequest` or dynamic `import(`.
- The file is at most 400 KB, with a `<title>`, `lang` and the viewport meta tag.
- The static HTML already contains the `h1` and the `main` text (so it reads with scripts off).
- The page's `tests` pass.
- A jsdom load with scripts on produces no runtime errors, and `smoke` passes.

Write the results to `tools/visuals/test-results.json`.

## Shared components (write once, in Phase 2)

Layout (header, skip link, `main`, footer notice), Toc with scroll-spy, ProgressBar, Section, Callout, Reveal (collapsible answer), QuickCheck (multiple choice with feedback), Slider with readout, StepThrough, SvgFigure with caption, and the theme and base CSS. Pages import them. Never copy component code into a page.

## What headless tests cannot do

They cannot judge visual design. In `TEST-IN-OBSIDIAN.md`, tell the user to open three to five pages (including one lesson) in a browser and look. Also tell them that Obsidian does not render `.html` files itself: use a browser, or a community HTML viewer plugin. Some of those plugins block scripts by default, so interactive parts stay inert there, but all the text remains readable.
