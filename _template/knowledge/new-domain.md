# Procedure: set up a new knowledge domain (for Claude Code)

Run this when `CLAUDE.md` tells you to. Never ask the user anything: if the brief is vague or invalid, choose the most conservative option and record it in `_meta/DECISIONS.md`.

## First domain (empty template)

The template ships with a placeholder domain `starter` and no notes. If `_meta/ids.json` holds no ids, there are no files under `Knowledge/`, `Examples/`, `Exercises/`, `Scenarios/` or `Visuals/` other than placeholders, and a brief exists for a slug other than `starter`, the brief is the **first domain**. Follow the steps below with these differences, which are allowed once because nothing depends on the placeholder yet:

- Step 4 may **replace** the `starter` line in `registry/domains.yaml`, the `starter-*` sections in `modules/curriculum.yaml`, the `starter-first-path` term in `vocabularies/tracks.yaml` and the starter tags in `vocabularies/tags.yaml` with the new domain's own values, in the default files (no override files for the first domain), and set `default:` to the new slug. Keep the starter tags that fit; add the domain's own.
- Delete `.claude/domains/starter.md`; replace `starter` with the new slug in `_bases/*.base` (`domain == ...` and the learning-path track), in `tools/visuals/domain.json`, and in the illustrations in `.claude/rules/note-frontmatter.md` and `.claude/rules/lesson-pages.md`.
- Step 6 sets the active domain in `CLAUDE.md` (replace the "no active domain" text) and removes the "First domain" trigger line there.
- Record all of this in `SETUP-LOG.md`. From the second domain on, every change is append-only.

## Trigger (second and later domains)

At session start, if both are true:

- a file `_template/knowledge/<slug>/brief.md` exists for a slug that is **not** yet in `_schema/registry/domains.yaml`, and
- the active domain is finished (`_meta/domains/<active>/REPORT.md` exists),

then follow this procedure. If the active domain is not finished, ignore the brief and say nothing; it will be picked up later. If several briefs qualify, take them in alphabetical order, one per run.

## Steps

1. **Read** the brief and `_template/knowledge/domain.template.md`. Check the slug matches `^[a-z][a-z0-9]{1,11}$` and is not already used. If it is not valid, derive the nearest valid slug and record the change. Choose a two-capital-letter prefix for it (for example `MA` for `maths`) that no registered domain uses; if the obvious one is taken, pick another and record it.
2. **Commit** the current state (`Before adding domain <slug>`), so every change below can be reverted.
3. **Derive from the brief:** 8 to 12 sections (`<slug>-start-here` first, `<slug>-reference` last, the rest from the brief's topics in learning order, values `<slug>-kebab-case`); 3 to 6 tracks (`<slug>-kebab-case`); a content plan; a practice plan; a visuals list; one lesson per section; a coverage checklist; and the tag terms. Reuse existing preferred tags wherever they fit.
4. **Edit the schema, append-only.** These are the only schema edits allowed, and nothing else may change:
   - `_schema/registry/domains.yaml`: add one line, `<slug>: { prefix: XX, description: ... }`, at the end of `domains`. The prefix is required here because every note gets a `unique_id` (`KB-XX-2026-0001`); numbering for the new domain starts at 0001. Change nothing else in the file.
   - **New file** `_schema/modules/curriculum/<slug>.yaml`: `domain: <slug>`, `sections: [...]` (the new sections) and `override: { section: { default: <slug>-start-here } }`. The default `curriculum.yaml` is not edited.
   - **New file** `_schema/vocabularies/tracks/<slug>.yaml`: `domain: <slug>` and `terms:` with the new track terms (each starts with `<slug>-`).
   - **New file** `_schema/vocabularies/tags/<slug>.yaml` for tags only this domain uses, and/or add only new preferred terms to `_schema/vocabularies/tags.yaml`, never a synonym that already exists as a term anywhere.
   - Add override files for `types/<type>/<slug>.yaml` or `modules/<module>/<slug>.yaml` only for what truly differs (kinds, extra fields); see `_schema/REFERENCE.md`, "Domain overrides".
   - `_schema/REFERENCE.md`: add one row to the domains table with the new sections and tracks.
   Do not change a type's `version`, any property type, any other file in `_schema/`, or any existing value.
5. **Write the domain file** `.claude/domains/<slug>.md` from `domain.template.md`, fully filled in from the brief (network and installs exactly as the brief states; defaults otherwise). No placeholders may remain.
6. **Switch the active domain** by editing only the "Active domain" section of `CLAUDE.md`: the domain slug sentence and the import line, so they name the new domain file.
7. **Create** `_meta/domains/<slug>/NEEDS-VERIFICATION.md` (empty list). The five domain folders (`Knowledge/<slug>/`, `Examples/<slug>/`, `Exercises/<slug>/`, `Scenarios/<slug>/`, `Visuals/<slug>/html/`) are created when you write the first file in each, because git does not track empty folders. Page sources go in `tools/visuals/src/<slug>/`; the shared toolchain and components already exist.
8. **Write** `_template/knowledge/<slug>/SETUP-LOG.md`: every value appended (file and value), every file created or edited, and every decision made.
9. **Run `tools/validate.py`.** It must pass, including its schema checks (append-only against the previous commit, prefixes, domain file present, no placeholders left). Fix anything it reports. After three failed attempts, revert to the commit from step 2 and follow the stop rules in `CLAUDE.md`.
10. **Commit** (`Add domain <slug>`), then start Phase 0 for the new domain in autonomous mode. The baseline commit already exists, so skip that part of Phase 0.
