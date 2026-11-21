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

## Separate axis: landmark significance (`significance`, `thread`)

Rank measures **urgency**: what a reader should act on or know first today. It deliberately puts active incidents and exploited vulnerabilities ahead of strategic news. That leaves a gap: a landmark event can sit at #3–#5, or in *Also worth knowing*, day after day, and a reader skimming the top can miss it entirely. Significance closes that gap. It is judged **independently of rank**, and it does not change the ranking rules above.

Ask: *would a well-informed technology reader be surprised or embarrassed to learn about this a week later?* If yes, set `"significance": "major"` on the story. The site then shows it as the **Big story** banner at the top of the dashboard, badges it in the executive summary and headlines, and keeps it in **This week's big stories** for seven days.

Typical `major` events (verified, not rumoured):

- IPOs, direct listings, acquisitions or mergers of the most prominent technology or AI companies, or any deal that reshapes a market.
- Frontier model or platform launches that change what developers can do, from the major labs and platforms.
- Leadership changes at the top of major technology companies (CEO, founder departures), or collapses and shutdowns of widely used companies or products.
- Landmark regulation, court rulings or government actions that change how technology is built, sold or used.
- Exceptional outages or security events whose scale makes them general news, not only operational news. These usually also lead the ranking.

Use `"significance": "notable"` for important stories that fall short of landmark (badge only). Leave it out for everything else. Expect **zero to two** `major` stories on a normal day. If everything is major, nothing is. Company prestige or a dollar figure alone is not enough. The event must be real, confirmed and consequential.

A `major` story should also appear in `executiveSummary`, usually first or second, even when its rank is lower.

**Developing stories.** When an event unfolds over several days (roadshow → pricing → first trade; announcement → rollout → backlash; lawsuit → ruling → appeal), give every story about it the same `"thread"` ID: lowercase kebab-case, stable for the life of the event, e.g. `"anthropic-ipo-2026"`. Reuse the existing ID on each new day. Before choosing one, check recent editions for a thread already in use. The site links the entries into a dated timeline on each story and shows "Developing since …" on the banner. Mark the decisive milestones `major` (pricing, first trade, closing, ruling), not every incremental update. Outages and security incidents use `incidentId` instead (see `editorial/INCIDENTS.md`).

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
- Ask the landmark question for every story, separately from rank. Set `significance: "major"` where it applies, and continue an existing `thread` ID for developing events.

For the Sunday review, rank themes by the week's cumulative importance, not Monday's ranking or an average of headline attention. Revisit outages that span multiple days, investigate resolution and root-cause updates, and do not attribute unrelated contemporaneous failures to a shared cause.

## Explain exceptions

When a widely verified operational emergency is covered below an ordinary launch or acquisition, explain the editorial reason in `discoveryAudit.rankingNotes`. If evidence is insufficient or the incident was already resolved, state that fact. Do not make the reason up after the ranking.

## Explicit exclusion: jQuery-specific coverage

Do not select standalone jQuery releases, security/maintenance patches, migration instructions, plugin updates or other routine jQuery stories for the daily or weekly technology feed. This is an explicit reader preference, not a claim about jQuery's usage or maintenance status. Look for more consequential technology news instead; do not artificially pad story counts to replace it. Exception: a genuinely major, independently verified broader cross-ecosystem incident may mention jQuery where indispensable to the incident facts, but do not frame it as a jQuery product story. Apply this filter before final ranking and do not rewrite historic editions as part of routine research.
