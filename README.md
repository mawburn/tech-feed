# mawburn Feed

Eleventy 3 / Nunjucks static news, deployed on GitHub Pages with **no browser JavaScript needed to render stories**.

**Daily:** https://mawburn.github.io/tech-feed/
**Weekly:** https://mawburn.github.io/tech-feed/weekly.html

## Source files, one edition per commit

    data/daily/2026-11-12.json
    data/daily/2026-11-13.json
    data/daily/2026-11-14.json
    data/daily/2026-11-15.json
    data/weekly/2026-11-15.json

The 7 AM Pacific news task writes one daily date file. The Sunday task writes one Sunday week-ending file. Old dated files remain in Git as history; no automation rewrites a growing JSON array of previous editions.

On each commit Eleventy reads the dated files and GENERATES bounded indexes and site pages under _site/:

- /data/briefings.json: the latest seven Pacific calendar days.
- /data/weekly.json: the latest 52 Sunday recaps.
- /archive.md and /weekly-archive.md: generated readable archives.
- /daily/YYYY-MM-DD/, /daily/YYYY-MM-DD/topics/SLUG/: separate static pages and topic filters.
- /weekly/YYYY-MM-DD/: dated weekly summary.
- /sitemap.xml: dynamically generated XML sitemap.

The generated JSON indexes are build artifacts, not documents maintained by the scheduled automations. Each date has its own JSON source.

## Sources and comment threads

Every story has reporting sources (an array of {label,url}). NEW stories can also include these two optional arrays:

    "discoveredVia": [
      {"platform":"Hacker News","url":"https://news.ycombinator.com/item?id=123","label":"Show HN"}
    ],
    "discussions": [
      {"platform":"Hacker News","url":"https://news.ycombinator.com/item?id=123","label":"HN comments"},
      {"platform":"Reddit","url":"https://www.reddit.com/r/programming/comments/.../","label":"r/programming"}
    ]

The primary sources prove what was reported. Discovered-via links record WHERE the story was encountered. Discussions are actual post/permalink links that lead to relevant comments. These fields are optional; no older story gets guessed or fabricated origin metadata. Hacker News top/new/Show HN, Reddit communities, engineering blogs, GitHub releases/discussions and other credible sources are included in discovery research. Thread URLs must point to individual discussions, not generic subreddit pages.

The official Hacker News API is documented at https://github.com/HackerNews/API.

### Prefetched discussion links (no browser search)

Discussion URLs are looked up in GitHub Actions by `scripts/enrich_discussions.py` **before site generation**. The matcher checks original source URLs, headline similarity, post dates, and actual comments, then writes confirmed matches to `story.discussions` in the individual dated JSON file. The Eleventy site renders these stored links directly. It does not run HN/Reddit searches in the browser or show generic search shortcuts when no match exists.

Hacker News works without credentials through the public Algolia search index.

**Reddit requires approved Data API access**. Unauthenticated Reddit RSS and unofficial archive workarounds have been removed because they were blocked/rate-limited and aren't a dependable production integration. If Reddit approves access for this application, configure these repository **Actions secrets** under Settings → Secrets and variables → Actions:

- `REDDIT_CLIENT_ID` — approved application's OAuth client ID.
- `REDDIT_CLIENT_SECRET` — approved application's client secret.
- `REDDIT_USER_AGENT` — descriptive user agent according to Reddit's requirements (including its app identifier and account contact).

The script uses the `client_credentials` OAuth grant and searches `oauth.reddit.com`; no credentials are exposed in the static website. If they are missing, Reddit lookup is skipped, while HN continues normally. A token alone does not grant permission: obtain explicit API approval first.

Documentation: https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data and https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy.

An optional image object {url,alt,credit,sourceUrl} uses the publisher's real OG image. The source image enrichment workflow can write one recent date file at a time; it is not responsible for discovery links.

## Build/deploy pipeline

1. The Morning AI & Developer Brief automation creates or updates data/daily/YYYY-MM-DD.json on main.
2. The GitHub Actions workflow Sync publisher Open Graph images also **prefetches matching HN discussion threads** and, when approved Reddit API credentials are configured, Reddit comment-thread links. It checks the most recent two daily editions when triggered by a new briefing and runs again every evening (03:17 UTC) to catch later discussions. The same workflow enriches publisher OG image URLs from recent daily source files.
3. Build and deploy static news site validates source files and uses Eleventy to generate _site/. It runs on source changes and after the image sync completes.
4. The Sunday Technology Weekly Review automation writes data/weekly/YYYY-MM-DD.json. The same Eleventy build updates the weekly pages and index.

Required Pages setting: Repository → Settings → Pages → Build and deployment → Source = GitHub Actions.

GitHub Actions token updates don't create another push-triggered workflow; a workflow_run hook handles the image enrichment completion.

## Local development

Node.js 20+; Eleventy 3.1.8 is pinned in package.json.

    npm install
    npm run check
    npm run build
    npm run dev

Generated files are in _site/. Public links use the GitHub Pages project prefix /tech-feed/, so local mounts should account for that prefix.

Template files are in src/ (including src/_includes/partials/story-sources.njk for discovery and comments), with styles in assets/styles.css.

Old root-level client-rendering scripts remain temporarily as rollback material, but they are NOT included in the generated Pages artifact.
