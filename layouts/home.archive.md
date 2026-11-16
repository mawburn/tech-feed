# {{ site.Title }} — Daily Archive

The most recent seven Pacific calendar days. Each heading is a **briefing date**, not necessarily when its stories first appeared. Every dated edition remains available at {{ (site.GetPage "/daily").Permalink }} and as JSON in the GitHub repository.

Website: {{ site.Home.Permalink }}
Weekly recaps: {{ (site.GetPage "/weekly-latest").Permalink }}
{{ range $issue := partialCached "data/window.html" . }}
## {{ $issue.date }} · {{ $issue.label | default "Daily briefing" }}

{{ $issue.overview }}
{{- range partialCached "data/sections.html" "sections" }}
{{- $section := . }}
{{- with index $issue .key }}

### {{ $section.label }}
{{ range . }}
#### {{ .title }}
Category: {{ partial "data/category.html" . }}

{{ .summary }}
{{ with .whyItMatters }}
**Why it matters:** {{ . }}
{{ end }}{{ with .limitations }}
**Caveat:** {{ . }}
{{ end }}{{ partial "markdown/links.html" (dict "sources" .sources "discoveredVia" .discoveredVia "discussions" .discussions) }}
{{ end }}{{ end }}{{ end }}
### Job market and business pulse

{{ $issue.marketPulse }}

---
{{ end }}
