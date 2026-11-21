# Incidents

An incident outlives one briefing: an outage, breach, exploited or newly disclosed vulnerability, supply-chain compromise, or severe regression. It's recorded **once** in `data/incidents/<id>.json` and followed through resolution, permanent fix and postmortem. Stories link it with `incidentId` instead of restating its status.

## When to open one

When it'll likely be covered again or its status will change. Not for a one-day item with nothing left to follow. When unsure, don't. **Check `data/incidents/` first; never open a second record for the same event.** Non-incident developing stories use `thread` (`ranking.md`).

## The record

```json
{
  "id": "example-provider-api-outage-2026-11",
  "title": "Example Provider API outage",
  "provider": "Example Provider",
  "category": "Cloud & Infrastructure",
  "status": "monitoring",
  "discoveredDate": "2026-11-17",
  "occurredDate": "2026-11-16",
  "summary": "The current state, rewritten as facts change.",
  "rootCause": {"status": "suspected", "summary": "…"},
  "sources": [{"label": "Status page", "url": "https://status.example.com/incidents/1"}],
  "history": [
    {"date": "2026-11-17", "kind": "discovery", "status": "investigating", "summary": "…"},
    {"date": "2026-11-18", "kind": "mitigation", "status": "monitoring", "summary": "…", "sources": [{"label": "…", "url": "https://…"}]}
  ]
}
```

- `id`: `<provider>-<what>-<yyyy>-<mm>`, lowercase kebab-case, equal to the file name, **never renamed**.
- `status`: `investigating` (cause or scope unknown), `identified` (known, not fixed), `monitoring` (mitigated, watching), `resolved` (restored or over).
- `resolvedDate`: required when `resolved`, **forbidden otherwise**. If it recurs, change `status` back and remove `resolvedDate`.
- `fix`, `fixDate`: the permanent fix only (patch, architecture or policy change), not a rollback. Unset until it really shipped.
- `rootCause.status`: `unknown`, `suspected` or `confirmed`. `confirmed` only from the affected party or a postmortem.
- `postmortems[]`: `{label, url, publishedDate?, summary?}`.
- Dates: `occurredDate` ≤ `discoveredDate` ≤ `resolvedDate`, `fixDate`.

**History** is append-only and chronological. `kind` is `discovery`, `update`, `mitigation`, `resolution`, `fix`, `postmortem` or `correction`. Fix mistakes with a `correction` entry; never edit old ones. Put `status` on each entry that changes it: **the last entry with a `status` must equal the record's `status`.** Cite sources; label user-reported outage counts as such; unknown stays unknown.

## What to establish

Affected service and a consistent name; severity and blast radius; start time and milestones with time zones; current status and when you checked; suspected vs confirmed cause; mitigation vs durable fix; follow-up safeguards and postmortems, promised vs shipped; what's still broken; direct status, issue and postmortem links. Restored service doesn't mean every user recovered.

When a provider later publishes a root cause or postmortem, add it to the **same** record.

## Linking

- Add `incidentId` to the story or weekly theme, and optionally to the audit's `majorIncidentsConsidered` entry.
- **Commit the incident file before the edition.** An `incidentId` with no valid record gets the whole edition left off the site.
- The story describes that day; the record carries the live status. Follow-ups use `isUpdate: true` and say what changed.
- Never edit past editions to refresh status: update the record. A record can be updated without a story.

## Chat report

**Incidents & fixes** appears in every report: new, ongoing, mitigated, resolved and postmortem updates; records created or updated with their status; what still awaits a fix or postmortem. On a quiet day: "No material verified updates."
