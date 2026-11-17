# Discovery sources and verification standards

These are **source categories and starting points**, not an exhaustive daily checklist. Research must be broad enough to catch emerging significant events, including topics outside the usual AI/software headlines. A source URL does not constitute verification unless its relevant content was actually reviewed.

## Hacker News

- Time-filtered Algolia API: https://hn.algolia.com/api
- Official live Top, Best, New and Show HN: https://hacker-news.firebaseio.com/v0/topstories.json , https://hacker-news.firebaseio.com/v0/beststories.json , https://hacker-news.firebaseio.com/v0/newstories.json , https://hacker-news.firebaseio.com/v0/showstories.json
- Direct discussion item: https://news.ycombinator.com/item?id=<id>

Record which interfaces succeeded and how many distinct candidates were *examined*. Lists fetched successfully are not the same as stories read. Filter rolling 24-hour submissions by timestamp.

## Current incidents and service reliability

Search the current news cycle **independently** for widespread outages, banking/payment interruptions, cloud incidents, DNS/CDN failures, SaaS disruptions, telecom failures, airline/transport issues, critical security events and unusual cascading dependencies. Consult relevant vendor/agency status updates and first-party incident posts where available.

Starting points include:
- AWS Health status: https://health.aws.amazon.com/health/status
- Google Cloud status: https://status.cloud.google.com/
- Cloudflare status: https://www.cloudflarestatus.com/
- GitHub status: https://www.githubstatus.com/
- Vendor-specific status/incident pages, regulators and emergency notices, as appropriate.

Official status pages can be delayed or incomplete. Corroborate with reputable independent reporting when practical. User-submitted outage aggregators can identify anomalies but **cannot alone prove outage scope, cause or provider attribution**. Verify whether an incident is active, restored or uncertain at the time of publication.

Look for verified affected systems, timeline, broad impact and confirmed downstream effects. Do not assert shared causes between separate outages without evidence.

## Engineering, security and open source

Research relevant official release notes, changelogs, GitHub releases/issues/advisories, maintainer announcements, technical writeups, CVE/vendor advisories and independent reproducible investigations. Track important new compiler/runtime, database, framework, library, agent/MCP, developer tooling and infrastructure work across languages and platforms.

GitHub Trending and community ranking are discovery prompts; prefer project documentation, code, release history and real-world evidence for claims.

## AI and research

Use first-party model cards, code/weight repositories, peer-reviewed or preprint papers, independent evaluations, hardware and inference benchmarks with disclosed methodologies, and credible reporting. State whether models are proprietary, open-weight or open-source; do not conflate the categories. Treat vendor tests as vendor-reported.

## Community discussions

Review relevant technical Reddit communities, Lobsters, developer forums and direct HN/GitHub discussion threads when they supply useful firsthand details or informed disagreements. Verify the exact thread permalink and topical match. Approved Reddit API access may not be available. If inaccessible, use verifiable public search results or omit the link; never invent a Reddit URL.

`sources` contains evidence for the factual story. `discoveredVia` is its genuine discovery origin. `discussions` is a matching community conversation. One link can serve multiple roles only if those roles are actually true.

## Practical applications and tutorials

Used for the "AI & tooling in practice" section; see `editorial/APPLICATIONS.md` for selection and verification rules.

- YouTube: search recent tutorials, demos and build logs by topic; link the specific video. Independent creators and conference talks are preferred over vendor marketing. Review the video itself, not only the title or description.
- GitHub: new and recently updated example repositories, trending projects, awesome-lists and linked demos. Verify the code, license, commit history and instructions.
- Show HN (`https://hacker-news.firebaseio.com/v0/showstories.json`, or Algolia with `tags=show_hn`): projects with working demos or source.
- Technical blogs, engineering writeups, Lobsters, relevant Reddit communities and developer forums for case studies and workflows.
- Treat aggregators and social posts as leads. The evidence is the underlying video, repository or writeup.

## Jobs, business and policy

Use employer filings/announcements, labor statistics, credible compensation and hiring datasets, regulatory texts, earnings/SEC documents, reputable business reporting and studies with identifiable sampling. Avoid making sweeping market conclusions from anecdotes, surveys without representative methodology, or isolated layoffs.

## Evidence hierarchy and timing

Prefer primary documentation for what was announced, independent investigation for what works, and reputable reporting for external effects. Search published dates **and** underlying event dates. When credible sources conflict, state the disagreement and avoid false precision.

Use time-filtered searches and fresh sources for ongoing incidents; evergreen sources alone cannot establish current status. Never say a source was checked solely because the URL appeared in a search result.
