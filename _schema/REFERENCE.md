# Schema reference: technical knowledge base pack

This pack defines the note types for a technical knowledge base (concepts, worked examples, exercises, decision scenarios and HTML visuals). The template ships with a placeholder domain `starter`, replaced by the first real domain; the pack is built so more domains can be added later without changing any existing note. It is written in the same schema language as the pack it was derived from, and reuses four of that pack's modules (`base`, `findability`, `relations`, `review`) unchanged. The second half of this file is the schema-language reference carried over from that pack.

## This pack

### Types

| Type       | Prefix | Folder                | Purpose                                                                                                    |
| ---------- | ------ | --------------------- | ---------------------------------------------------------------------------------------------------------- |
| `kb`       | KB     | `Knowledge/<domain>/` | A written note: concept, how-to, reference, troubleshooting, faq, checklist, glossary, case-study or index |
| `example`  | EG     | `Examples/<domain>/`  | A worked example applying a concept to concrete numbers or a design                                        |
| `exercise` | EX     | `Exercises/<domain>/` | A question with hidden hints and a hidden answer                                                           |
| `scenario` | SC     | `Scenarios/<domain>/` | A real-world situation needing a decision, with a hidden answer and reasoning                              |
| `visual`   | VS     | `Visuals/<domain>/`   | A stub note for an HTML page in `Visuals/<domain>/html/`: an interactive visual or a long-scroll lesson    |

Every type uses the modules `base`, `findability`, `relations`, `review`, `domain`, `curriculum`, `pathways` and `verification`, in that order, then its own properties, then `created` and `modified`. Every type allows the statuses `draft`, `review`, `published`, `outdated` and `archived` (default `draft`). ID prefixes belong to types, not domains, so IDs stay unique across every domain. Each note also has a `unique_id` that adds the domain's prefix and counts per domain.

### Modules added by this pack

| Module | Properties | Meaning |
| --- | --- | --- |
| `domain` | `domain`, `unique_id` | Which knowledge domain a note belongs to, and its readable ID within that domain. `domain`'s values, default and each domain's two-letter prefix come from `registry/domains.yaml` (`values_from: domains`); it is required. `unique_id` is `TYPE-DOMAIN-YEAR-NNNN` (for example `KB-PC-2026-0046`), locked and generated, with its own counter per type, domain and year; a domain with no prefix gets none. Link by `id`, never by `unique_id` |
| `curriculum` | `section`, `level`, `topic`, `order`, `track` | Where a note sits: its subject, level and reading order (it requires the `domain` module). These live here instead of in folders. `section`, `level` and `order` are required. `order` should be unique within a section, in steps of 10 |
| `pathways` | `prerequisites`, `next`, `companion` | Reading sequence and pairing. `companion` links a kb note to its visual and back |
| `verification` | `ai_generated`, `generated_by`, `verified`, `verified_by`, `references`, `standards` | Who wrote the note and whether a person has checked it. `ai_generated` and `verified` default to `false`, so a note written by hand needs no extra work; AI-written notes set `ai_generated: true` explicitly |

### Domains, sections and tracks

The domains are registered in `registry/domains.yaml` (slug, two-letter prefix, description, and the default domain), like types in `registry/types.yaml`. The first domain keeps its sections and tracks in the default lists; every later domain keeps its own in override files (see "Domain overrides" below).

| Domain | Section values | Track values |
| --- | --- | --- |
| `starter` | `starter-start-here`, `starter-reference` | `starter-first-path` |

Rules that keep domains apart (checked by the project validator, because the schema language cannot express them): every note sits directly in `<TypeFolder>/<domain>/` and its `domain` property equals that folder name; every `section` and `track` value starts with its domain slug and a hyphen; a visual's HTML file is under `Visuals/<domain>/html/`; file names of notes are unique across the whole vault.

### Type-specific properties

| Type | Properties |
| --- | --- |
| `kb` | `kind`, `audience`, `confidence` |
| `example` | `demonstrates` (link to a kb note, required), `difficulty` (required), `confidence` |
| `exercise` | `difficulty`, `time_minutes`, `tests` (links to kb notes) all required; `answer_verified`, `confidence` |
| `scenario` | `decision_type`, `difficulty`, `time_minutes`, `tests`, `senior_signal` all required; `answer_verified`, `confidence` (default `low`) |
| `visual` | `kind` (diagram, calculator, comparison, interactive-checklist, flow or lesson), `file` (must match `Visuals/<domain>/html/<kebab-case-name>.html`, required), `formula_source` (required for calculators, by convention), `tested`, `confidence` |

### Vocabularies

| Vocabulary | Used by | Notes |
| --- | --- | --- |
| `tags` | `tags` in `findability` | Strict and normalised, shared by every domain. Add a preferred term to `vocabularies/tags.yaml` before using it, and prefer general terms other domains could reuse |
| `tracks` | `track` in `curriculum` | Strict and normalised. Every term starts with its domain slug |

### Adding a domain later

Changes are append-only, so no existing note needs editing. Claude Code does them itself from a short brief: put `brief.md` in `_template/knowledge/<slug>/` and follow `_template/knowledge/README.md`. The manual equivalent is:

1. Add a line to `registry/domains.yaml`: `<slug>: { prefix: XX, description: ... }`. The prefix is two capital letters, unique among the registered prefixes.
2. Add `modules/curriculum/<slug>.yaml` (a new file): `domain: <slug>`, `sections: [...]` (each starting with the slug and a hyphen) and `override: { section: { default: <slug>-start-here } }`.
3. Add the domain's tracks as a new file `vocabularies/tracks/<slug>.yaml`, and its own tags as `vocabularies/tags/<slug>.yaml`. Preferred terms that other domains could reuse still go in `vocabularies/tags.yaml`.
4. Add a row to the domains table above.
5. Notes for the new domain go in `<TypeFolder>/<slug>/`, one folder per type, created as the first file is written.
6. Never rename or remove a value that notes already use. Renaming means editing every note that uses it.

Keep a type's `version` at 1 for these changes. Raise it only when you want the plugin to offer a migration for existing notes.

### Design notes

- **Domain folders, not section folders.** Each type has one root folder, mapped in `registry/folders.yaml` (a root folder can map to only one type). Inside it, notes sit in a folder named after their domain. Section, level and order are properties, and Obsidian Bases views do the organising. Folder and `domain` must agree; Check vault cannot see this, so the project validator does.
- **HTML pages are built, not hand-written.** JSX (Preact) and Tailwind CSS compile at build time into one offline file per page, with the content pre-rendered so it reads with scripts off. Sources and the build live in `tools/visuals/`.
- **No `breadcrumb`.** The `taxonomy` module is not used, because folders carry no subject information in this pack.
- **Links, not IDs, connect notes.** IDs are generated and immutable, so every cross-reference is a quoted wiki-link to the file name.
- **`scope.yaml` excludes `_meta`, `tools` and `_template`**, which hold build files and templates, not notes.

## Schema language reference (carried over)

What every file and attribute in this folder means. The plugin reads these files, validates them when it loads them (naming the file and line of any problem) and reloads them when they change. If a file is invalid the plugin keeps using the last good copy and shows a warning.

Schema files are plain YAML. Edit them in any editor. The plugin writes only `registry/folders.yaml` and `registry/scope.yaml`, and only when you change a folder mapping or a scope rule in settings or answer the "no schema for this folder" prompt. Comments in those two files are kept.

### Folder layout

| Path                    | Purpose                                                                                                                    |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `registry/types.yaml`   | Format version, minimum plugin version, paths of modules and vocabularies, list of types with ID prefix and schema version |
| `registry/folders.yaml` | Matching mode and root folder → type mapping                                                                               |
| `registry/scope.yaml`   | Which notes are managed                                                                                                    |
| `modules/*.yaml`        | Reusable groups of properties                                                                                              |
| `vocabularies/*.yaml`   | Controlled lists (tags)                                                                                                    |
| `types/*.yaml`          | A note type: the modules it uses plus its own properties                                                                   |

### registry/types.yaml

| Key | Meaning |
| --- | --- |
| `format` | Version of this schema language. Currently `1`. A newer format than the plugin understands is refused (the last good copy stays in use) |
| `min_plugin_version` | Oldest plugin version that understands this pack |
| `modules` | Map of module name → file path (relative to the schema folder) |
| `vocabularies` | Map of vocabulary name → file path |
| `types` | Map of type name → `{ file, prefix, version }`. `prefix` is two capital letters used in IDs. `version` is the number written to `schema` in notes; a note with a lower number is offered a migration |

### registry/folders.yaml

| Key | Meaning |
| --- | --- |
| `mode` | `combined` (type, then breadcrumb, then folder name, then ask), `auto` (same without asking), `manual` (you choose per note or folder) |
| `order` | Documented, fixed: `type, breadcrumb, folder, ask`. Other values are reported and ignored |
| `folders` | Map of root folder name → type name. One type may have several folders. Names are compared ignoring case and accents |

If two types claim the same folder the plugin warns and asks which one owns it; it never picks silently.

### registry/scope.yaml

| Key | Meaning |
| --- | --- |
| `mode` | `exclude` (everything except `exclude`) or `include-only` (only `include`) |
| `exclude` | Folders that are not managed. Exclude always wins. The schema folder is always excluded and not listed |
| `include` | Folders that are managed in `include-only` mode |

An excluded note gets no suggestions, no picker, no validation, no automation and no prompts.

### Modules, vocabularies and types

A module file has `module` (its name), an optional `description`, and `properties`: a map of property name → attributes.

A type file has:

| Key | Meaning |
| --- | --- |
| `type` | The type name |
| `uses` | Module names in order. The note's property order is these modules in order, then the type's own `properties`, then `archived_fields` (if any), then `created` and `modified` |
| `overrides` | Changes to module properties for this type only. Used to give `status` its values and default. May change `values`, `default`, `required` |
| `properties` | The type's own properties |

A vocabulary file has `vocabulary` (its name) and `terms`: a map of preferred term → `{ synonyms: [...] }`.

### Property attributes

| Attribute | Applies to | Meaning |
| --- | --- | --- |
| `type` | all | Value type: `string`, `integer`, `boolean`, `date` (`YYYY-MM-DD`), `datetime` (`YYYY-MM-DDTHH:mm`, local time, no timezone), `url`, `link` (a quoted wiki-link `"[[Note]]"`), `enum`, `list` |
| `items` | `list` | Item type: `string`, `link`, `url` or `term` (a controlled term; needs `vocabulary`) |
| `required` | all | Must be present |
| `default` | all | Value used when a note is created. `today` is allowed for `date`. A property is written at creation when it is `required` or has a `default` |
| `values` | `enum` | Allowed values, in menu order |
| `values_from` | `enum` | `type` = the values come from the type's `overrides` (used by `status`); `registry` = the values are the type names (used by `type`) |
| `min`, `max` | `integer` | Limits |
| `pattern` | `string` | A regular expression the value must match |
| `vocabulary` | `list` of `term` | Name of the controlled list |
| `strict` | controlled | Unknown terms are flagged |
| `normalise` | controlled | Synonyms are replaced by the preferred term |
| `locked` | all | Never opens a picker in the Properties area; a short note says who manages it |
| `immutable` | all | Never changes after it is first written; changes are reported by the vault check |
| `generated` | all | The plugin fills it in |
| `managed_by: external` | all | Another plugin writes it (for example `breadcrumb`); this plugin only reads and checks it |
| `position: end` | all | Always sorts after every other property |
| `allow_heading` | `link` | The link may include a heading: `"[[Note#Heading]]"` |
| `target` | `link`, list of `link` | Link suggestions are limited to notes of this type |
| `description` | all | Free text for people reading the file |

A property name must have the same value type (and item type) in every type, because Obsidian keeps one type per property name across the vault. Enum value lists may differ between types.

### Built-in property

`archived_fields` is built in, locked and generated. When a note is converted to another type, values that no longer apply are never deleted: they are kept in `archived_fields` as entries with the old type, the date and the values.

### Limits worth knowing

- Locks are advisory. Nothing stops another tool changing a locked property; the vault check reports it.
- Comments inside a note's frontmatter may be lost when the plugin rewrites it. Put explanations here, in the schema files.
- `created` and `modified` use local time with no timezone, so the hour when clocks go back is ambiguous.

## Domain overrides (applied 2026-10-25, proposal P-001)

Next to a default file, an optional folder of the same name holds one override file per domain, named by the domain: `types/kb.yaml` plus `types/kb/maths.yaml`, `modules/verification/maths.yaml`, `vocabularies/tags/maths.yaml`. A note's effective schema is the default plus the override file for its `domain`; no file means the default applies (so the first domain, which has none, is unchanged). The file starts with `domain: <slug>` and the file name must be that slug, a domain registered in `registry/domains.yaml`.

| Verb       | Meaning                                                                                                                                                                              |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `override` | Change `values`, `default` or `description` of an existing property. `values` replaces the list and only applies to an enum. The `type` cannot change                                |
| `add`      | Properties allowed only for this domain (full property definitions)                                                                                                                  |
| `remove`   | Properties not allowed for this domain. The core properties `type`, `schema`, `id`, `name`, `status`, `domain`, `section`, `level`, `order`, `created`, `modified` cannot be removed |
| `sections` | Module files only (`modules/curriculum/<domain>.yaml`): extra `section` values for the domain, added to the default list                                                             |

Vocabulary override files are `domain:` plus `terms:`. A term or synonym that equals a default term or synonym is an error and the default wins. Every `section` value and every `track` term for a domain starts with `<domain>-`. A module file may only name properties of that module and applies to every type that uses it; module files apply before the type file.

`tools/validate.py --domain <slug>` prints a domain's overrides and the effective properties per type. The only domain in force in the empty template is `starter` (the default shape, no files).
