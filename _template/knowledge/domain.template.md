# Domain: <name>

Claude Code fills this file in from the domain's brief and saves it as `.claude/domains/<slug>.md`. Replace every angle-bracket placeholder, delete this paragraph, and keep the finished file under 200 lines.

Domain slug: `<slug>`. Per-domain build files live in `_meta/domains/<slug>/`. Folders: `Knowledge/<slug>/`, `Examples/<slug>/`, `Exercises/<slug>/`, `Scenarios/<slug>/` and `Visuals/<slug>/` (with `html/` inside). Page sources: `tools/visuals/src/<slug>/`.

## Settings

- **Tools or platforms to reference:** <from the brief>
- **Target size for the first build:** <from the brief, or the default: about 40 `kb`, 12 `example`, 20 `exercise`, 10 `scenario` and 8 `visual` pages, plus one `lesson` page per section; a floor, not a ceiling, because the coverage audit adds more>
- **Note `review_cycle`:** <value from the brief; written into every note of this domain>

## Permissions

- **Network use:** <none, or: read-only lookups of official documentation only; record each source in `references` as title, publisher, address and access date>
- **Installs:** <only what the brief lists; the shared HTML toolchain in `tools/visuals/` is already set up (run `npm ci` there if `node_modules` is missing), so a new domain needs no new installs>
- **Accuracy:** <the main risks from the brief, and how to handle them; specific values always go to `NEEDS-VERIFICATION.md`>
- **Standards or sources to name, never quote:** <from the brief>

## Safety and scope

<Delete this section only if the domain has no safety, legal or personal-impact risk. Otherwise state: who the reader is; what the base must never do (for example give a diagnosis, a dose, a legal ruling or a design sign-off); the disclaimer that goes on every start-here and index note; which claims always need a named source and `confidence: low`; and what to tell a reader to take to a qualified professional. The validator and the Check vault run cannot enforce this, so keep it short and concrete.>

## Sections (the values the schema allows, in build order)

Every value starts with `<slug>-`. Include `<slug>-start-here` first and `<slug>-reference` last.

| `section` value | Covers |
| --- | --- |
| `<slug>-start-here` | How to use the base, learning paths, index notes |
| `<slug>-<topic>` | <one line> |
| `<slug>-reference` | Checklists, troubleshooting, glossary, FAQs, reading list |

Learning paths (`track` values, each starting with `<slug>-`, three to six): <list>

## Content plan (propose exact file names, types, levels and kinds in Phase 1)

<One short paragraph per section, listing its topics. Derive them from the brief's topics.>

## Practice content

<How many exercises and scenarios per concept, which `decision_type` values matter most here, how difficulty is spread. Scenarios concentrate in the advanced and senior levels.>

## Suggested visuals

<Visuals that genuinely help in this domain, and any limits. Visuals are self-contained, so equations are drawn as plain text or SVG.>

## Lessons

<One lesson per section, named after the section.>

## Coverage checklist (seeds for the coverage audit)

<Sectors, lifecycle stages, subtypes, disciplines, failure modes, tools and standards a practitioner of this domain would expect to see covered. Claude Code checks the base against this list and adds candidates for gaps.>

## Tags

<Existing preferred terms to reuse, and the few new general terms to add to `tags.yaml`.>
