# Restructure plan: make the feed easy for the writing agent

Status: decisions recorded, ready for phase 1 · 2026-11-20

## Goal

The ChatGPT scheduled task (the agent) researches, ranks and writes every edition. The repo builds the site from what it commits. Today the agent spends much of its effort on bookkeeping the repo could do, gets no feedback when it makes mistakes, and decides alone what is a landmark story and what continues an earlier one. The result: missed or buried stories (the Anthropic IPO roadshow ran for a week before it was marked `major`), developing stories with no thread (Nvidia's CEO crisis, Nov 12–15), and repeated coverage presented as new (Gemini 4 Hydrogen on Nov 12, 14 and 16).

This plan restructures the repo so that:

1. **The agent writes one file per run and nothing else.** The repo does all bookkeeping.
2. **The repo gives the agent a short, checked list of what to look at** (candidates it can't fetch itself, open tracked stories, scheduled milestones, what it may have missed yesterday).
3. **The repo checks the agent's judgement where it can**: it promotes `major` stories by rule and flags landmark candidates that got no decision.
4. **Every mistake has somewhere to go**: validation results, possible misses and your corrections all feed into the next run.

## Evidence this is based on

| Finding | Source |
| --- | --- |
| The "mandatory" HN Algolia 24h scan failed on every audited day (Nov 16–20); Reddit and YouTube mostly unavailable | `discoveryAudit.sources` in `data/daily/2026-11-16…20.json` |
| GitHub Actions reaches the same Algolia API fine: 47 HN threads attached by CI | `scripts/enrich_discussions.py`, story `discussions` |
| Anthropic IPO: Nov 12 also-worth #8, absent Nov 13, label-only titles Nov 14–15, absent from the Nov 15 weekly, absent Nov 16–17, `major` only from Nov 18 | daily and weekly JSON |
| Thread IDs were added by hand in PR #2; the agent has never set one | git history |
| A security story led 4 of 5 audited days; GPT-6.2 was #4 and the IPO #3/#4 | daily JSON |
| Nov 16 needed four reruns; bot and agent commits interleaved on the same file | git log |
| Every publication arrives as several commits (each incident file, then the edition), each starting an enrich and deploy run | git log |
| Five spellings of the AI category ("AI", "AI & Models", "AI Models", "AI Models & Research", "AI Research") | daily JSON |
| Rejected candidates are never recorded, so a miss can't be traced to discovery or judgement | `discoveryAudit` |
| The playbooks tell the agent to run `pnpm validate`, which it presumably can't | `editorial/INCIDENTS.md` |

## Principles

- **One writer per file.** The agent, you and CI each own separate files. Nobody edits a file someone else writes. This removes the rebase conflicts, the "preserve existing enrichment" instruction and the read-modify-write of incident records.
- **The agent proposes, the repo applies.** Status changes, timelines and promotions are computed by code from what the agent states.
- **Hard checks only for what breaks the site.** Editorial checks are warnings that go back to the agent, so an imperfect edition still publishes.
- **Concrete examples over abstract rules.** Calibration cases from real editions do more than more paragraphs in the playbooks.

## Target layout

```
agent/                          read by the agent; written by you or CI
  prompts/daily.md, weekly.md   the short permanent prompts you paste into ChatGPT        (you)
  DAILY.md, WEEKLY.md           entry points: procedure, output contract, full example    (you)
  playbooks/                    discovery, ranking, writing, in-practice, incidents, sources (you)
  catalog/                      engineering blogs and maker venues, one file per weekday   (you)
  calibration.md                dated real cases: what was right, what was wrong, why     (you)
  landmarks.yaml                entities and event types that make a candidate a landmark (you)
  calendar.yaml                 scheduled events: IPO dates, earnings, conferences, rulings (you)
  overrides.yaml                pins and priorities for tracked stories                   (you)
  context.json                  daily briefing pack for the agent                         (CI)
data/
  daily/YYYY-MM-DD.json         v2 editions                                              (agent)
  weekly/YYYY-MM-DD.json        v2 weekly reviews                                        (agent)
  tracked/<id>.json             incidents and developing stories, built from updates     (CI)
  enrichment/daily/<date>.json  images and discussion threads, keyed by story id         (CI)
  enrichment/weekly/<date>.json                                                          (CI)
  candidates/YYYY-MM-DD.json    raw collector output, kept for the miss check            (CI)
schemas/v2/                     daily, weekly, tracked, enrichment, context, common
scripts/
  collect_candidates.py         new: candidate collector
  apply_tracked_updates.mjs     new: folds edition updates into data/tracked/
  build_context.mjs             new: writes agent/context.json
  migrate_v1_to_v2.mjs          new: one-off migration, also the cutover shim
  validate-content.mjs          rewritten for v2: hard errors and soft warnings
  enrich_discussions.py         writes to data/enrichment/ instead of editions
  sync_publisher_images.py      writes to data/enrichment/ instead of editions
docs/                           README split: architecture, data contract, operations
```

### Who writes what

| Owner | Files |
| --- | --- |
| Agent | `data/daily/*`, `data/weekly/*` (one file per run) |
| You | everything in `agent/` except `context.json`; site code |
| CI | `data/tracked/*`, `data/enrichment/*`, `data/candidates/*`, `agent/context.json`, `assets/img/*`, `scripts/image_manifest.json` |

## Data contract v2

The archive is 9 daily editions, 1 weekly and 9 incidents. Breaking changes are cheap now and expensive later, so v2 drops every compatibility name instead of carrying it.

### Edition (daily)

```json
{
  "schemaVersion": 2,
  "date": "2026-11-21",
  "label": "Saturday briefing",
  "overview": "…",
  "executiveSummary": [
    {"story": "anthropic-lockup-terms", "headline": "…", "text": "…", "links": [{"label": "…", "url": "https://…"}]}
  ],
  "topStories":       [ /* story */ ],
  "alsoWorthKnowing": [ /* story */ ],
  "inPractice":       [ /* story, may carry "format" */ ],
  "marketPulse": {"summary": "…", "business": "…", "jobs": "…", "watch": "…"},
  "trackedUpdates":   [ /* see Tracked stories */ ],
  "discoveryAudit":   { /* see Candidates and decisions */ }
}
```

### Story

```json
{
  "id": "anthropic-lockup-terms",
  "title": "Anthropic discloses lockup terms after first week of trading",
  "category": "business",
  "significance": "major",
  "track": "anthropic-ipo-2026",
  "isUpdate": true,
  "summary": "…",
  "briefing": [{"heading": "…", "body": "…"}],
  "whyItMatters": "…",
  "limitations": "…",
  "sources": [{"label": "…", "url": "https://…"}],
  "discoveredVia": [{"platform": "Hacker News", "url": "https://news.ycombinator.com/item?id=…"}],
  "discussions": [],
  "image": {"url": "https://…", "alt": "…", "credit": "…", "sourceUrl": "https://…"}
}
```

### Changes from v1

| v1 | v2 | Why |
| --- | --- | --- |
| no story id | `id` (kebab-case, unique in the edition; globally `<date>/<id>`) | stable references for the executive summary, enrichment and tracking |
| `rank` | removed; array order is the rank | it duplicated the order and could disagree with it |
| `executiveSummary[].story = "topStories/3"` | `story = "<id>"` | survives reordering |
| `newTools` / `toolsToWatch` | `inPractice` (daily and weekly) | matches what the site shows |
| free-text `category` | fixed list (see Open decisions); each maps to one accent | ends the regex guessing in `topic-style.html` and the spelling drift |
| `incidentId` and `thread` | one `track` field | one tracking system (below) |
| `briefing` optional | required on every new story and weekly theme | it was already required by the playbooks |
| unknown fields allowed | unknown fields rejected | typos like `whyitmatters` fail instead of vanishing |
| `image.local/width/height/sha256`, bot-added `discussions` in the edition | moved to `data/enrichment/` | one writer per file |
| incident files edited by the agent | `trackedUpdates[]` in the edition | the agent never edits shared records |

The weekly review gets the same treatment: theme ids, `inPractice`, `track`, required `briefing`, strict fields.

### Enrichment sidecar

`data/enrichment/daily/2026-11-21.json`, written only by CI:

```json
{
  "stories": {
    "anthropic-lockup-terms": {
      "image": {"url": "https://…", "local": "img/…webp", "width": 600, "height": 315, "sha256": "…"},
      "discussions": [{"platform": "Hacker News", "url": "https://news.ycombinator.com/item?id=…", "label": "HN discussion"}]
    }
  }
}
```

The site merges the sidecar into the story at build time. The agent's own `image` and `discussions` stay in the edition and take precedence. Re-running a day becomes a plain overwrite: enrichment is keyed by story id and survives as long as the id is kept.

## Tracked stories (incidents and developing stories)

Incidents and developing stories become one mechanism with two types. They share storage, timeline, validation and the "follow this story" link. Each keeps its own site section.

| | `incident` | `developing` |
| --- | --- | --- |
| Examples | outages, breaches, exploited vulnerabilities, supply-chain attacks | IPOs, acquisitions, leadership crises, lawsuits, staged launches |
| Status | `investigating`, `identified`, `monitoring`, `resolved` | `developing`, `concluded` |
| Extra fields | `provider`, `rootCause`, `fix`, `fixDate`, `postmortems` | `subject`, `expectedNext[]` (milestone, expected date, confidence) |
| Site | `/incidents/<id>/` (URLs unchanged) | `/developing/<id>/` |

### The agent proposes updates in its edition

```json
"trackedUpdates": [
  {"track": "anthropic-ipo-2026", "action": "open", "type": "developing",
   "title": "Anthropic IPO", "subject": "Anthropic", "summary": "Roadshow began…",
   "expectedNext": [{"milestone": "Pricing", "expected": "2026-11-18", "confidence": "reported"}],
   "sources": [{"label": "…", "url": "https://…"}]},
  {"track": "nginx-http2-rce-2026-11", "action": "update", "status": "monitoring",
   "summary": "Patched builds now in major distributions…", "sources": [{"label": "…", "url": "https://…"}]}
]
```

Actions: `open`, `update`, `milestone` (a decisive event, e.g. pricing or first trade), `resolve` / `conclude`, `correction`. The entry date defaults to the edition date.

### CI applies them

`scripts/apply_tracked_updates.mjs` runs in the enrichment workflow:

- appends each update to the record's `history` in order;
- recomputes `status`, `resolvedDate`, `summary` and `expectedNext` from the history;
- rejects an `update` to a track that was never opened, or a second `open` for the same id;
- commits `data/tracked/*` in the same commit as enrichment.

Status/history consistency, date order and `resolvedDate` rules stop being instructions to the agent and become code.

### Your overrides

`agent/overrides.yaml` lets you pin or prioritise a track without touching CI-owned files:

```yaml
anthropic-ipo-2026:
  priority: lead-on-milestones   # a milestone story must be the lead or carry significance: major
  watch: [lockup expiry, first earnings]
```

## Placement: rank versus landmark

Two separate slots at the top, each decided by a clear rule:

- **Lead story** (first in `topStories`): the most urgent story today. The agent decides, using the ranking rubric. Active incidents can win this.
- **Big story banner**: every `significance: "major"` story from the last seven days, one per track. The site places these automatically and lists them first in the executive summary, whatever their rank.

So a landmark like the IPO no longer has to beat an active vulnerability for #1 to be seen first. The agent no longer has to remember the promotion rules; it only answers "is this major?", which the landmark flags (below) force it to answer.

## Agent entry point and context

### `agent/DAILY.md` and `agent/WEEKLY.md`

The prompt points at one of these; the agent reads it every run. Once the context file exists (phase 4), the daily order is:

1. Read `agent/context.json`.
2. Deal with last run's errors and possible misses.
3. Re-check open tracked stories and milestones due.
4. Decide every must-decide candidate; do your own discovery beyond the list.
5. Rank, judge significance, write.
6. Commit one file: `data/daily/<date>.json` (or the weekly).

It then gives the output contract, one complete valid example, and links to the playbooks for depth. Hugo internals, compatibility notes and repo history come out of everything the agent reads. Target: under 200 lines each, with the playbooks trimmed from ~630 lines. The weekly follows the same pattern over the week's editions, tracked stories and possible misses.

### `agent/context.json`

Rebuilt by the 22:30 UTC collector run before each agent run:

```json
{
  "forDate": "2026-11-21",
  "generatedAt": "2026-11-21T23:05:00Z",
  "lastRun": {
    "edition": "2026-11-20", "published": true,
    "errors": [], "warnings": ["story 'os-patch' title looks like a label"],
    "undecided": ["c-20261120-014"]
  },
  "possibleMisses": [{"candidate": "c-20261120-031", "title": "…", "why": "HN 812 points, 6 outlets, not covered"}],
  "openTracked": [{"id": "anthropic-ipo-2026", "type": "developing", "status": "developing",
                   "lastUpdate": "2026-11-19", "expectedNext": [{"milestone": "Lockup terms", "expected": "2026-11-24"}],
                   "priority": "lead-on-milestones"}],
  "due": [{"date": "2026-11-21", "what": "…", "source": "calendar"}],
  "recentStories": [{"ref": "2026-11-19/anthropic-first-trade", "title": "…", "track": "anthropic-ipo-2026"}],
  "categories": ["ai-models", "ai-products", "developer-tools", "…"],
  "candidates": [ /* see below */ ]
}
```

The agent reads one file it can already reach (it reads the repo through GitHub) instead of crawling `data/`.

## Candidate collector

`scripts/collect_candidates.py`, run by a scheduled workflow at 22:30 UTC, ahead of the agent's 17:00 Pacific run. It reuses `safe_fetch.py` and the HN code from `enrich_discussions.py`.

**Sources** (configured in `agent/sources.yaml`):

- Hacker News: Algolia 24h by points and by date; official top, best, show
- Lobsters hottest
- CISA Known Exploited Vulnerabilities feed; critical GitHub security advisories
- status pages: Statuspage-based providers (GitHub, Cloudflare, OpenAI, Anthropic, Atlassian…) plus AWS, Azure and GCP feeds
- RSS: major vendor and engineering blogs, technology news outlets
- Reddit, once API access is approved

**Processing:**

- cluster duplicates (same canonical URL, similar titles, shared primary link);
- attach signals: HN points and comments, points per hour, number of independent outlets, KEV listed, live status incident;
- flag `landmark` when a candidate matches `agent/landmarks.yaml` (entity plus event type, e.g. Anthropic plus IPO);
- flag `tracked:<id>` when it matches an open tracked story's aliases;
- mark `mustDecide` for landmark, KEV, live status incidents, tracked matches and the top N by signal.

**Output:** `data/candidates/<date>.json` (kept for the miss check) and the `candidates` list in `agent/context.json`.

### Candidates and decisions

The agent records a decision for every must-decide candidate, and may add its own finds:

```json
"discoveryAudit": {
  "checkedAt": "…", "windowStart": "…", "windowEnd": "…",
  "sources": [ /* as today */ ],
  "decisions": [
    {"candidate": "c-20261121-003", "decision": "selected", "story": "nginx-http2-patch"},
    {"candidate": "c-20261121-011", "decision": "rejected", "reason": "Vendor benchmark only; no independent evidence"},
    {"candidate": "c-20261121-019", "decision": "merged", "story": "anthropic-lockup-terms"},
    {"candidate": null, "decision": "selected", "story": "frostbite-cpu-codesign", "foundVia": "own search"}
  ],
  "rankingNotes": "…"
}
```

A miss can then be traced: never collected (fix the sources), collected but rejected (fix the judgement, add a calibration case), or not flagged (fix the landmark list).

## Validation

`scripts/validate-content.mjs` rewritten for v2.

**Hard errors** (the edition is quarantined, as today):

- schema violations, including unknown fields
- duplicate story ids; `executiveSummary` or `decisions` pointing at a story that doesn't exist
- `track` that isn't an existing record or opened in the same edition
- invalid `trackedUpdates` (update before open, unknown status, dates out of order)

**Soft warnings** (published anyway; reported in `agent/context.json`, the workflow summary and optionally a GitHub issue):

- must-decide candidates with no decision
- a landmark candidate rejected without a reason
- a story on an open track without `isUpdate`, or a story that closely matches a recent one with no `track`
- label-like titles (fewer than four words, no verb)
- a track with `priority: lead-on-milestones` whose milestone story is neither the lead nor `major`
- weekly: a track with a milestone that week that isn't covered by a theme or explained in the audit
- weekly: a daily edition from that week not listed in `sourceDays`

## Feedback loop

- **Miss check, folded into the collector.** Each 22:30 UTC run first compares the previous edition with that day's candidates file plus anything that gained signal since (higher HN points, more outlets, a new KEV listing or status incident), then writes `possibleMisses` into `agent/context.json`. The run that follows decides whether each deserves a follow-up. The 03:17 UTC run stays enrichment-only.
- **Calibration.** `agent/calibration.md` holds dated real cases, each with the call that was made, the right call and the reason. Seed cases:
  - Anthropic IPO roadshow (Nov 12): should have opened a developing track and been `notable`, with pricing expected
  - Anthropic IPO pricing (Nov 18): `major` was right; it belongs in the banner even at #3
  - Nvidia CEO resignation and fallout (Nov 12–15): one developing track, not four unconnected stories
  - Gemini 4 Hydrogen (Nov 12, 14, 16): a repeat must be an update on a track or left out
  - "Anthropic IPO" as a story title (Nov 14–15): titles state what happened
- **Your corrections.** Add a calibration case, a landmark entry, a calendar entry or an override. Each is a small edit to a file you own.

## Site changes

- Data partials read v2 fields and merge enrichment sidecars (`data/with-enrichment.html` replaces `with-local-image.html`).
- `topic-style.html` maps the category list directly to accents; the regex goes.
- Executive summary and Big story banner order `major` stories first automatically.
- Tracked stories: shared timeline components; `/incidents/<id>/` keeps its URLs; new `/developing/` and `/developing/<id>/`; story cards show "Track this incident" or "Follow this story".
- `/data/briefings.json` and `/data/weekly.json` move to `schemaVersion: 2`. This is a public format change; note it in the docs.
- `llms.txt`, Markdown archives and site tests updated for v2.

## Phases

Each phase ends with the site building, all tests passing and the agent able to publish.

### Phase 0: decisions and baseline

- Decisions are recorded below; the one open item is whether the task can open PRs.
- Build the current site with a fixed `HUGO_PARAMS_TODAY` and keep `public/` as a baseline for comparison.
- Tag the last v1 commit.

### Phase 1: move the instructions into the repo

The current ChatGPT prompts are about 4,500 words each, and much of that repeats or contradicts the `editorial/` files (see "The current prompts" below). This phase moves every instruction into the repo, still on the v1 data format, and replaces both prompts with short permanent ones (`agent/prompts/daily.md`, `agent/prompts/weekly.md`) that only say "read `agent/DAILY.md` (or `WEEKLY.md`) and follow it".

- `agent/DAILY.md` and `agent/WEEKLY.md`: the procedure in order, the v1 output contract with one full example, the chat report format, the paragraph and "Summary" heading rules, and what the agent may write.
- `agent/playbooks/`: the `editorial/` files, de-duplicated against the prompts, with Hugo internals and compatibility notes removed. Each `editorial/` file becomes a pointer to its replacement, so a run still on the old prompt reads the new content; delete them once both tasks are on the new prompts.
- Fix what's stale or impossible today:
  - remove the "incident registry not yet committed" gate (it is committed)
  - correct the site URL to news.mawburn.com and drop "Morning" from the daily title
  - stop requiring the HN Algolia API; use HN's official pages until the collector exists, and record the scan as `partial`
  - stop asking it to "check against the schema" (it can't run code); point it at the full example instead
  - one ranking rule set (the prompt's list and `RANKING.md` currently disagree)
  - teach `significance`, `thread` and `executiveSummary`, which no prompt mentions and which reached `RANKING.md` only after the last run
- `agent/calibration.md` with the seed cases.
- **You paste the two short prompts once.** After that, every contract change in later phases ships as a repo change to `agent/` in the same PR as the code, so the prompt never lags the schema.
- **Exit check:** one daily run on the new prompt publishes a valid edition and its audit shows it read `agent/DAILY.md`.

### Phase 2: v2 contract and one writer per file

- `schemas/v2/` (daily, weekly, enrichment, common) with strict fields.
- `scripts/migrate_v1_to_v2.mjs`: assign story ids from titles; check `rank` matches order, then drop it; rename sections; map categories; convert executive-summary references to ids; move `image.local/width/height/sha256` and bot-added discussions (HN with label "HN discussion") into sidecars.
- Point both enrichment scripts at `data/enrichment/`; the image manifest is unchanged.
- Rewrite the validator for v2 hard errors (soft warnings come in phase 4).
- Update templates, feeds and tests, and `agent/DAILY.md` / `WEEKLY.md` to the v2 contract in the same PR.
- **Cutover shim:** for two weeks, CI upgrades any v1 file it receives with the migration script, covering a run that started before the merge.
- **Exit check:** rebuilt site matches the phase 0 baseline except for intended changes (accent mapping, feed `schemaVersion`).

### Phase 3: tracked stories and placement

- `schemas/v2/tracked.json`; `scripts/apply_tracked_updates.mjs` in the enrichment workflow.
- Migrate the 9 incident records into `data/tracked/` (type `incident`, history kept).
- Open `anthropic-ipo-2026` and `nvidia-leadership-2026` (or your preferred id) from existing stories, and set `track` on the Nov 12–15 Nvidia stories.
- `track` replaces `incidentId` and `thread` in editions (in the migration).
- Site: `/developing/` pages, shared timeline, automatic `major` ordering.
- `agent/` files: `trackedUpdates` replaces editing incident files; `agent/overrides.yaml`.
- **Exit check:** incident pages unchanged; the Anthropic IPO shows as one developing story with a dated timeline.

### Phase 4: context file and feedback

- `agent/landmarks.yaml`, `agent/calendar.yaml`.
- `scripts/build_context.mjs` and the `agent/context.json` it writes (without candidates yet); `agent/DAILY.md` starts from it.
- Soft warnings in the validator, reported into the context.
- **Exit check:** a run reads `context.json`, handles last run's warnings and re-checks open tracked stories.

### Phase 5: candidate collector

- `scripts/collect_candidates.py`, `agent/sources.yaml`, scheduled workflow.
- Clustering, signals, landmark and tracked flags, must-decide marking.
- `candidates` in `context.json`; `decisions` in the audit; the undecided warning.
- **Exit check:** a week of candidate files where every published story either matches a candidate or is marked `own search`, and the HN scan is no longer "unavailable".

### Phase 6: miss check

- Comparison of the previous edition at the start of each collector run; `possibleMisses` in `context.json`.
- Weekly review reads tracked milestones and the week's possible misses.
- **Exit check:** possible misses appear in the next day's context and are either covered or dismissed with a reason.

### Phase 7: cleanup

- Split the README into a short README plus `docs/architecture.md`, `docs/data-contract.md`, `docs/operations.md`.
- Remove the "Changes from the Eleventy site" section, `summaryCollapseChars`, and `new_design/`.
- Drop the cutover shim once the scheduler has published v2 for two weeks.

### Prompt changes

Only once, in phase 1: paste `agent/prompts/daily.md` and `agent/prompts/weekly.md` into the two scheduled tasks. Every later change is a repo change to `agent/`.

### The current prompts

What the phase 1 rewrite fixes, from the prompts as of 2026-11-20:

- **Two copies of every rule.** HN discovery appears three times (prompt preflight, prompt body, `DISCOVERY.md`); incident rules, writing targets and the engineering-blog catalog are in both the prompt and the repo. Rules are added as dated patches ("added 2026-11-17") that aren't versioned or reviewable.
- **Conflicting ranking rules.** The prompt ranks by "consequence, technical significance, evidence, practical relevance, community interest"; `RANKING.md` puts active incidents first, then scores six factors.
- **Never told about landmarks.** No prompt mentions `significance`, `thread` or `executiveSummary`. They reached `RANKING.md` in PR #2, which merged after the Nov 20 run, so the agent has never been asked to mark a story `major` or continue a thread; the existing ones were added by hand.
- **Stale:** the incident-registry gate says the registry is "not yet committed"; the published site URL is the old `mawburn.github.io/tech-feed`; the daily is titled "Morning" but runs at 17:00.
- **Impossible steps:** the Algolia API (fails every run), "check the completed document against the schema" (no code execution), merging enrichment by SHA.
- **Story counts live only in the prompt** (5–8 top stories, 5–10 also worth knowing).

## Decisions

1. **What the scheduled task can do.** Design for the minimum the evidence supports:
   - **Reads the repo** through the ChatGPT GitHub app.
   - **Writes whole files straight to `main`, as you.** Its commits are unsigned, one file each, authored and committed as your account, pushed directly to `main`; it has never opened a PR or created a branch (PR #2 came from Claude Code). OpenAI documents the GitHub app as read-only and points to Codex for writes ([help article](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt); OpenAI support repeated this in September 2026 in a [community thread](https://community.openai.com/t/feature-request-add-apply-patch-partial-file-updates-to-the-chatgpt-github-app/1390673) that also describes the same whole-file write behaviour). So the write path works but is undocumented, and could change.
   - **Searches the web and reads pages, but can't call JSON APIs.** The HN Algolia API failed on every audited day while the HN HTML pages worked.
   - **PRs: unknown.** To find out, check the GitHub app's action list in ChatGPT, or run the task once with "create a branch and open a draft PR" on a test file. Until then: CI collects anything that needs an API, validation stays post-commit (quarantine plus warnings fed back through `agent/context.json`), and everything else lives in repo files the agent can read.
   - **Alternative worth considering later:** Codex automations officially push branches and open PRs, and can run the validator before submitting. Moving the writer to Codex would enable validation before merge, but it's a tooling change, not part of this plan.
2. **Run time: 17:00 Pacific.** The collector runs at 22:30 UTC (14:30 PST / 15:30 PDT), leaving room for GitHub's scheduled-run delays. Fix the README's "morning scheduler" wording.
3. **Top of page: urgency-ranked lead plus the automatic Big story banner** for `major` stories.
4. **Categories: no fixed count.** Start from the list below and adjust while mapping the existing editions in phase 2: `ai-models`, `ai-products`, `developer-tools`, `security`, `cloud-infrastructure`, `hardware-chips`, `databases`, `business-markets`, `jobs-labor`, `policy-regulation`, `research`, `other`. Each maps to one accent.
5. **One tracking system** for incidents and developing stories, as long as it tracks over time: every tracked story keeps a dated, append-only history, shown as a timeline on its page and linked from every story that covers it.
6. **Delete `new_design/`** (it stays in git history).
7. **Reddit: pending.** The collector's Reddit source stays off until the `REDDIT_*` secrets exist, the same as enrichment today.

## Risks

- **The agent's write path is undocumented.** If OpenAI removes whole-file writes from the GitHub app, publishing stops. Nothing in this plan makes that worse (the agent writes fewer files than today); Codex is the documented fallback.
- **Prompt lag.** Removed by phase 1: the prompt only points at `agent/`, so contract changes and instructions ship together. The cutover shim covers a run already in progress when a change merges.
- **The agent ignores the pointer.** It might lean on its memory of the old prompt. The phase 1 exit check confirms it reads `agent/DAILY.md`; keep the old prompts saved so you can roll back.
- **Collector noise.** Too many must-decide candidates and the agent rubber-stamps rejections. Start with a small top N plus hard flags (landmark, KEV, live incident), and tune with a week of data.
- **Public feed consumers.** `/data/briefings.json` changes shape. Bump `schemaVersion` and document it; there are no known external consumers.
- **CI writes more of the repo.** Every CI write goes through one workflow with one concurrency group, and agent-owned files are never touched, so the rebase-conflict path should no longer trigger.
- **Status page and RSS sources change.** Each collector source fails independently and is reported as unavailable in the context, never as zero results.
