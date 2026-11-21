# Ranking, significance and threads

Two separate judgements for every story:

- **Rank:** what to know or act on first today. The order of `topStories` is the rank; `rank` numbers match it.
- **Significance:** how big it is, regardless of rank. `major` stories get the Big story banner automatically.

A landmark doesn't need #1 to be seen first, and an urgent incident doesn't need to be a landmark to lead.

## Rank

**Incidents first.** Critical (usually leads): active or newly confirmed widespread disruption to critical infrastructure, a major platform, payments, communications or transport; large confirmed security emergencies. High (normally a top story): contained but significant failures, major resolved outages with real effects or a published root cause, widely exploitable flaws. Don't inflate: weigh confirmation, population, severity, duration and whether it's ongoing.

**Then compare all candidates on:** consequence (disruption, security, money, jobs, urgent action); technical significance and novelty; breadth and durability; evidence quality; practical relevance (extra weight for AI and software engineering, but the whole industry counts); and substantive community discussion. Points, prestige and dollar figures alone never earn rank. Vendor benchmarks and funding need scrutiny. A deep engineering investigation can beat a routine model launch.

**Sizes:** about 5–8 top stories and 5–10 also worth knowing; AI & tooling in practice has no fixed number. Fewer on quiet days; never pad.

## Significance

For every story ask: *would a well-informed technology reader be embarrassed to learn about this a week later?* If yes, `"significance": "major"`. Typical: IPOs and major acquisitions of prominent technology or AI companies; frontier model or platform launches that change what developers can do; leadership changes at the top of major companies; collapses or shutdowns of widely used products; landmark rulings, regulation or government action; outages big enough to be general news.

`"notable"` for important stories short of landmark; otherwise leave it out. Expect zero to two `major` stories a day.

A `major` story always goes in `topStories` (any position) and first or second in `executiveSummary`.

## Threads

Events that unfold over days (roadshow → pricing → first trade; resignation → successor; lawsuit → ruling) share a `thread` ID: lowercase kebab-case, e.g. `anthropic-ipo-2026`.

- **Open it on day one** if later milestones are likely, even when that day's story is only `notable`.
- **Reuse the ID**: check recent editions first.
- **Check open threads every run.** When something material happened, publish a short update (`isUpdate: true`, same `thread`) saying what changed. When nothing did, publish nothing.
- Mark decisive milestones `major`, not every update.
- Outages and security incidents use `incidentId` instead (`incidents.md`).

## Before publishing

- Is a verified major incident missing or buried? Fix it or explain in `rankingNotes`.
- Is a strong HN or community candidate missing? Know why.
- Did every story get the landmark question? Is every `major` story first or second in `executiveSummary`?
- Does any story continue a thread or incident without `thread`/`incidentId` and `isUpdate`?
- Is anything a repeat with no material change? Drop it. Nothing appears in two sections.
- Thin evidence: de-rank or omit.

If an operational emergency ranks below an ordinary launch or deal, say why in `rankingNotes`.

## Weekly

Rank themes by cumulative verified consequence, not daily positions or votes. Every thread with a decisive milestone that week gets a theme or a reason in `rankingNotes`.

## jQuery exclusion

No routine jQuery stories (releases, patches, migration guides, plugins, ordinary advisories) in any section, daily or weekly. It's a reader preference. A genuinely major cross-ecosystem incident may mention jQuery where the facts require; cover the incident, not jQuery.
