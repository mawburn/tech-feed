# Editorial writing and briefing-depth standards

Read this file **before drafting** daily and weekly editions, after source discovery and verification. The site should be useful even when a reader does not open the linked article. This is **original, attributed synthesis**, not excerpts, close paraphrases or copied article structure.

## Two levels of explanation

Every substantive story has:

1. A **visible `summary`**: a complete, informative short account, not a teaser. Establish what happened, the relevant who/what/when, the concrete technical or operational specifics, the scope or evidence, and the main implication. Give the reader a reliable understanding without expanding anything.
2. A **structured `briefing` array**: multiple headed sections that *add* context, details, mechanisms, constraints, timelines, comparisons, and practical consequences. The dropdown must stand on its own as a researched brief that largely removes the need to read the original source for general understanding. The article remains available for primary documentation and deeper verification.

Each `briefing` is an array of 2–5 objects: `{"heading":"Specific heading","body":"Specific factual explanation..."}`. Use plain-text body strings, not HTML, Markdown, UI syntax or direct quotes. Section headings should describe the actual subject, not generic fillers. Two or more short paragraphs can be separated by `\n\n` in a body when useful.

## Writing targets (editorial guidelines, not text padding)

- **Daily overview:** roughly 110–180 words (typically 5–8 informative sentences) synthesizing the main developments and their relative significance.
- **Daily top stories:** visible `summary` around 75–130 words (usually 3–5 substantive sentences). Expanded `briefing` around 180–350 words in 3–5 headed sections. `whyItMatters` and `limitations` should add distinct information rather than repeat entire sections.
- **Also worth knowing:** visible `summary` around 50–95 words (typically 3–4 sentences). Expanded `briefing` usually 100–220 words across 2–3 headings, focused on useful concrete context.
- **AI & tooling in practice (`newTools`):** visible `summary` around 60–120 words on what was built or demonstrated, how, and the evidence. Expanded `briefing` of 2–6 sections (about 120–300 words) covering what was done, how it works, why it is interesting and how to reproduce it, plus limitations. Optional `format` label. No fixed entry count. Follow `editorial/APPLICATIONS.md`.
- **Weekly overview:** about 130–220 words explaining the arc of the week, not a list of headlines.
- **Weekly themes:** visible `summary` around 85–145 words; expanded `briefing` 200–400 words in 3–5 sections explaining development over the week, evidence, technical/business effects, and uncertainties. `impact` and `caveat` are concise distinct complements.
- **Weekly AI & tooling in practice (`toolsToWatch`):** visible `summary` around 60–120 words; add `briefing` sections (what was done, how it works, how to reproduce) when details can be verified. No fixed entry count.
- **Market pulse / next-week watch:** meaningful synthesis with specific dates, figures, samples and caveats when verified; do not fill space when there is no material signal.

These ranges are **targets, not minimum quotas**. A short verified report is preferable to verbose speculation. Never hallucinate details to hit a word count.

## Expanded briefing editorial structure

Choose useful headings according to the event. Examples:

- **What actually happened:** chronology, affected versions/services, what was announced versus what has shipped.
- **How it works:** architecture, technical mechanism, implementation choices or concrete limitations.
- **Evidence and independent checks:** confirmed sources, benchmarks and their methodology, disagreements, firsthand experience and what has not been demonstrated.
- **Who is affected / practical impact:** users, engineers, businesses, migrations, costs, security implications or response actions.
- **What remains unresolved:** known gaps, operational recovery, licensing, adoption evidence, unanswered questions and next steps.

For live outages or incidents, track them in `data/incidents/` and link the story with `incidentId` (see `editorial/INCIDENTS.md`); the story states what was known that day while the incident record carries the live status. Include confirmed start/resolution state and observed effects. Distinguish facts from preliminary reports. For acquisitions and policy, explain concrete terms, what changes now versus later, and plausible constraints. For developer releases, explain what is new, how it differs from alternatives, compatibility and real limitations. For a weekly theme, integrate the week's timeline instead of repeating daily news verbatim.

Do not rigidly use all headings for every story. Never restate the same paragraph several times under different headings. Write with an informed technical reader in mind, defining unfamiliar terms briefly where necessary.

## Source integrity and copyright

- Use independent factual language. **Do not quote or closely paraphrase long passages.** Do not reproduce the original article's unique wording, sequence, or detailed expressive structure.
- Support every material factual assertion with actually reviewed sources in `sources` (daily) or `links` (weekly); include useful additional primary links. Source URLs are clickable outside the brief.
- Clearly attribute measurements to vendors or researchers; state uncertainty, unknown totals and study limitations. An unverified claim does not become fact merely because a source repeats it.
- Read the full accessible original announcement, article, report or documentation when practical, including methodology/limitations; do not generate the expanded brief from an isolated headline or search snippet. When access is partial, limit detail to independently verified facts and disclose the access limitation rather than inventing specificity.
- Distinguish article publication time from event time, active incident from resolved incident, and updated stories from new ones.
- New output must include the structured `briefing` field for **every** daily story and each weekly theme. For weekly tools use it when grounded. If there is genuinely not enough evidence to produce two meaningful sections, omit the under-supported story instead of filling with fluff.
- The user-facing chat briefing should provide the full informative visible summaries and can include the most useful expanded context; do not allow publishing to the website to reduce the quality of the chat report.

## Hugo UI / schema contract

The structured `briefing` field is optional in the JSON schema for backward compatibility with historical editions. New scheduled publications are editorially required to populate it as described here. The Hugo templates render `summary` in full, then a native, accessible **Read full briefing** disclosure with each `briefing[].heading` and `briefing[].body`. Older editions retain their original presentation without generated fake detail.

When re-running an existing date, **refresh and expand the actual story content** to the new standard while preserving valid publisher images, HN/Reddit links and other enrichment on unchanged stories. Never invent historic detail or backfill unrelated dates.
