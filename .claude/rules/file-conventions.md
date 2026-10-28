---
paths:
  - "Knowledge/**"
  - "Examples/**"
  - "Exercises/**"
  - "Scenarios/**"
  - "Visuals/**"
---

# File conventions the Rubric plugin needs

## Where files go

- Each note type has one root folder, because the schema maps a root folder to one type: `kb` to `Knowledge/`, `example` to `Examples/`, `exercise` to `Exercises/`, `scenario` to `Scenarios/`, `visual` to `Visuals/`.
- Inside it, every note sits **directly** in a folder named after its domain, for example `Knowledge/<domain>/Decoupling capacitor placement.md`. The note's `domain` property equals that folder name. Create the folder when you write the first file in it.
- No other sub-folders: not by section, level or topic. Those are properties.
- A visual's stub note sits directly in `Visuals/<domain>/`. Its HTML file sits in `Visuals/<domain>/html/` with a kebab-case name, and the stub's `file` property holds that path. A lesson's file is `<section-slug>-lesson.html` and its stub is named `<Section title> lesson`.
- JSX page sources live in `tools/visuals/src/<domain>/`, outside the note folders. Only built HTML goes in `Visuals/`.
- `Archive/`, `Attachments/` and `Templates/` are reserved and excluded from checking. Do not use them.

## Identity

- **Schema choice:** an explicit valid `type` wins. Every note has one.
- **IDs** are generated and immutable: `PREFIX-YYYY-NNNN`, for example `KB-2026-0001`. The year comes from `created` and never changes. The number counts per type per year, never reused. You write files directly, so **you** generate IDs.
- **Ledger:** `_meta/ids.json` maps prefix to year to the last number used, for example `{"KB": {"2026": 14}}`. The next ID is that number plus one, zero-padded to four digits. Update it in the same batch that uses the numbers. IDs are shared across all domains.
- **`unique_id`** (`TYPE-DOMAIN-YEAR-NNNN`, for example `KB-PC-2026-0046`) sits right after `domain`. It has its own counter per type, domain and year, kept in the same ledger under the key `KB-PC` (`{"KB-PC": {"2026": 253}}`); the domain's two-letter prefix is in `_schema/registry/domains.yaml`. take the next number from that ledger entry and update it in the same batch. It names the note's type and domain, so it is issued again if either ever changes (the old value is then kept in `archived_fields`). Never link by it.
- **`name` equals the file name** (without `.md`). Cross-references use file names, never IDs.
- **Links in frontmatter** are quoted wiki-links: `"[[Decoupling capacitor placement]]"`. In the body use `[[File name]]`. Plain names work because file names are unique across the whole vault.

## Frontmatter shape

- **Property order:** modules in the order the type lists them, then the type's own properties, then `created` and `modified` last. Copy the order of the examples in `note-frontmatter.md`.
- **Defaults:** write every required property, every property with a default and any optional property with a real value. Omit empty optional properties.
- **Do not write `breadcrumb`.** This pack does not use it.
- **Dates:** `created` and `modified` are local time, `YYYY-MM-DDTHH:mm`. Read the system clock when you create a note and set both equal. When you later edit a note, update `modified` only; never change `id`, `created` or `schema`.
- **Controlled values:** `tags` and `track` accept only preferred terms, never synonyms. Add new tags to `tags.yaml` first.
- **Domain values:** `section` and `track` values start with the domain slug and a hyphen.
- **One type per property name** across the vault. Do not invent properties.

## File names

They must work on macOS and Windows: no `/ \ : * ? " < > |`, no trailing dot or space, no reserved names such as CON or NUL. They must be unique across the whole vault, including future domains. Use specific sentence-case titles; avoid generic ones like "Grounding".
