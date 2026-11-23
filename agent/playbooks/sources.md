# Sources

Where to look, and how much to trust each kind of source. A URL is not verified until you've read the relevant content.

## Hacker News

Front page (pages 1–2), [Best](https://news.ycombinator.com/best), [Show](https://news.ycombinator.com/show), [New](https://news.ycombinator.com/newest); threads at `https://news.ycombinator.com/item?id=<id>`. The [Algolia API](https://hn.algolia.com/api) has the true 24-hour window but is usually unreachable for you: try once, then record it `unavailable`.

## Incidents and status pages

[AWS Health](https://health.aws.amazon.com/health/status), [Google Cloud](https://status.cloud.google.com/), [Cloudflare](https://www.cloudflarestatus.com/), [GitHub](https://www.githubstatus.com/), plus the affected vendor's own status page, regulators and emergency notices. Status pages can be late or incomplete; corroborate with reputable reporting. Outage aggregators show anomalies but never prove scope, cause or provider.

## Markets

Check every run, whatever the weekday: where the major US indexes closed (S&P 500, Nasdaq Composite, Dow), the biggest movers among AI, chip and cloud names, and any weekly or record totals. Start with [CNBC markets](https://www.cnbc.com/markets/) and live blogs, [Reuters markets](https://www.reuters.com/markets/) and Yahoo Finance live coverage. Get closing figures from a report written after the close; intraday figures are not closes. Prefer two outlets for index levels and say when they differ. Many news sites refuse automated fetches or time out (CNN, The Hill and NPR have): try another outlet rather than relying on a snippet. Causes come from named analysts, company filings or reporters, never from your own inference; an event that coincided with a move is not its cause.

## Engineering blogs: the daily rotation

Each day, open the one catalog file for today's Pacific weekday in `agent/catalog/` (`monday-cloud.md` … `sunday-maker-venues.md`) and check a few of its blogs for new posts. Also check the engineering blog, incident history and issue tracker of any provider behind a tracked incident, listed or not. The weekly review reads all seven files.

Prefer implementation detail, measurements, failures and trade-offs over product announcements dressed up as engineering posts. An older post can provide background but is never a fresh headline.

## Other sources

- **Engineering, security, open source:** release notes, changelogs, GitHub releases, issues and advisories, CVE and vendor advisories, maintainer posts. Trending lists are prompts; check the code, docs and release history.
- **AI and research:** model cards, weights and code repositories, papers, independent evaluations with disclosed methods. Say whether a model is proprietary, open-weight or open-source. Vendor benchmarks are vendor-reported.
- **Community:** Reddit, Lobsters, forums, HN and GitHub threads for firsthand detail and informed disagreement. Verify the exact permalink and that it's about this story. Never invent a Reddit URL; no access is "limited access", not "no discussion".
- **Jobs, business, policy:** filings, labour statistics, compensation and hiring datasets with known sampling, regulatory texts, earnings and SEC documents, reputable business reporting. No sweeping conclusions from anecdotes or isolated layoffs.

## Evidence

- Primary documentation for what was announced; independent investigation for what works; reputable reporting for external effects.
- Check publication date **and** event date. Ongoing incidents need fresh sources.
- When credible sources conflict, say so; avoid false precision.

## Link roles

- `sources` (daily) / `links` (weekly): the evidence you used.
- `discoveredVia`: where you genuinely found the story (HN, Reddit, a trending list).
- `discussions`: a community thread that materially discusses the same story.

One link can fill several roles only when each is true. A YouTube video is a source, not a `discoveredVia` entry.
