# "AI & tooling in practice": discovery, selection, verification and writing standards

This section replaces the former "Tools, models & repositories" concept. It highlights interesting, genuinely useful *applications* of AI and other tooling: real workflows, creative experiments, technical tutorials, independent demonstrations, practical integrations and unusual things people have built. It is **not** a product-launch feed.

Data keys are unchanged for compatibility: daily `newTools[]` and weekly `toolsToWatch[]`. Only the published headings and the editorial intent changed. Historical editions keep their original content.

Read this file with `DISCOVERY.md`, `SOURCES.md`, `RANKING.md` and `WRITING.md` before drafting.

## What belongs

Prefer material that shows hands-on evidence, originality, reproducibility and practical value:

- Video tutorials and demonstrations (YouTube and similar) where the creator actually builds or runs something.
- GitHub repositories and examples that someone can clone and run, including small, odd or experimental projects.
- Show HN and similar community project posts with working demos or source.
- Technical writeups, case studies and postmortems of a real workflow or integration, with enough detail to follow.
- Creative or unusual experiments, including ones that partly fail, when the process is documented.
- Practical integrations: wiring models, agents, editors, CLIs, hardware, data pipelines or automation together.

## What does not belong

- New product, model or feature announcements, pricing changes and funding news (these belong in the news sections if significant).
- Promotional, sponsored, affiliate or lead-generation content, "top 10 tools" listicles and AI-generated roundups.
- Demos with no way to inspect what was done (no code, no steps, no method) and unsupported capability claims.
- Repositories that are only a README, a wrapper around a landing page, or star-farming.
- Duplicates of a story already in the same edition's other sections.

A launch may appear here only when an independent party built something notable with it and documented how.

## Discovery

Look broadly and independently of the news sections. **Use the concrete discovery venues and rotating search examples in `editorial/SOURCES.md`**. The daily pass should try YouTube, Show HN, GitHub examples and working demo/independent experiment sources; rotate the other venues and seek smaller creators, technical hobbyists and niche communities. The Sunday review should search across the full week and catch missed examples. Use time-filtered searches where supported; do not treat a year-old tutorial as newly published merely because it was found today. HN, Reddit and similar are discovery leads: record a genuine lead in `discoveredVia` and a matching thread in `discussions`. If a discovery path is unavailable, log it accurately in the audit and use another. Do not set a quota. If nothing meets the bar, publish fewer entries, or none.

## Selection

Judge each candidate on:

1. **Hands-on evidence:** shown running, with real inputs and outputs, not just described.
2. **Reproducibility:** code, prompts, configuration, dataset or enough steps for another person to repeat it.
3. **Originality:** a new idea, combination or perspective, not a rehash.
4. **Practical value:** a reader could learn something or reuse it.
5. **Independence:** made by someone other than the vendor, or clearly labeled when it is first-party.
6. **Freshness:** published or materially updated within the window (state the actual date).

There is **no fixed number** of entries and no display cap. Include every item that clearly meets the bar. Do not pad a thin day or drop a strong item to hit a number.

## Verification

Before including an entry:

- Watch or read the actual material, not only the title, thumbnail, README or comments. For long videos, review the relevant parts and say what you reviewed.
- For repositories check that the code exists and matches the claim: license, recent commits, installation instructions, whether it appears to run, open issues about failures.
- Check numbers and capability claims against what is actually shown. Attribute claims to the author; mark anything not independently confirmed.
- Note requirements that affect reproducibility: paid services or API keys, specific hardware, accounts, model versions, operating system.
- Do not claim to have run or reproduced something unless you did. Say "not independently reproduced" otherwise.
- Link directly to the video, repo, demo or writeup, not to an aggregator page.

## Links

Use the existing `sources[]` (daily) and `links[]` (weekly) structures: `{ "label": "...", "url": "https://..." }`. Link the primary material first and give labels that tell the reader what they are opening, such as `YouTube tutorial`, `Source code`, `Live demo`, `Writeup`, `Dataset`, `Show HN thread`. Include every directly relevant link; there is no link limit in the data. Put a Show HN or Reddit discovery thread in `discoveredVia[]` and a matching conversation in `discussions[]`.

## Content format (optional)

Add an optional `format` string to label what the reader is getting, for example `Video tutorial`, `Workflow`, `Experiment`, `Case study`, `Technical writeup`, `Demo`, `Source code` or `Show HN`. It is free text up to 40 characters. Use one short label; leave it out when none fits.

## Writing

Follow `WRITING.md` for general rules (original synthesis, no copied wording). For this section:

- **Visible `summary`** (about 60–120 words): what was built or shown, by whom (when relevant), the key technique, and the evidence. It must be useful without opening anything.
- **`whyItMatters`** (optional): why it is interesting or useful in practice.
- **`briefing`** (2–6 headed sections, about 120–300 words in total): choose from *What was done*, *How it works*, *Why it's interesting*, *How to reproduce it* (tools, versions, steps, prerequisites, cost) and *Limitations*. Do not fabricate steps that the source does not support.
- **`limitations`**: caveats, unverified claims, and access limits (for example "reviewed the first 20 minutes of the video").
- Neutral, specific, no hype, no promotional adjectives.

### Weekly

`toolsToWatch[]` entries are the week's best practical applications: draw from the dailies and from independent discovery during the week. Each has `title`, `summary` (about 60–120 words), optional `format`, `links[]` and optional `briefing[]` written to the same standard. Include as many as meet the bar; include none rather than fill the space.
