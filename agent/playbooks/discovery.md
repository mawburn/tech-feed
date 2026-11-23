# Discovery

How to find candidates. Where to look is in `sources.md`.

## Window

Pacific time. **Daily:** the rolling previous 24 hours, plus major missed or materially updated events from the previous 72. **Weekly:** Monday–Sunday ending today. Record the actual research time with its offset.

## 1. Incidents first

1. Re-check every open record in `data/incidents/`: anything not `resolved`, plus resolved ones still awaiting a root cause, fix or postmortem.
2. Sweep for new incidents across cloud, DNS/CDN, developer platforms, CI and package registries, identity, databases, SaaS, AI providers, payments and banking, telecoms, transport and consequential open-source defects. Start broad (`major outage today`, `service disruption today`), then narrow. Check status pages and first-party statements, and corroborate.
3. For each serious candidate establish: first-known time, active vs restored vs uncertain, verified impact, downstream effects, and what's unknown. Don't link separate outages without evidence.

Re-check them again just before locking the lead.

## 2. Hacker News, before choosing stories

Read the front page (two pages), Best, Show and New, skipping items older than the window. Try the Algolia API once. Screen roughly 40–60 distinct candidates, keeping room for low-engagement technical finds; open the originals and discussions for anything material. Points are a lead, never proof of importance.

## 3. Everything else

- Reddit, GitHub (releases, advisories, issues), Lobsters, changelogs, model and research repositories, credible journalism in any language.
- Today's engineering-blog rotation (`sources.md`).
- Security, operations, labour-market and business sources searched separately, so AI news doesn't crowd them out.
- A separate hands-on pass for AI & tooling in practice (`in-practice.md`).

## 4. Shortlist

Deduplicate by underlying event. For each candidate note: event time, where found, sources, confidence, impact, and whether it updates earlier coverage or continues a `thread` or incident. Consider about 10–20 strong candidates, then rank with `ranking.md`. No quotas of any kind.

## 5. `discoveryAudit`

```json
{
  "checkedAt": "2026-11-21T16:40:00-08:00",
  "windowStart": "2026-11-20T16:40:00-08:00",
  "windowEnd": "2026-11-21T16:40:00-08:00",
  "sources": [
    {"name": "HN front page, Best, Show and New", "status": "partial", "candidateCount": 52, "notes": "52 titles screened, 9 opened"},
    {"name": "HN Algolia 24h", "status": "unavailable", "notes": "Request failed"}
  ],
  "majorIncidentsConsidered": [
    {"title": "…", "decision": "top-story", "reason": "…", "sourceUrl": "https://…", "incidentId": "…"}
  ],
  "rankingNotes": "Why the lead leads, what was left out and why, significance and thread decisions."
}
```

Values are illustrative. Rules:

- Name only sources you actually consulted or attempted. `status` is `checked`, `partial` or `unavailable`.
- `candidateCount` is what you really screened; omit it when unknown. Titles seen on a list are "screened", not "examined".
- `majorIncidentsConsidered` lists real, corroborated incidents, including ones you left out (`decision`: `top-story`, `also-worth` or `excluded`); use `[]` when there were none. Entries carry no incident state: link the record with `incidentId` and leave status to the record (`incidents.md`).
