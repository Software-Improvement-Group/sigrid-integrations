---
description: "Always apply during code review for any changes in report-generator."
applyTo: "report-generator/src/**/*.py"
---

## Repository context

This repository generates Sigrid quality reports (pptx/docx) from Sigrid API data. It supports both standard SIG report
layouts and custom user-provided templates, using a placeholder system to map Sigrid metrics into template fields.

## Architecture enforcement

This repository uses a layered architecture (`context → domain → placeholders → rendering`); see `report-generator/docs/architecture.md` for the full explanation. During code review, flag the following logical placement violations:

1. **`context/` interpreting data:** Does new code in `context/` parse, reshape, or apply any semantic meaning to API
   responses? → `context/` returns raw JSON only; interpretation belongs in `domain/`.

2. **`domain/` producing display-ready output:** Does new code in `domain/` return formatted strings, star symbols,
   percentage strings, color names, or any value that only makes sense in the context of a report? → That belongs in
   `placeholders/formatting/`.

3. **`domain/` with report-specific logic:** Does new code in `domain/` contain thresholds, conditions, or computed
   properties that are only meaningful because of how a template displays them? → That belongs in
   `placeholders/implementations/`.

4. **`rendering/` with Sigrid knowledge:** Does new code in `rendering/` reference Sigrid data structures, domain
   objects, or call formatting helpers? → `rendering/` should only contain pptx/docx mechanics; it must not know what
   the values mean.

5. **`utils/` with domain knowledge:** Does new code in `utils/` reference Sigrid API response shapes or depend on what
   Sigrid data looks like? → That belongs in `domain/`; `utils/` must be pure and stateless.

6. **`presets/` using internals:** Does a new or changed preset import from anywhere inside `generator/` other than the
   public `ReportGenerator` API? → Presets are thin wrappers and must not depend on generator internals.

Do not flag import order, unused imports, or dependency direction — those are enforced by a separate CI job.

## Fail early

Flag any code that silently swallows a missing or unexpected state by returning a neutral default (`None`, `0`, `[]`,
`""`) instead of raising an error. Returning a default when data is genuinely absent is fine, but doing so when it
indicates a bug or a broken assumption hides the real problem and pushes failures downstream where they are much harder
to diagnose.

Concrete things to look for during review:

- A lookup that returns `0` or `None` when an entity is not found, where "not found" should never happen in normal
  execution (e.g. a system name that came from the same API response is then looked up in a second call and silently
  defaults to zero).
- A calculation that silently excludes items from aggregations (weighted averages, sums, distributions) because a
  helper returned a falsy default instead of surfacing the error.
- `except Exception: pass` or `except Exception: return default` blocks that discard error information.
- Conditionals that skip processing when a value is `None`/`0` without logging or raising, making it impossible to
  tell from the output whether data was missing or simply zero.

When in doubt: fail loudly at the point where the invariant is violated, not quietly at the point where the result is
consumed.

## Version updating

Every change requires a version bump in `report-generator/setup.cfg` using semantic versioning. Flag the PR if the
version is unchanged.