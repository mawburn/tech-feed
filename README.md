# mawburn Feed

Daily and weekly AI and technology briefings, built with [Hugo](https://gohugo.io/) and published on GitHub Pages as static HTML. No browser JavaScript is used.

- **Daily:** https://mawburn.github.io/tech-feed/
- **Weekly:** https://mawburn.github.io/tech-feed/weekly.html

## Editorial discovery and ranking

The ChatGPT daily and Sunday scheduled tasks read the version-controlled editorial playbooks **before** selecting stories:

- [Discovery protocol](editorial/DISCOVERY.md): rolling 24-hour Hacker News scan, cross-category breaking-incident sweep, source checks and research audit.
- [Ranking rules](editorial/RANKING.md): operational-impact priority and final missing-story check.
- [Source guide](editorial/SOURCES.md): primary sources, independent confirmation and community-link rules.
- [AI & tooling in practice](editorial/APPLICATIONS.md): discovery, selection, verification and writing standards for hands-on applications, tutorials, demos and experiments (daily `newTools`, weekly `toolsToWatch`).
- [Writing standards](editorial/WRITING.md): substantive visible summaries and source-grounded expandable explanations for daily stories and weekly themes.

New daily and weekly JSON files may include an optional root `discoveryAudit` field recording which sources were checked, actual candidate counts where known, material incidents considered and editorial decisions. It is research metadata; it does not replace `sources`, `discoveredVia`, or `discussions`. These instructions are used by the scheduled research task, not executed as a GitHub Actions collector.

## How it fits together

```
ChatGPT scheduler ──commits──▶ data/daily/YYYY-MM-DD.json / data/weekly/YYYY-MM-DD.json  (main)
                                          │ push
                                          ▼
              "Enrich and publish" workflow (sync-og-images.yml), main only
                1. HN + approved Reddit discussion threads  → story.discussions
                2. publisher OG images → assets/img/*.webp  → image.local/width/height/sha256
                3. validate changed files, commit + push to main if anything changed
                4. call deploy-pages.yml ─────────────────┐
                                                          ▼
              "Build and deploy site" workflow (deploy-pages.yml)
                validate (quarantine invalid files) → hugo build → site tests → GitHub Pages
```

- JSON in `data/` is the only content source. Each publication is its own dated file, and the scheduler doesn't need to know anything about Hugo.
- Hugo's **content adapters** (`content/*/_content.gotmpl`) generate a page for every dated file. Templates read the JSON directly through small data partials in `layouts/_partials/data/`.
- The image and discussion enrichment runs only in GitHub Actions against `main`. The Hugo build makes no network requests.

## Data contract

| File | Written by | Schema |
| --- | --- | --- |
| `data/daily/YYYY-MM-DD.json` | Morning scheduler (Pacific date) | [`schemas/daily.v1.schema.json`](schemas/daily.v1.schema.json) |
| `data/weekly/YYYY-MM-DD.json` | Sunday scheduler (week-ending Sunday) | [`schemas/weekly.v1.schema.json`](schemas/weekly.v1.schema.json) |

The schemas describe the scheduler's existing output. They allow unknown properties, so new fields don't break the build. The fields stories use:

- **Required:** `title`, `category`, `summary`, `sources[]` (`{label,url}`).
- **Optional:** `rank`, `whyItMatters`, `limitations`, `isUpdate`, `discoveredVia[]`, `discussions[]`, `briefing[]`, `format` and `image`.

The third daily section is published as **AI & tooling in practice** (hands-on workflows, tutorials, demos and experiments). Its JSON keys stay `newTools` (daily) and `toolsToWatch` (weekly) for compatibility. Neither section has an item cap: any number of entries, including none, renders correctly. An optional `format` string (for example "Video tutorial", "Workflow", "Experiment", "Case study") labels an entry; direct YouTube, GitHub and demo links use the normal `sources[]`/`links[]` structure. A `briefing` may have 2–6 sections.

Weekly reviews carry `themes[]`, `toolsToWatch[]`, `sourceDays[]` and optional summary fields. Each theme, and optionally each weekly tool, may also contain `briefing[]`.

`summary` is a complete, moderately detailed account shown directly on the card. `briefing` adds 2–5 headed sections inside a native **Read full briefing** disclosure:

```json
"summary": "A meaningful multi-sentence account of the event, its scope, evidence and consequences.",
"briefing": [
  {"heading": "What happened", "body": "Additional verified chronology, scope and context."},
  {"heading": "How it works and what changes", "body": "Concrete technical details and implications."}
]
```

These examples show the structure only; actual stories require supported detailed reporting. The field is optional for backward compatibility with old editions, but required by the editorial writing standards for new daily stories and weekly themes. Longer visible summaries are not automatically collapsed into a second, competing disclosure.

Optional link metadata:

```json
"discoveredVia": [{"platform": "Hacker News", "url": "https://news.ycombinator.com/item?id=123", "label": "Show HN"}],
"discussions":   [{"platform": "Reddit", "url": "https://www.reddit.com/r/programming/comments/…/", "label": "r/programming"}]
```

Primary `sources` show what was reported. `discoveredVia` records where a story was found, and `discussions` link to the actual comment threads. Nothing is guessed or fabricated for older stories.

`image` keeps the publisher's metadata: `{url, alt, credit, sourceUrl}`. The image pipeline adds `local` (a path under `assets/`), `width`, `height` and `sha256`. It never changes the original keys.

## Routes

| Path | Content |
| --- | --- |
| `/` | Latest published daily edition |
| `/daily/YYYY-MM-DD/` | Every daily edition (permanent) |
| `/daily/YYYY-MM-DD/topics/SLUG/` | One topic within an edition |
| `/daily/` | Full daily archive |
| `/all/` | Every story from the last seven Pacific days |
| `/topics/`, `/topics/SLUG/` | Topic index; recent stories per topic plus links to earlier coverage |
| `/weekly.html` | Latest weekly review |
| `/weekly/YYYY-MM-DD/`, `/weekly/` | Every weekly review, plus the archive |
| `/data/briefings.json` | Last seven Pacific days, `{schemaVersion:1, updatedAt, issues[]}` |
| `/data/weekly.json` | Latest 52 weekly reviews, `{schemaVersion:1, updatedAt, weeks[]}` |
| `/archive.md`, `/weekly-archive.md`, `/llms.txt` | Markdown and LLM-readable indexes |
| `/sitemap.xml`, `/robots.txt` | Generated |

"Today" is the build date in `America/Los_Angeles`. Editions dated after today are not published yet. The JSON feeds, `/all/` and `/archive.md` cover today and the six days before it. Every build recalculates this window. Builds happen on each new publication and on scheduled enrichment runs that change data. On a day with no new edition, the window moves forward at the next build.

## Project layout

```
editorial/                  source discovery, ranking and verification playbooks
hugo.toml                   site config: base URL, output formats (JSON/Markdown/llms.txt), windows
content/                    section stubs + content adapters (daily, weekly, topics)
layouts/
  baseof.html, home.html…   page templates (one per route type)
  _partials/data/           data access only: editions, windows, slugs, images (no markup)
  _partials/components/     reusable markup: edition, story, story-image, link lists, navs
  _partials/head/           <head> metadata, SEO, JSON-LD
assets/css/                 tokens, base, layout, components, pages (concatenated + fingerprinted)
assets/img/                 optimized publisher images only (committed)
static/                     favicon, logo SVGs (img/), self-hosted Inter (fonts/), .nojekyll
schemas/                    versioned JSON Schemas
scripts/                    validator (Node), enrichment (Python), image policy and manifest
tests/                      site, validator and image-pipeline tests
```

**Design:** the *mawburn dispatch* design (Stitch export, navy "Editorial Charcoal" palette) lives entirely in `layouts/`, `assets/css/` and `static/`.

- **Tokens and CSS:** `assets/css/tokens.css` holds the palette, type, spacing and the six topic accents. The files are concatenated in `head/assets.html`. There is no JavaScript. The "Read briefing" expander is a native `<details>`.
- **Topic accents:** `_partials/data/topic-style.html` maps any category name to an accent and icon by keyword (security, jobs, business, developer tools, infrastructure, AI, else neutral). Templates only emit `topic--{key}`.
- **Components:** `story.html` has `lead`, `brief` and `tool` variants (`tool` renders "AI & tooling in practice" entries in a responsive auto-fill grid). `edition-hero`, `section-index`, `coverage-bars` and `weekly-edition` build the page bodies, and `icon.html` holds the inline SVG icons. Keep `class="story__title"` on story headings and `thread-pill` on discussion links, because the site tests match them.
- **Brand:** the logo SVGs in `static/img/` were generated from the outlined artwork (wordmark, full lockup, mountain mark). The favicon uses the same crescent and mountain.
- **Fonts:** Inter variable (latin, SIL OFL) is self-hosted in `static/fonts/`. Mono text uses the system monospace stack.
- **Images:** the image partial (`components/story-image.html`) renders `srcset`, `sizes`, `width`/`height`, lazy loading and attribution (as an overlay credit), and handles SVGs. It renders nothing when a story has no local image. Adjust `sizes` there and `params.imageWidths` in `hugo.toml` to match a layout change. General long-form text can still collapse at `params.summaryCollapseChars`, but story and weekly-theme summaries are shown fully. Structured `briefing[]` sections use their own native `<details>` element.

## Local development

Requirements:
- Hugo **0.170.0** (standard edition). Install it with `brew install hugo` or from the [releases page](https://github.com/gohugoio/hugo/releases/tag/v0.170.0).
- Node 24 with pnpm 12.21.0. Run `corepack enable` and the version pinned in `package.json` is used.
- Python 3.12+ for enrichment (Pillow and numpy, pinned in `scripts/requirements.txt`).

Install the Node dependencies:

```bash
pnpm install
```

Set up a Python environment for the enrichment scripts:

```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
```

Common commands:

| Command | What it does |
| --- | --- |
| `pnpm validate` | Validate every publication against the schemas |
| `pnpm dev` | Start the dev server at http://localhost:1313/tech-feed/ |
| `pnpm build` | Build to `public/` |
| `pnpm test:site` | Check the built site (routes, feeds, links, images, sitemap) |
| `pnpm check` | Validate, build, then test the site |
| `pnpm test` | Validator tests and offline image-pipeline tests (needs the `.venv` packages) |

To build as if it were another date, set `HUGO_PARAMS_TODAY=2026-11-20` for both the build and `pnpm test:site`.

Run enrichment locally (writes to `data/`, `assets/img/` and `scripts/image_manifest.json`):

```bash
.venv/bin/python scripts/sync_publisher_images.py --dry-run
```

```bash
.venv/bin/python scripts/enrich_discussions.py --days 2
```

## Publishing pipeline

**`sync-og-images.yml` — Enrich and publish**

- **Triggers:**
  - Pushes to `main` under `data/daily/**` or `data/weekly/**`.
  - A schedule at 03:17 UTC, the evening Pacific refresh that picks up discussions posted after the morning briefing.
  - Manual dispatch.
- **Concurrency:** one run at a time (`enrich-main`). Pending runs always process the latest `main`.
- **Enrichment steps:** discussions and images both use `continue-on-error`. If enrichment fails, the new text-only briefing still deploys.
- **Commits:** changes are committed only if the diff is non-empty. The push retries with fetch and rebase, never force. On a rebase conflict with a concurrent scheduler commit, the run gives up quietly and the next run redoes the work.
- **Deploying:** the workflow then calls `deploy-pages.yml` through `workflow_call`. Pushes made with `GITHUB_TOKEN` don't trigger other workflows, and this avoids the old `workflow_run` hook that redeployed even when nothing changed.
- **When it deploys:** after every scheduler push, every manual run, and every scheduled run that changed something. That means one deploy per publication, with no loops.

**`deploy-pages.yml` — Build and deploy site**

- **Triggers:** site changes (`layouts/`, `content/`, `hugo.toml`, `schemas/`, …), manual dispatch, or a call from the enrichment workflow. `data/**` is deliberately not a trigger here.
- **Tooling:** Hugo is downloaded from the official release and checked against its published checksum. Hugo's image cache is restored with `actions/cache`.
- **Validation:** `node scripts/validate-content.mjs --quarantine` removes invalid publications from the build checkout only, never from git. The remaining content builds and deploys, and the run then fails with an error naming the bad files. A malformed publication can't take down the deployed site or block later ones.
- **Final checks:** `pnpm test:site` runs against `public/` before the artifact is uploaded.

Required repository setting: **Settings → Pages → Build and deployment → Source = GitHub Actions**.

### Discussion threads (Hacker News and Reddit)

`scripts/enrich_discussions.py` is unchanged apart from skipping unparseable files. It matches stories to real threads using source URLs, title similarity, post dates and comment counts. It writes only confirmed matches to `story.discussions`, and re-checks the links it added itself earlier.

Hacker News uses the public Algolia API. Reddit needs **approved Data API access**. When access is granted, set these repository **Actions secrets**: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`. Without them, Reddit lookup is skipped. See Reddit's [developer access](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data) and [Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy).

## Publisher images

`scripts/sync_publisher_images.py` replaces hotlinked remote images with optimized local copies.

1. **Discovery.** For daily stories without an image, it reads `og:image`/`twitter:image` from the first two sources, as before.
2. **Download.** Images go through `scripts/safe_fetch.py`:
   - http/https on the default ports only, with no credentials in the URL.
   - Every resolved address must be public. The socket connects to the checked address, which prevents DNS rebinding.
   - Each redirect is re-validated, up to 5 of them.
   - Byte caps: 8 MB per image and 650 KB per HTML page. Timeouts apply throughout.
3. **Validation.** The `Content-Type` and the sniffed format must both be one of JPEG, PNG, WebP, GIF, AVIF or SVG. Other formats are skipped. Anything above 40 MP is rejected before decoding, which guards against decompression bombs, and anything smaller than 200×100 is rejected as an icon or tracking pixel.
4. **Conversion to WebP.**
   - EXIF orientation is applied and the colour is converted to sRGB.
   - Images are fitted within 600×600 and never upscaled. That is enough for a 2× screen at today's display size, with room for a somewhat larger redesign; Hugo builds the smaller sizes.
   - Transparency is kept. Animations use their first frame.
   - All metadata (EXIF, ICC, XMP) is stripped.
   - Quality is chosen per image: the lowest WebP quality, from 60 upwards in steps of 5, whose result still measures as visually identical to the resized original. The measure is structural similarity (SSIM): at least 0.99 on average and 0.95 in the worst 1% of 8×8 blocks, which catches smeared text.
   - The ceiling is 80 for photos and 90 for graphics (PNG/GIF and low-colour images such as screenshots and diagrams). Graphics switch to lossless when that is about the same size.
   - Each file is capped at 50 KB (raster or SVG). Above that, the quality steps down to as low as 40 until it fits; if it still doesn't fit, the image is skipped. In practice files are 2–38 KB, median about 9 KB.
   - **SVG** is kept as a vector, not converted. Each file is sanitized with an allowlist first: scripts, event handlers, `foreignObject`, embedded images, external links and stylesheets, and editor metadata are all removed, because an SVG opened directly could otherwise run code on `mawburn.github.io`. SVGs are never used as `og:image`, since social networks don't accept them.
5. **Storage.** Files go straight into `assets/img/`, which holds nothing but images, named by a content hash (`<sha256-of-source[:20]>.webp`, or `.svg`). Identical images share one file, and only optimized files are committed. At build time Hugo generates 320 and 480 px WebP versions for `srcset` (`params.imageWidths`). These are build output, not committed, so a 160 px thumbnail downloads a 320 px file rather than the full image.
6. **Manifest.** `scripts/image_manifest.json`, kept next to the policy file, records every image URL and article page as ok, failed or skipped.
   - Stored images are never downloaded again.
   - Failures are retried after 3 days, up to 3 attempts.
   - Skipped URLs are not retried. Delete their entry to force a retry.
   - Files are kept even if the source disappears.
7. **Scope and growth limits.** Normal runs cover the last 7 Pacific days and download at most 60 images. The step summary reports the total size, warns at 300 MB, and stops adding images at 750 MB (the GitHub Pages site limit is 1 GB).

**Licensing.** Publisher OG images are shared for link previews, but that is not a licence to redistribute every image. The pipeline therefore:
- skips images whose article page or image response says `noimageindex`;
- skips hosts listed in [`scripts/image_policy.json`](scripts/image_policy.json): stock and wire agencies, plus publishers known to license their photography, such as Reuters, AP, Getty, Bloomberg, WSJ, FT and NYT;
- keeps the original `url`, `credit` and `sourceUrl` on every image and shows the credit, linked to the article, under it.

You can edit the policy file. To remove an image, delete its file and manifest entry, then add the host to the policy.

### Historical backfill

Go to **Actions → Enrich and publish → Run workflow** and tick **backfill** (optionally set `max_images`). The run processes every daily and weekly file, up to the image and time budget, then commits and deploys.

Backfills are restartable and safe to repeat. Run the workflow again to continue, and stored or skipped images aren't fetched again. Normal pushes and scheduled runs only look at recent files.

To run a backfill locally:

```bash
.venv/bin/python scripts/sync_publisher_images.py --backfill --max-images 150
```

## Changes from the Eleventy site

- **Permanent pages.** Dated daily and weekly pages now exist for the full history. Eleventy built only the 7-day and 52-week windows, so old URLs disappeared. The JSON feeds keep their windows.
- **New archive pages:** `/daily/`, `/weekly/` and `/topics/`. Global `/topics/SLUG/` pages persist after a topic leaves the seven-day window.
- **Homepage fallback.** The homepage shows the latest published edition even when it is more than seven days old. Previously it showed an empty state.
- **Local images only.** Images come only from local optimized copies, with no hotlinking. A story has no image until the pipeline has stored one.
- **Single deploy.** Each publication deploys once, after enrichment, instead of once on push and again after enrichment.
- **Feed format.** In `data/briefings.json` and `data/weekly.json`, object keys are now alphabetical (a side effect of Hugo's JSON encoding), and stored images gain an absolute `image.localUrl`.
- **Validation.** It now uses versioned JSON Schemas. Invalid files are quarantined from the build instead of failing the whole deploy.
- **Tooling.** pnpm replaces npm. Eleventy and the old client-side scripts (`assets/app.js`, `assets/weekly.js`, the root `index.html`/`weekly.html`) are gone.
- **Design.** The site uses the mawburn dispatch redesign (see Project layout).
