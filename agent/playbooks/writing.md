# Writing

Applies to the chat report and the JSON. Write original, attributed synthesis that's useful without opening the source: never excerpts, close paraphrase or copied structure.

## Format

- The opening section is **"Summary"** in chat (never "Executive Summary"); the JSON field stays `overview`.
- Narrative fields (`overview`, every `summary`, longer `briefing` bodies, `marketPulse`) are short paragraphs of 2–4 sentences, under about 80 words each. A 1–2 sentence field stays one paragraph.
- Paragraph break: `\n\n` in JSON, a blank line in chat. JSON is plain text: no Markdown, HTML or citations.
- No walls of text; it must read well on a phone. Never cut substance for formatting.

## Every story has two levels

1. **`summary`:** a complete short account: what happened, who, when, the concrete specifics, the evidence, the main implication. Never a teaser.
2. **`briefing`:** 2–5 `{heading, body}` sections (up to 6 for AI & tooling) that *add* mechanism, context, timeline, comparisons and consequences. Headings name the subject. Pick from: what happened, how it works, evidence and independent checks, who's affected, what's unresolved. Don't repeat the summary or restate one paragraph under several headings.

`whyItMatters`, `limitations` (daily) and `impact`, `caveat` (weekly) are short and distinct.

## Lengths (targets, never padding)

| | `summary` | `briefing` |
| --- | --- | --- |
| Daily overview | 110–180 words | |
| Top story | 75–130 | 180–350, 3–5 sections |
| Also worth knowing | 50–95 | 100–220, 2–3 sections |
| AI & tooling in practice | 60–120 | 120–300, 2–6 sections |
| Weekly overview | 130–220 | |
| Weekly theme | 85–145 | 200–400, 3–5 sections |

If you can't support two meaningful briefing sections, drop the story.

## Titles

State what happened: "Anthropic begins IPO roadshow", not "Anthropic IPO".

## By story type

- **Incidents:** what was known that day; the record carries live status. Facts vs preliminary reports.
- **Deals and policy:** concrete terms, what changes now vs later.
- **Releases:** what's new, versus alternatives, compatibility, real limits.
- **Updates:** lead with what changed; don't retell the history.
- **Weekly themes:** the week's arc, not daily summaries pasted together.

## Sources

- Every material claim is backed by a source you actually read: the full accessible original, not a headline or snippet. If access was partial, say so and limit detail.
- Attribute measurements and claims to who made them; state uncertainty. Repetition doesn't make a claim true.
- Separate publication time from event time, active from resolved, updates from new stories.
