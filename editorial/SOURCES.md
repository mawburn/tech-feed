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

## Practical applications and tutorials — specific discovery venues

Used for **AI & tooling in practice**, not to determine the day's breaking-news lead. See `editorial/APPLICATIONS.md` for selection and verification rules. These are **leads**, not approved articles, trusted vendors, or instructions to reproduce their claims. Link the original project/video/code after examining it.

### Core searches for each daily edition

Try these **four distinct discovery paths**, then follow promising material to the original source:

1. **YouTube videos, not just articles**: [YouTube](https://www.youtube.com/). Search by topic, filter or check actual publication dates, inspect real demonstrations, chapters/transcripts where accessible, linked repositories, requirements and results. Search independent makers and small channels, not just high-subscriber creators.
2. **Show HN / small projects**: [Show HN](https://news.ycombinator.com/show), [HN official show feed](https://hacker-news.firebaseio.com/v0/showstories.json), and [HN Algolia](https://hn.algolia.com/api) for time-filtered `show_hn` submissions. Inspect the working demo and source behind each interesting post.
3. **GitHub projects and examples**: [Trending](https://github.com/trending), [AI agents topic](https://github.com/topics/ai-agents), and recently updated code repositories, examples and discussions. Prioritize code actually present, demo/test instructions, license and commit activity over stars.
4. **Working demo ecosystems / independent experiments**: [Hugging Face Spaces](https://huggingface.co/spaces?sort=trending), [Simon Willison's coding-agent experiments](https://simonwillison.net/tags/coding-agents/) and [AI-assisted programming](https://simonwillison.net/tags/ai-assisted-programming/), plus relevant independents. Inspect the actual app, blog entry or implementation.

If one venue is inaccessible, use a reasonable alternative and record `partial`/`unavailable` accurately in `discoveryAudit.sources`. Do **not** claim to have searched YouTube or watched a video merely because a search result shows a title. These paths are separate from the required outage and general-news sweeps.

### Rotating discovery venues (mix across days, deepen on Sundays)

| Place | What to look for | How to evaluate |
| --- | --- | --- |
| [The Coding Train](https://thecodingtrain.com/) | Creative-coding challenges, generative art, simulations, learning projects and linked videos | Concrete technique, runnable examples, originality; not every lesson is new |
| [Sebastian Lague](https://www.youtube.com/channel/UCmtyQOKKmrMVaKuRXz02jbQ) and [project code](https://github.com/SebLague) | Hands-on graphics, simulations, tools and coding adventures | Source availability, engineering tradeoffs, publish date |
| [Hackaday AI](https://hackaday.com/category/artificial-intelligence/) | Odd hardware/software integrations, local models, small experiments | Follow the article to original maker writeup, code and demonstration |
| [Kaggle Notebooks](https://www.kaggle.com/code/) | Runnable ML/data experiments and tutorials | Reproducible notebooks, data and runtime requirements; be wary of leaderboard-only work |
| [ComfyUI workflow examples](https://github.com/comfyanonymous/ComfyUI_examples) | Reproducible image/video workflows, node graphs and techniques | Workflow files, model/license dependencies, hardware requirements |
| [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) | Locally run models, unusual installations, performance tests, maker showcases | Firsthand artifacts, disclosed hardware, reproducible method; treat anecdotes as anecdotes |
| [Lobsters](https://lobste.rs/) | Technical writeups, hobby projects, developer tooling and deep-dive discussions | Go beyond the submission title to original work |
| [GitHub Show-and-Tell / discussions](https://github.com/topics/creative-coding) | Experimental repos, techniques, novel combinations and linked demo videos | Prefer a runnable demo or useful documentation |

Do not let a watchlist become a whitelist. Every run should also search outside the known venues, including non-English creators or niche maker communities when a credible, relevant project appears. Rotate themes (coding agents, software architecture, 3D/Blender, game engines, simulation, creative coding, local inference, data visualization, automation, robotics/hardware, video/audio workflows), and avoid covering the same category or popular creator repeatedly without a material new technique.

### Optional independent technical blogs (supplementary leads, not priority sources)

These are examples of thoughtful, often technically detailed writing to **sample periodically** alongside broad web searches, HN, GitHub and unfamiliar independent authors. They are **not a ranking, a whitelist, a mandatory daily checklist or preferred publication sources**. A post from one of these blogs must meet the exact same freshness, factual relevance, evidence and significance standards as any other source. Do not allocate a fixed number of story slots or give an automatic score boost to any author. A useful old explanation may provide background, but is not new news merely because it has been rediscovered.

| Blog | Possible areas of interest |
| --- | --- |
| [Daniel Doubrovkine — code.dblock.org](https://code.dblock.org/) | Hands-on engineering, AI coding, open source, developer workflows and leadership |
| [Dan Abramov — overreacted.io](https://overreacted.io/) | React, JavaScript, web architecture, developer mental models and unusual programming experiments |
| [Julia Evans — jvns.ca](https://jvns.ca/) | Systems, debugging, Unix, networking and practical explanations |
| [Dan Luu — danluu.com](https://danluu.com/) | Empirical software engineering, performance, benchmarks, infrastructure and skepticism about claims |
| [Brandur Leach — brandur.org](https://brandur.org/articles) | APIs, databases, production engineering and software design |
| [matklad](https://matklad.github.io/) | Languages, compilers, tooling, Rust/Zig and concrete software design |
| [Brendan Gregg's blog](https://www.brendangregg.com/blog/) | Performance analysis, observability, Linux and systems diagnostics |
| [Martin Fowler](https://martinfowler.com/) | Architecture, refactoring, engineering practices and system design |
| [Josh W. Comeau](https://www.joshwcomeau.com/blog/) | Frontend engineering, CSS/React, interactive teaching and creative implementation |

Use **actual new-post dates** and read the original article before summarizing it. For the general news feed, seek substantive new engineering developments, investigations or insights, not every post. For **AI & tooling in practice**, select only entries that demonstrate a concrete workflow, experiment, reproducible technique or useful walkthrough; an opinion essay does not qualify merely because it appears here. Discover other writers through relevant links, citations, niche communities and blogrolls so these examples do not narrow the search. Check author affiliations and commercial interests where they matter; do not assume either independence or accuracy.

### Reusable search patterns

Use different queries and date filters as supported by each platform. Examples; substitute the current topic rather than searching only these exact strings:

- `AI coding agent real project build demo walkthrough source code`
- `local LLM actual workflow benchmark hardware config experiment`
- `Claude Code / Codex / MCP automating Blender or CAD hands-on demonstration`
- `creative coding simulation coding adventure source code tutorial`
- `ComfyUI reproducible workflow video example files`
- `small open-source tool how I built it technical writeup`
- `AI automation engineering workflow what worked what failed`
- `YouTube developer tool experiment build log GitHub repository`

For video results, prefer videos that show input, setup, implementation and output. Search within the **actual daily/weekly time window** where possible; a discovery about an older video should only be presented as fresh when a new build, update, or application occurred during that window. Publish a direct `youtube.com/watch?v=...` or `youtu.be/...` link only after verifying the exact video.

### Distinguish source types

- **Discovery**: HN, Reddit, YouTube search, an aggregator, trending list or a watchlist channel.
- **Primary evidence**: original working demo, creator's video/build log, source code, notebook or detailed engineering writeup.
- **Independent check**: reproducible evaluation, second technical implementation, issue report, knowledgeable criticism or credible third-party review.

Use `discoveredVia` for actual community discovery provenance, `discussions` for relevant matching community threads and `sources[]` / `links[]` for the material supporting the writeup. A useful YouTube video is a source link; do not fabricate a `discoveredVia` community object for YouTube if its provenance structure would misrepresent the data.

### Quality and effort limits

- Prefer surprising **uses** of tools over announcements of the tools themselves. Reject sponsored funnels, repackaged press releases, affiliate "best of" roundups, benchmark claims without methodology and projects without inspectable implementation.
- Investigate promising independent or unfamiliar creators as seriously as known ones. Do not confuse follower counts, stars or upvotes with technical merit.
- Check source accessibility and what was actually read/viewed. When a YouTube video cannot be watched, the title and metadata alone cannot support a detailed technical briefing; use a creator-provided transcript, code, tutorial or another source and describe the limitation.
- No item cap or mandatory number of applications. Attempt the daily discovery paths without inventing check results; publish only genuinely worthwhile entries. Sunday should independently look for missed, substantial week-long use cases, not only repeat daily picks.

## Jobs, business and policy

Use employer filings/announcements, labor statistics, credible compensation and hiring datasets, regulatory texts, earnings/SEC documents, reputable business reporting and studies with identifiable sampling. Avoid making sweeping market conclusions from anecdotes, surveys without representative methodology, or isolated layoffs.

## Evidence hierarchy and timing

Prefer primary documentation for what was announced, independent investigation for what works, and reputable reporting for external effects. Search published dates **and** underlying event dates. When credible sources conflict, state the disagreement and avoid false precision.

Use time-filtered searches and fresh sources for ongoing incidents; evergreen sources alone cannot establish current status. Never say a source was checked solely because the URL appeared in a search result.
