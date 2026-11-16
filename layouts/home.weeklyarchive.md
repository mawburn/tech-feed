# {{ site.Title }} — Sunday Weekly Summaries

A Monday–Sunday synthesis, with original-source links. The latest {{ site.Params.weeklyWindow | default 52 }} weekly recaps are listed here; every review remains at {{ (site.GetPage "/weekly").Permalink }}.

Website: {{ (site.GetPage "/weekly-latest").Permalink }}
{{ range partialCached "data/weekly-window.html" . }}
## {{ .weekStart }} – {{ .weekEnding }}{{ if .partial }} · Partial week ({{ .coverageDays }} editions){{ end }}

**{{ .title }}**

{{ .overview }}

### Major themes
{{ range $i, $t := .themes }}
#### {{ add $i 1 }}. {{ $t.title }}
Category: {{ partial "data/category.html" $t }}

{{ $t.summary }}
{{ with $t.impact }}
**Why it matters:** {{ . }}
{{ end }}{{ with $t.caveat }}
**Caveat:** {{ . }}
{{ end }}{{ partial "markdown/links.html" (dict "sources" $t.links "discussions" $t.discussions) }}
{{ end }}
### Tools worth investigating
{{ range .toolsToWatch }}
- **{{ .title }}** — {{ .summary }}{{ range .links }}{{ if partial "data/is-http.html" .url }}
  - [{{ .label | default "Source" }}]({{ .url }}){{ end }}{{ end }}
{{ end }}
### Jobs and markets

{{ .marketPulse }}

### Next week

{{ .nextWeekWatch }}

Dates covered: {{ delimit (.sourceDays | default slice) ", " }}

---
{{ end }}
