{{- $entries := partial "llm-papers-data.html" . -}}
{{- $fullTextEntries := where $entries "full_text_available" true -}}
{{- $metadataOnlyEntries := where $entries "full_text_available" false -}}
# Matthieu Queloz — Works Index for LLM Retrieval

This file helps language models identify which papers and books on this site are most relevant to a user query before fetching the full text.

- Canonical base URL: {{ site.BaseURL }}
- Scope: English-language pages in the `entries` and `books` sections
- Companion full texts, when available, are linked as `.md` and `.txt`
- HTML hub: {{ "llm/papers/" | absURL }}
- LLM sitemap: {{ "llm/papers/sitemap.xml" | absURL }}
- Works in scope: {{ len $entries }}
- Works with companion full text: {{ len $fullTextEntries }}
- Companion files preserve section headings and printed page markers such as `[p. 12]`

## Retrieval Guidance

1. Use the title, abstract, tags, and categories below to shortlist relevant works.
2. Use the canonical entry URL for citation metadata and the published PDF.
3. When full text is available, prefer the Markdown companion for structured reading and the plain-text companion when Markdown is inconvenient.

## Works With Companion Full Text

{{- range $fullTextEntries }}
### {{ .title }}{{ with .year }} ({{ . }}){{ end }}

Type: {{ .work_type }}
Abstract: {{ .abstract }}
{{ with .citation }}
Citation: {{ . }}
{{ end }}
{{ with .doi }}
DOI: {{ . }}
{{ end }}
Entry: {{ .entry_url }}
{{ with .pdf_url }}
Published PDF: {{ . }}
{{ end }}
{{ with .llm_markdown_url }}
Full text (Markdown): {{ . }}
{{ end }}
{{ with .llm_plain_url }}
Full text (Plain text): {{ . }}
{{ end }}
{{ with .tags }}
Tags: {{ delimit . ", " }}
{{ end }}
{{ with .categories }}
Categories: {{ delimit . ", " }}
{{ end }}

{{ end -}}

## Works Without Companion Full Text

{{- range $metadataOnlyEntries }}
### {{ .title }}{{ with .year }} ({{ . }}){{ end }}

Type: {{ .work_type }}
Abstract: {{ .abstract }}
{{ with .citation }}
Citation: {{ . }}
{{ end }}
{{ with .doi }}
DOI: {{ . }}
{{ end }}
Entry: {{ .entry_url }}
{{ with .pdf_url }}
Published PDF: {{ . }}
{{ end }}
{{ with .llm_markdown_url }}
Full text (Markdown): {{ . }}
{{ end }}
{{ with .llm_plain_url }}
Full text (Plain text): {{ . }}
{{ end }}
{{ with .tags }}
Tags: {{ delimit . ", " }}
{{ end }}
{{ with .categories }}
Categories: {{ delimit . ", " }}
{{ end }}

{{ end -}}
