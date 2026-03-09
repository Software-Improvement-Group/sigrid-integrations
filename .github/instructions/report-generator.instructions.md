---
applyTo: "report-generator/src/**/*.py"
---

## Architecture enforcement

This repository uses a layered architecture (`context → domain → placeholders → rendering`); see `report-generator/docs/architecture.md` for the full explanation. During code review, flag the following logical placement violations:

1. **`domain/` producing display-ready output:** Does new code in `domain/` return formatted strings, star symbols, percentage strings, color names, or any value that only makes sense in the context of a report? → That belongs in `placeholders/formatting/`.

2. **`domain/` with report-specific logic:** Does new code in `domain/` contain thresholds, conditions, or computed properties that are only meaningful because of how a template displays them? → That belongs in `placeholders/implementations/`.

3. **`rendering/` with Sigrid knowledge:** Does new code in `rendering/` reference Sigrid data structures, domain objects, or call formatting helpers? → `rendering/` should only contain pptx/docx mechanics; it must not know what the values mean.

4. **`utils/` with domain knowledge:** Does new code in `utils/` reference Sigrid API response shapes or depend on what Sigrid data looks like? → That belongs in `domain/`; `utils/` must be pure and stateless.

5. **`presets/` using internals:** Does a new or changed preset import from anywhere inside `generator/` other than the public `ReportGenerator` API? → Presets are thin wrappers and must not depend on generator internals.

Do not flag import order, unused imports, or dependency direction — those are enforced by a separate CI job.

## Version updating

A version bump in report-generator/setup.cfg is generally required and should use semantic versioning.