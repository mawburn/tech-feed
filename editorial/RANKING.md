# Editorial ranking and coverage gates

Apply this after discovery, **not** as a substitute for discovery. The objective is to lead with what matters now, while retaining consequential long-term research, technology, market and employment news.

## First gate: credible, urgent operational impact

Consider all verified breaking incidents before applying ordinary story scores.

- **Critical (usually lead):** active or newly confirmed widespread disruption to critical infrastructure, a major cloud/developer platform, financial transactions, communications, transport or multiple downstream services; large confirmed security emergencies; incidents with material public impact or urgent operator action.
- **High (normally among top stories):** significant but contained failures, major resolved outages with substantial effects or published root-cause findings, widely exploitable security flaws, major fast-moving operational or regulatory events.
- **Standard:** important launches, company transactions, technical research, sustained economic trends, tooling changes and less urgent developments.

Do not label every outage critical. Weigh independent confirmation, affected populations, severity, duration, geography, downstream dependencies and whether the incident is ongoing. If severity or scope is unknown, say so and do not inflate it. Recheck the current incident state before writing.

A verified widespread *active* failure ordinarily outranks a non-urgent strategic acquisition or a speculative model benchmark. An even more consequential simultaneous verified emergency may take precedence; explain the judgment. A restored event may remain the lead when repercussions are still substantial, but do not describe it as ongoing without evidence.

## Second gate: score the full candidate set

For all credible candidates, compare:

1. **Observed impact and urgency:** actual disruption, affected users/operators, security or safety consequences, time-critical action.
2. **Technical consequence:** material change to architecture, performance, safety, reliability, tooling or developer practice.
3. **Breadth and durability:** affected ecosystem and expected lasting effects.
4. **Evidence quality:** primary documentation, reproducibility, independent corroboration, uncertainty and contradictions.
5. **Novelty and relevance:** what is genuinely new today, including previously under-covered research or releases.
6. **Community substance:** useful firsthand HN/Reddit/engineering discussion as supporting context, never a popularity proxy.

A single numerical score is optional; use explicit comparisons. Pure engagement metrics (HN votes, comments, Reddit rank) are **candidate discovery** signals only. Company prestige and dollar values alone do not confer a #1 rank. Corporate announcements, funding and vendor benchmarks require scrutiny.

## Editorial quality checks

Before publishing:

- Inspect current outage/incident coverage again: is a verified major incident missing or buried? Correct ranking or record a defensible reason.
- Compare selected stories with the highest-signal rolling 24-hour HN candidates, plus new/Show HN and other community discoveries. If important candidates were excluded, know why.
- Review cross-category balance without enforcing quotas. Significant security, platform, infrastructure, jobs, business, languages and AI news can all lead.
- Check `data/incidents/` before ranking: a new development on a tracked incident is an update to its record (and a story with the same `incidentId`), not a new incident. See `editorial/INCIDENTS.md`.
- Distinguish *incident occurred*, *reported*, *resolved*, *root cause published* and *investigation continuing* timestamps.
- Avoid repeating an old article as new; a material update needs an explicit change.
- Do not invent community consensus, vendor capabilities, source URLs, dates, cause/effect claims or adoption.
- Keep summaries specific: what happened, what it affects, why it matters, limitations and useful primary/independent links.
- If the evidence is thin, de-rank or omit the claim instead of making it sound established.

For the Sunday review, rank themes by the week's cumulative importance, not Monday's ranking or an average of headline attention. Revisit outages that span multiple days, investigate resolution and root-cause updates, and do not attribute unrelated contemporaneous failures to a shared cause.

## Explain exceptions

When a widely verified operational emergency is covered below an ordinary launch or acquisition, explain the editorial reason in `discoveryAudit.rankingNotes`. If evidence is insufficient or the incident was already resolved, state that fact. Do not make the reason up after the ranking.

## Explicit exclusion: jQuery-specific coverage

Do not select standalone jQuery releases, security/maintenance patches, migration instructions, plugin updates or other routine jQuery stories for the daily or weekly technology feed. This is an explicit reader preference, not a claim about jQuery's usage or maintenance status. Look for more consequential technology news instead; do not artificially pad story counts to replace it. Exception: a genuinely major, independently verified broader cross-ecosystem incident may mention jQuery where indispensable to the incident facts, but do not frame it as a jQuery product story. Apply this filter before final ranking and do not rewrite historic editions as part of routine research.
