# Examples

Complete, valid files for the agent to copy the shape of. `tests/validate.test.mjs` checks both against the schemas, so they stay correct when the contract changes.

- `daily.json`: stories copied from the published 2026-11-18 edition (cut to one or two per section), with GitHub Actions' image fields removed and an `executiveSummary` added. It shows `incidentId`, `significance` and `thread` in use.
- `weekly.json`: structure only. The text describes what goes in each field and the URLs are placeholders.

Never copy example values into a real edition.
