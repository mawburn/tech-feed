# Incident tracking

Read this file **after** the breaking-incident sweep in `editorial/DISCOVERY.md` and **before** drafting. An incident is a real-world event that outlives one briefing: an outage, a breach or intrusion, an exploited or newly disclosed vulnerability, a supply-chain compromise. We record it **once** in `data/incidents/<id>.json` and follow it from discovery through resolution, permanent fix and postmortem. Daily stories and weekly themes point at that record instead of restating its status.

Schema: `schemas/incident.v1.schema.json`. Validation also checks the rules below that a schema cannot express.

## When to open an incident record

Open one when an event is likely to be covered more than once, or when its status will change (investigating → resolved, patch shipped, postmortem published). Do **not** open one for a single-day news item with nothing left to follow (a product launch, a funding round, a one-hour outage that is already resolved and has no stated cause to wait for). When unsure, do not open one; a story without `incidentId` is always valid.

Before opening a record, check `data/incidents/` for an existing one. **Never create a second record for the same event.** If a new report concerns the same incident, update the existing record and link the new story to it.

## The record

| Field | Rule |
| --- | --- |
| `id` | Stable, lowercase kebab-case, also the file name (`<id>.json`). Pattern: `<provider>-<what>-<yyyy>-<mm>`, for example `apple-icloud-apple-pay-outage-2026-11`. Assign once; **never rename** (stories and URLs depend on it). |
| `title`, `provider` | Plain description and the affected provider, vendor or project. |
| `status` | `investigating` (scope or cause unknown), `identified` (cause or scope known, no fix yet), `monitoring` (mitigated or patched, watching recovery or uptake), `resolved` (service restored or threat ended; **requires `resolvedDate`**). |
| `discoveredDate` | Pacific date the incident was first reported. |
| `occurredDate` | Optional. When it actually began (or the flaw was introduced) if known and different from discovery. Never after `discoveredDate`. |
| `resolvedDate` | Set only while `status` is `resolved`. If an incident recurs, set `status` back and **remove** `resolvedDate` (and record why in `history`). |
| `fixDate`, `fix` | The **permanent** fix: a patch, architectural change or policy change. Distinct from a rollback or workaround, and may be later than `resolvedDate`. Leave unset until a fix really shipped. |
| `rootCause` | `{status, summary, sources?}` where `status` is `unknown`, `suspected` or `confirmed`. Use `confirmed` only when the affected party or a postmortem says so. Researcher or press inference is `suspected`. |
| `postmortems[]` | `{label, url, publishedDate?, summary?}`. Add when an official or credible independent postmortem is published. |
| `sources[]` | Best primary and secondary sources for the incident as a whole. |
| `summary` | The **current** state in one paragraph. Rewrite it as facts change. |
| `history[]` | Chronological, **append-only**, oldest first. See below. |

## History

Each entry is `{date, kind?, status?, summary, sources?}` and records what became known on that date. Rules:

- Append; do not edit or delete earlier entries. Fix an error with a new entry of `kind: "correction"`.
- Dates must not go backwards. Same-day entries are ordered by position.
- Put `status` on every entry that changes it. The **last** entry that sets a status must equal the record's `status` (validation enforces this).
- `kind` is one of `discovery`, `update`, `mitigation`, `resolution`, `fix`, `postmortem`, `correction`.
- Report only what a cited source supports. Keep user-submitted outage counts (for example Downdetector) labelled as user reports, not customer totals.
- Do not invent times, causes, counts or links. Unknown stays unknown, and the page says so.

## Linking reports

Add `"incidentId": "<id>"` to the daily story or weekly theme that covers the incident, and optionally to a `discoveryAudit.majorIncidentsConsidered[]` entry. The id must match an existing, valid record, or validation fails.

- The story still carries its own `summary`, `sources` and `briefing`, written as of that day. The incident record carries the live status, so a story about a "monitoring" outage keeps linking to the page that will later say "resolved".
- Follow-up stories set `isUpdate: true` and point at the same incident. Do not restate the whole history; summarise what changed.
- Do **not** edit published historical daily or weekly files to refresh status. Update the incident record. Add `incidentId` to an older report only when it is the first mention of an incident you are now tracking.
- A weekly theme that spans an incident links to it the same way, and its summary should explain the week's arc rather than copy the timeline.

## Updating an existing incident

1. Update the record in `data/incidents/`: append `history`, rewrite `summary`, change `status`, set `resolvedDate` / `fixDate` / `fix` / `rootCause` / `postmortems` as they become true.
2. If today's briefing covers the development, add or update a story with the same `incidentId`.
3. Run `pnpm validate`. Quote any validation message in your run notes rather than working around it.

During the daily sweep, re-check **open** incidents (anything not `resolved`, and resolved incidents still awaiting a root cause, fix or postmortem) for new developments, even when no new story is written.
