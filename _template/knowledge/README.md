# Adding a knowledge domain

`_template/<kind>/` holds what a new domain starts from. The kind here is `knowledge` (a knowledge base). Each domain you add gets its own folder, `_template/knowledge/<domain>/`, holding its brief and a setup log. The live domain files stay in `.claude/domains/`.

| File | What it is |
| --- | --- |
| `brief.template.md` | The short form you fill in for a new domain |
| `domain.template.md` | The blank domain file Claude Code fills in from your brief |
| `new-domain.md` | The procedure Claude Code follows (you do not need to read it) |
| `<domain>/brief.md` | Your filled-in brief for that domain |
| `<domain>/SETUP-LOG.md` | Written by Claude Code: exactly what it added to the schema and which files it created |

## To add a domain

1. Copy `brief.template.md` to `_template/knowledge/<domain>/brief.md` and fill it in. About ten lines is enough.
2. For the **first** domain nothing else is needed. For later domains, make sure the active domain is finished (its `_meta/domains/<active>/REPORT.md` exists).
3. Open Claude Code in the vault folder and say: "Read CLAUDE.md and begin."

Claude Code sees a brief for a domain that is not in the schema yet, sets the domain up (append-only schema edits, a domain file, a setup log), makes it the active domain, and builds it. It creates the domain's folders under each note type as it writes files. It does not ask you anything. Review `SETUP-LOG.md` afterwards; every schema change is also a git commit you can revert.
