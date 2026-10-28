# Knowledge base template

An empty, domain-neutral Obsidian vault for building a structured knowledge base with Claude Code. It was derived from the PCB vault ("Second Brain The Knowledge"): same schema, rules, validator, Bases views and HTML toolchain, with every PCB-specific item removed.

## What is here

| Path | What it is |
| --- | --- |
| `CLAUDE.md` | Universal rules and the build workflow. Says "no active domain" until a brief is processed |
| `.claude/rules/` | How-to files Claude reads before each kind of work (frontmatter, style, bodies, HTML, Bases, validator) |
| `.claude/domains/` | One file per domain. Only a placeholder (`starter.md`) until the first brief is processed |
| `_schema/` | The Rubric schema pack: five note types (kb, example, exercise, scenario, visual), modules, vocabularies, domain registry |
| `_bases/` | Eleven Obsidian Bases views (they filter on the placeholder domain until the first domain replaces it) |
| `_template/knowledge/` | Brief form, domain-file template, and `new-domain.md` (the procedure Claude follows) |
| `_meta/` | Id ledger, decisions, schema proposals; per-domain build files appear in `_meta/domains/<slug>/` |
| `tools/validate.py` | The real gate: validates schema and notes. Run `python3 tools/validate.py` |
| `tools/visuals/` | Offline HTML build (Preact + Tailwind + esbuild). Run `npm ci` there before the first build |
| `.obsidian/` | Core plugin set, theme and 13 community plugins, including `rubric` (the schema plugin) |

## Start a domain

1. Copy `_template/knowledge/brief.template.md` to `_template/knowledge/<slug>/brief.md` and fill it in (about ten lines).
2. Open Claude Code in this folder and say: `Read CLAUDE.md and begin.`
3. Claude replaces the `starter` placeholder with your domain, writes the domain file, and builds in autonomous mode. Review `_template/knowledge/<slug>/SETUP-LOG.md` afterwards.

## Not included (on purpose)

`tools/mknote.py`, `mkstub.py`, `batch.sh` and `migrate_unique_id.py` from the PCB vault hard-code that domain's sections and tracks. Claude writes notes directly and allocates ids from `_meta/ids.json`; ask for a generic `mknote.py` once the first domain's sections exist.

## Checks after copying

- Open the folder as a vault in Obsidian, trust the community plugins, and run **Check vault** (Rubric). Expect no errors.
- `python3 tools/validate.py` should report `0 errors`.
