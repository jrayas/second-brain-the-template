---
paths:
  - "tools/**"
---

# Validator specification (`tools/validate.py`)

Standard library plus PyYAML if needed (tell the user before installing anything). It reads every rule from `_schema/` instead of hard-coding it, so it keeps working when a domain is added. Output is terse: one line per problem plus a summary. The exit code is non-zero if any error exists.

## The schema pack

- Every file parses; every module, type and vocabulary in the registry exists; type and vocabulary names match their files.
- Prefixes are two capital letters and unique.
- No property name has a different value type or item type in two places.
- Every `target` is a real type; every `term` list names a real vocabulary.
- Vocabulary synonyms do not collide with terms or with each other.
- A type's `kind` values only grow. Every folder maps to a real type; overrides change only `values`, `default` or `required`; every type's `status` has `values` and a `default`.
- **Append-only:** compared with the last commit, nothing a type exposes has been removed or changed: every property still exists with the same type, default, `required` and other constraints, every enum value (`domain`, `section`, `kind`, `status`...) and every tracks and tags term and synonym is still present, and no type prefix or version has changed. Compare what each type exposes (its resolved properties), not file by file, so a property may move between modules; vocabulary, folder and scope files and override files are compared file by file. A `description` is documentation and may change. Parse both versions; do not use a line diff, because value lists sit on one line.
- Every domain (in `registry/domains.yaml`) has a file `.claude/domains/<slug>.md`, every `section` value starts with a registered domain slug and a hyphen, and every track term does too.
- No domain file contains an unfilled placeholder (an angle-bracket placeholder such as `<slug>`).

## The domain registry, `requires` and domain overrides

- `registry/domains.yaml` (optional; without it the domains are the `domain` property's own values): `domains` is a map of slug to `{ prefix, folder, description }`; a slug is lowercase letters, digits and single hyphens; a prefix is two capital letters and unique; a folder is one name, unique ignoring case and accents; `default` is a listed domain. A property with `values_from: domains` takes its values and default from it.
- A module may list `requires`; every type that uses the module lists the required modules too. A module file with no properties is an error. A type that uses a module that is not in the registry is an error, not a crash.
- Override files (`types/<type>/<slug>.yaml`, `modules/<module>/<slug>.yaml`, `vocabularies/<name>/<slug>.yaml`): the slug is a registered domain and the file says `domain: <slug>`; only `override` (`values`, `default`, `description`), `add`, `remove` and, in a module file, `sections`; a property under one verb only; `remove` never names a core property (`type`, `schema`, `id`, `name`, `status`, `domain`, `section`, `level`, `order`, `created`, `modified`); `override` cannot change a `type`; an added property has a type (a list has `items`, an enum has `values`) and must not already exist; a default is valid for its property (checked after the file's `sections` are added); vocabulary override terms and synonyms must not equal a default term or synonym; `section` and `track` values start with `<slug>-`.
- A note is checked against its domain's effective schema (default plus that domain's override files): values, required properties, order, and a property the domain removed must not be present.
- `tools/validate.py --domain <slug>` prints a domain's overrides and the effective properties per type; `--root DIR` validates another vault; `--warnings` lists tags used on only one or two notes.

## Every `.md` note in `Knowledge/`, `Examples/`, `Exercises/`, `Scenarios/` and `Visuals/`

- Frontmatter parses; the root folder maps to the note's `type`; `schema` equals the type's version.
- `id` matches `PREFIX-YYYY-NNNN`, uses the type's prefix, has a year equal to `created`, is unique and matches `_meta/ids.json`.
- `unique_id` (when the type has the property and the domain has a prefix in `registry/domains.yaml`): present; matches `TYPE-DOMAIN-YEAR-NNNN`; its first part is the type's prefix and its second the domain's prefix; unique across the vault; its number does not exceed the ledger entry `_meta/ids.json[TYPE-DOMAIN][YEAR]`. A `unique_id` in a domain with no prefix is an error.
- `name` equals the file name; the file name is valid on macOS and Windows; names are unique across the whole vault.
- Required properties present; no properties outside the type's schema; property order matches the schema, with `created` and `modified` last.
- Every value matches its type: enums, integers with `min` and `max`, booleans, `date`, `datetime`, patterns, quoted wiki-links with the right `target` type, lists with the right item type.
- `created` is not later than `modified`; no `breadcrumb` property.
- `tags` and `track` use only preferred terms (no synonyms, no unknown terms).
- Every `[[wikilink]]` in frontmatter and body resolves to an existing note.
- `description` is at most 160 characters.
- `order` is unique within each `section`.
- **Folder and domain rules:** the note sits directly in `<TypeFolder>/<domain>/` (the second path segment equals `domain`; a note in the root folder or in a deeper sub-folder is an error); `section` and every `track` value start with the note's `domain` and a hyphen; a visual stub sits directly in `Visuals/<domain>/` and its `file` is under `Visuals/<domain>/html/`.
- `companion` links are reciprocal; every visual stub's `file` exists and every HTML file has a stub.
- Each section of a domain has exactly one `kind: lesson` stub once Pass C is complete (a report until then). The lesson's `companion` and `parent` are that section's `kind: index` note, and the index note's `companion` is the lesson.
- `exercise` and `scenario` notes contain collapsed answer callouts (a line beginning `> [!...]-`); `scenario` notes contain the four callouts from the template and a non-empty `senior_signal`.
- No note has `status: published`, `verified: true` or `answer_verified: true`; `ai_generated` is `true` on every note; no visual has `tested: true` without a passing entry for its page in `tools/visuals/test-results.json`.
- Calculators have a `formula_source`.
- Math: `$$` fences are balanced, inline `$` pairs are balanced outside code blocks, and no `$` or LaTeX appears in frontmatter values or headings.

## HTML files in `Visuals/<domain>/html/`

- No external requests: no `http://` or `https://` in `src`, `href` or `url()`, no `<script src`, and no `fetch`, `XMLHttpRequest` or dynamic `import(`.
- At most 400 KB; a `<title>`, `lang="en-GB"`, the viewport meta tag and the educational-aid notice.
- The static HTML already contains the `h1` and the `main` text, and the CSS contains `scroll-behavior` and `prefers-reduced-motion`.
- Every HTML file has a JSX source in `tools/visuals/src/<domain>/`.

## Reports (not errors)

Orphan notes (no incoming links); `kb` notes under 250 words; concept notes with no exercise or scenario; concept notes with no companion visual; sections with no lesson; candidates still open in `CANDIDATES.md`.
