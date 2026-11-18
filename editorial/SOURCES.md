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

## Company engineering and technical developer blogs — rotating discovery catalog

**Purpose:** Find substantive engineering knowledge, incidents, debugging reports, performance work, architecture trade-offs, new developer capabilities, technical investigations, and postmortems that may never get covered by technology news. This catalog is a **discovery map, not an endorsement, ranking, whitelist, story quota, or demand to visit every URL on every run**. Follow current articles and direct technical sources. **Company posts receive no editorial priority merely for being on this list.** Search other organizations and independent engineers too.

**Routine:** Rotate across these categories during the week, going deeper on Sunday. Check the most relevant newly published engineering posts, incident histories and recent significant updates; for any tracked outage or regression, check the *specific responsible provider's* engineering blog, incident history, issue tracker and patch notes even if that provider is not listed. Prefer official engineering/technology subcategories over broad corporate news feeds. Where RSS/Atom is actually available, use it; otherwise use category pages and date-filtered search. Older high-quality posts can supply technical background, **not** a fresh headline by themselves. Verify actual publication and incident dates; some indexes, redirects and archives change.

### Cloud, networking, infrastructure and operational reliability

| Official source | Topics worth checking |
| --- | --- |
| [Cloudflare Blog](https://blog.cloudflare.com/) | DNS/CDN, BGP, networking, security, edge architecture, incident analyses |
| [AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/) and [Amazon Builders' Library](https://aws.amazon.com/builders-library/) | Large-scale design, retries, overload, distributed systems and failure handling |
| [AWS Compute Blog](https://aws.amazon.com/blogs/compute/) and [AWS Database Blog](https://aws.amazon.com/blogs/database/) | Lambda, containers, infrastructure and persistence internals |
| [Google Cloud Blog](https://cloud.google.com/blog) and [Google SRE](https://sre.google/) | Infrastructure, distributed systems, availability, operations and reliability |
| [Microsoft DevBlogs](https://devblogs.microsoft.com/) and [Azure Blog](https://azure.microsoft.com/en-us/blog/) | Runtime internals, Azure, .NET, developer tooling, reliability |
| [Fastly Blog](https://www.fastly.com/blog) | Edge, CDN, traffic engineering, security and outages |
| [Fly.io Blog](https://fly.io/blog/) | Anycast, VMs, distributed SQLite, networking, honest failures |
| [Tailscale Blog](https://tailscale.com/blog) | WireGuard, NAT traversal, networking, security and debugging |
| [Oxide Computer Blog](https://oxide.computer/blog) | Systems software, Rust, firmware, hardware and operational design |
| [Dropbox Tech Blog](https://dropbox.tech/) | Sync, storage, data durability and infrastructure |
| [Uber Engineering](https://www.uber.com/us/en/blog/engineering/) | Storage, service architecture, capacity, performance and distributed systems |
| [Lyft Engineering](https://eng.lyft.com/) | Envoy, service mesh, data infrastructure and experimentation |
| [Netflix TechBlog](https://netflixtechblog.com/) | Chaos engineering, streaming, performance, distributed data systems |
| [Slack Engineering](https://slack.engineering/) | Reliability, cloud migration, testing and service operations |
| [Discord Engineering posts](https://discord.com/blog) | Realtime messaging, voice infrastructure, data migrations and scaling; filter for technical articles |
| [Shopify Engineering](https://shopify.engineering/) | Ruby/React, high-traffic commerce, performance, deploys, data and engineering practices |
| [Backblaze Blog](https://www.backblaze.com/blog/) | Hardware/storage reliability and observed drive-failure data |
| [Ably Blog](https://ably.com/blog) | Realtime messaging, pub/sub, ordering, delivery and scale |
| [incident.io Blog](https://incident.io/blog) | Incident response and concrete internal engineering decisions |

### Software platforms, frontend, developer tools and observability

| Official source | Topics worth checking |
| --- | --- |
| [GitHub Engineering](https://github.blog/engineering/) | Git infrastructure, search, performance, developer systems and incidents |
| [GitLab Engineering](https://about.gitlab.com/blog/categories/engineering/) | CI/CD, builds, testing, repositories and infrastructure |
| [Vercel Blog](https://vercel.com/blog) | Next.js, runtime, web performance, build infrastructure and security; filter marketing |
| [Netlify Blog](https://www.netlify.com/blog/) | Hosting, serverless, build/release systems and web developer tooling |
| [Figma Engineering](https://www.figma.com/blog/engineering/) | Multiplayer synchronization, browser performance, rendering and databases |
| [Canva Engineering](https://www.canva.dev/blog/engineering/) | Frontend, scaling, infrastructure, security and rendering |
| [Linear Blog](https://linear.app/blog) | Local-first-ish sync, architecture and client performance; filter launches |
| [Notion Tech](https://www.notion.com/blog/topic/tech) | Database systems, search, multi-region architecture and performance |
| [JetBrains Blog](https://blog.jetbrains.com/) | IDE internals, compiler/tooling performance and language development |
| [Docker Blog](https://www.docker.com/blog/) | Containers, builds, developer experience and runtime internals |
| [Sentry Blog](https://blog.sentry.io/) | Production debugging, instrumentation, error tracking, profiling |
| [Datadog Engineering](https://www.datadoghq.com/blog/engineering/) | Telemetry systems, profiling, ingestion and observability infrastructure |
| [Grafana Labs Blog](https://grafana.com/blog/) | Prometheus/Mimir/Loki/Tempo, operational design and scaling |
| [Honeycomb Blog](https://www.honeycomb.io/blog) | Observability, tracing and practical production debugging |
| [Temporal Blog](https://temporal.io/blog) | Durable execution, workflows, event processing; filter promotional content |
| [Sourcegraph Blog](https://sourcegraph.com/blog) | Code intelligence, search, agent-assisted software development and evaluations |
| [Prisma Blog](https://www.prisma.io/blog) | TypeScript, ORM and database query-engine internals |
| [V8 Blog](https://v8.dev/blog) | JavaScript engine, compilation, optimization, garbage collection |
| [Chromium Developers Blog](https://developer.chrome.com/blog) | Browser engines, web platform and Chrome developer capabilities |
| [WebKit Blog](https://webkit.org/blog/) | Browser internals, rendering, performance, CSS/JS implementation |
| [Mozilla Hacks](https://hacks.mozilla.org/) | Web standards, Firefox internals and browser engineering |
| [Node.js Blog](https://nodejs.org/en/blog) | Node runtime, APIs, security and releases |
| [Go Blog](https://go.dev/blog/) and [Rust Blog](https://blog.rust-lang.org/) | Language/runtime/compiler features, engineering changes and ecosystem design |
| [React Blog](https://react.dev/blog) | React architecture, renderer, framework guidance and releases |
| [Yelp Engineering](https://engineeringblog.yelp.com/) | TypeScript migrations, GraphQL, search and ML production work |

### Databases, data infrastructure and distributed systems

| Official source | Topics worth checking |
| --- | --- |
| [PlanetScale Blog](https://planetscale.com/blog) | MySQL/Postgres internals, query behavior, backups and operations |
| [ClickHouse Blog](https://clickhouse.com/blog) | OLAP internals, query execution, storage and benchmarks |
| [Neon Blog](https://neon.com/blog) | Serverless Postgres, storage separation and branching |
| [Cockroach Labs Blog](https://www.cockroachlabs.com/blog/) | Distributed SQL, consensus, transactions and failure modes; filter AI marketing |
| [MongoDB Engineering](https://www.mongodb.com/company/blog/engineering) | Storage engines, concurrency, specification and correctness |
| [Confluent Blog](https://www.confluent.io/blog/) | Kafka, Flink, stream processing and operational trade-offs |
| [Materialize Blog](https://materialize.com/blog/) | Incremental computation, dataflow and streaming SQL |
| [Redis Blog](https://redis.io/blog/) | Caching, data structures and Redis internals; filter generic SEO posts |
| [Turso Blog](https://turso.tech/blog) | SQLite, storage engines, Rust and multitenant databases |
| [Supabase Blog](https://supabase.com/blog) | Postgres, realtime, auth and developer platform internals |
| [Elastic Search Labs](https://www.elastic.co/search-labs/blog) | Search internals, retrieval, indexing and performance |
| [Vespa Blog](https://blog.vespa.ai/) | Search, ranking, vector retrieval and evaluation |

### AI systems, compilers, hardware and research engineering

| Official source | Topics worth checking |
| --- | --- |
| [NVIDIA Technical Blog](https://developer.nvidia.com/blog/) | GPU/graphics internals, CUDA, inference, performance, optimization and game tech |
| [Anthropic Engineering](https://www.anthropic.com/engineering) | Agents, evaluation design, practical model infrastructure and limitations |
| [OpenAI Research](https://openai.com/research/) | Research, systems, evaluation methods and technical reports; scrutinize vendor claims |
| [Google Research Blog](https://research.google/blog/) | Systems, algorithms, AI, measurements and research |
| [Google DeepMind Blog](https://deepmind.google/discover/blog/) | ML research, model systems and reproducible evidence |
| [Meta Engineering](https://engineering.fb.com/) | Networks, ML systems, datacenters, storage and open source |
| [Hugging Face Blog](https://huggingface.co/blog) | Model implementations, open-source tooling, inference and practical experiments |
| [Databricks Engineering Blog](https://www.databricks.com/blog/category/engineering) | Data/ML systems, distributed execution, storage and infrastructure |
| [Jane Street Blog](https://blog.janestreet.com/) | OCaml, compilers, correctness, hardware acceleration and formal methods |
| [Microsoft Research Blog](https://www.microsoft.com/en-us/research/blog/) | Systems research, AI evaluation, research implementation and methodology |

### Game engineering, realtime simulation, rendering and anti-cheat — explicit technical beat

**Riot/VALORANT are particularly useful examples of the desired depth.** Technical posts about tick rate, network replication, hit registration, lag compensation, server load, anti-cheat, shader implementation, debugging and performance can be significant without describing a new game release. Avoid equating player-facing patch notes or promotional dev diaries with engineering investigations.

| Official source | Topics worth checking |
| --- | --- |
| [Riot Games Technology](https://technology.riotgames.com/) and [Riot's game-dev tech resources](https://www.riotgames.com/en/game-dev-resources) | Game servers, netcode, anti-cheat, patching, debugging, rendering and developer tooling |
| [VALORANT Dev articles](https://playvalorant.com/en-us/news/dev/) | Technical deep dives when present, netcode/anti-cheat/replays/performance alongside less-technical design updates |
| [Riot: Peeking into VALORANT's Netcode](https://www.riotgames.com/en/news/peeking-valorants-netcode) | **Quality exemplar, not fresh news**: competitive netcode, latency and peeker's advantage |
| [Riot: VALORANT's 128-Tick Servers](https://www.riotgames.com/en/news/valorants-128-tick-servers) | **Quality exemplar, not fresh news**: optimizing game-server compute and profiling |
| [Riot: Scalability and Load Testing for VALORANT](https://www.riotgames.com/en/news/scalability-and-load-testing-valorant) | **Quality exemplar, not fresh news**: game-server capacity and realistic load tests |
| [Roblox Engineering](https://about.roblox.com/engineering) | Engine, networking, platform scale, realtime simulation and runtime performance |
| [Unity Blog](https://unity.com/blog) | Engine internals, graphics, physics, Burst, DOTS, profiling and tooling; filter product promotion |
| [Unreal Engine News](https://www.unrealengine.com/en-US/news) and [Epic Developer Community](https://dev.epicgames.com/community/) | Rendering, engine architecture, optimization, technical Unreal Fest material |
| [Bungie Tech Blog introduction / archive entry](https://www.bungie.net/7/en/News/Article/50139) | Game networking, matchmaking, rendering, tools and automation; check whether new engineering writing exists rather than assuming an active feed |
| [Ubisoft technology research](https://www.ubisoft.com/en-us/company/how-we-make-games/technology) | Snowdrop/Anvil, simulation, graphics, tools, technical R&D |
| [NVIDIA developer game/graphics posts](https://developer.nvidia.com/blog/) | GPU profiling, rendering, shaders, latency and engine optimization |

### Commerce, consumer platforms, finance and large-scale product engineering

| Official source | Topics worth checking |
| --- | --- |
| [Stripe Dev Blog: Engineering](https://stripe.dev/blog/topic/engineering) | APIs, idempotency, payments, database remediation and reliability |
| [Airbnb Engineering](https://medium.com/airbnb-engineering) | Search/ML systems, product experimentation, service and data architecture |
| [DoorDash Engineering](https://careersatdoordash.com/engineering-blog/) | Backend architecture, logistics, platform engineering and data systems |
| [Spotify Engineering](https://engineering.atspotify.com/) | Developer platforms, experimentation, infrastructure and incident reviews |
| [LinkedIn Engineering](https://www.linkedin.com/blog/engineering) | Kafka, distributed storage, search, stream processing and platform systems |
| [Pinterest Engineering](https://medium.com/pinterest-engineering) | ML, high-throughput data and recommendation systems |
| [Etsy Code as Craft](https://www.etsy.com/codeascraft) | Observability, deployment, web scaling and experimentation |
| [Booking.com Tech](https://blog.booking.com/) | Experimentation, infrastructure, mobile and data platforms |
| [Grab Engineering](https://engineering.grab.com/) | Data platforms, scale, infrastructure and systems trade-offs |
| [Zalando Engineering](https://engineering.zalando.com/) | Kubernetes, open source, infrastructure and load balancing |
| [Monzo Technology](https://monzo.com/blog/topic/technology) | Banking infrastructure, microservices, operational reliability |
| [Coinbase Engineering](https://www.coinbase.com/blog/landing/engineering) | Incident postmortems, infrastructure, security and trading-system operations |
| [PayPal Technology](https://medium.com/paypal-tech) | Payment services, storage, scale and production engineering |
| [Netflix TechBlog](https://netflixtechblog.com/) | Revisit for experiment platforms, streaming scale and resilience |

### Independent discovery directories (find omissions, do not substitute for primary sources)

- [73 engineering blogs worth reading](https://bytesizeddesign.com/resources/engineering-blogs) — maintained directory with topic descriptions and RSS information, not a ranking mandate.
- [Engineering.fyi company engineering archive](https://www.engineering.fyi/companies) — cross-company article discovery; follow each finding to its original publisher.
- [Riot game development resource index](https://www.riotgames.com/en/game-dev-resources) — first-party entry point for Riot technical content; don't mistake archived highlights for new posts.

**Editorial filters for every category:**
- Prefer implementation detail, code, measurements, reproducible experiments, diagrams, failures and trade-offs. A deep bug investigation or graphics/netcode technique can beat a routine model launch for practical reader value.
- Distinguish **engineering analysis, incident RCA, tutorial/demonstration, product launch, and corporate opinion**. A product announcement is not an engineering deep dive simply because the company calls it a developer blog.
- When covering an incident, track its original occurrence, mitigation, final fixes and later postmortem across dates; link the direct primary article and status/issue history.
- Search beyond the catalog, check actual new-post dates, independently verify consequential claims, and never invent feeds or claim a source was checked without actually opening it.
- The existing independent technical-blog list below remains complementary and should still be sampled without automatic priority.


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
