# Standard Markdown Math Pipeline Design

## Objective

Render mathematical Markdown consistently in dashboard prose, including the
single-dollar inline syntax emitted by paper-writing models, without changing
LLM prompts, cached paper inputs, visualization loading, or graph behavior.

The motivating failure is prose such as:

```markdown
The detection input is the model itself: $g_c(\cdot)$ is queried over the input
domain $\mathcal{X}$, while the clean sample set $D$ appears only in the
mitigation problem [§sec_1].
```

The current custom tokenizer recognizes `$$...$$` and `\(...\)` but not
`$...$`, so single-dollar expressions remain unrendered text.

## Scope

This change affects Markdown rendering inside the dashboard's article and
explanation surfaces. It does not alter content generation, model calls,
token usage, cached page files, the graph data contract, or `--viz-dir`.

## Rendering Pipeline

`RichMarkdown` will use the established unified ecosystem:

1. `remark-gfm` parses GitHub-flavored Markdown.
2. `remark-math` parses `$...$` and `$$...$$` into math nodes.
3. `rehype-katex` renders those nodes with the project's local KaTeX package.
4. React Markdown renders the resulting safe React tree.

KaTeX remains local and locked down with `trust: false`. The pipeline must not
load remote fonts, scripts, styles, or other resources.

## Legacy Delimiter Compatibility

Existing pages use `\(...\)` for inline math. Before Markdown parsing, a small
compatibility normalizer will convert complete legacy inline spans to the
standard inline form understood by `remark-math`.

The normalizer must leave these regions untouched:

- inline code spans;
- fenced code blocks using backticks or tildes;
- incomplete `\(` spans;
- escaped dollar signs and ordinary currency text.

Existing `$$...$$` display blocks pass directly to `remark-math`.

## Glossary Interaction

The dashboard currently decorates prose text with glossary tooltips after
Markdown parsing. KaTeX emits a nested span tree containing accessibility and
visual representations of the same equation. Glossary decoration must treat a
KaTeX root as an opaque subtree so it cannot duplicate or corrupt mathematical
markup. Normal prose around the equation remains eligible for glossary
tooltips.

## Failure Behavior

Malformed TeX must not crash the drawer or discard the surrounding paragraph.
KaTeX will render its inert error representation or preserve visible source
text. Trusted HTML and network-capable TeX features remain disabled.

## Dependencies

Add compatible releases of:

- `remark-math`;
- `rehype-katex`.

KaTeX, React Markdown, and `remark-gfm` are already installed. No runtime
service or browser network request is introduced.

## Verification

Regression coverage will verify:

- the motivating `$g_c(\cdot)$`, `$\mathcal{X}$`, and `$D$` sentence renders
  as KaTeX without visible delimiters;
- legacy `\(...\)` inline math still renders;
- `$$...$$` display math still renders;
- math works inside lists and tables;
- code spans and fenced code preserve literal dollar and legacy delimiters;
- escaped dollar signs and currency remain prose;
- glossary decoration does not enter KaTeX markup;
- malformed TeX leaves visible output without throwing;
- the complete dashboard test suite and production build pass.

## Success Criteria

The dashboard renders standard mathematical Markdown reliably while retaining
all current content compatibility and safety behavior. The change adds no LLM
calls, no content rewrite requirement, and no external runtime dependency.
