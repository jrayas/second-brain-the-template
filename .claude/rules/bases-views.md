---
paths:
  - "_bases/**"
---

# Bases views

**Do not guess the `.base` file syntax.** Check the current Obsidian Bases documentation (help.obsidian.md, the Bases section) and follow it exactly. If you cannot access it, write the views as a plain-language spec in `_bases/README.md` and tell the user, rather than guessing.

Every view filters on `domain` (default: the active domain), so views keep working when more domains are added. Views live in `_bases/`; a view meant for one domain only goes in `_bases/<domain>/`. Create:

1. **Learning path:** filter by a chosen `track`, sorted by `order`, grouped by `level`.
2. **By section:** grouped by `section`, sorted by `order`, columns `level`, `type`, `status`.
3. **By level:** grouped by `level`, filterable by `type`.
4. **Exercises:** `type: exercise`, grouped by `level`, columns `difficulty`, `time_minutes`, `tests`.
5. **Scenarios:** `type: scenario`, grouped by `decision_type`, columns `difficulty`, `time_minutes`.
6. **Review queue:** `verified: false`, sorted by `confidence` (lowest first), then `section`.
7. **Answers to verify:** exercises and scenarios with `answer_verified: false`.
8. **Visuals:** `type: visual`, columns `kind`, `tested`, `formula_source`.
9. **Gaps: concept notes without a visual:** `type: kb`, `companion` empty.
10. **Due for review:** sorted by `review_next`.
11. **Lessons:** `type: visual`, `kind: lesson`, sorted by `section`, columns `section`, `tested`, `status`.
