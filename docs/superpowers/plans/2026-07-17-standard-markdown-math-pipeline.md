# Standard Markdown Math Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render `$...$`, `$$...$$`, and existing `\(...\)` mathematical Markdown through the standard remark/rehype KaTeX pipeline without changing generated paper content or model usage.

**Architecture:** `remark-math` will add standard math nodes to the existing React Markdown pipeline and `rehype-katex` will render those nodes with local, untrusted KaTeX. The current Markdown preprocessor will become a narrow legacy-delimiter adapter that converts complete `\(...\)` spans outside code into `$...$`; glossary decoration will treat KaTeX output as opaque.

**Tech Stack:** React 19, React Markdown 10, remark-gfm 4, remark-math 6.0.0, rehype-katex 7.0.1, KaTeX 0.16, TypeScript, Vitest, Vite.

## Global Constraints

- Do not change LLM prompts, model calls, token usage, cached paper files, graph data, or `--viz-dir` behavior.
- Keep KaTeX local with `trust: false`; add no remote runtime resources.
- Preserve literal content in inline code spans and fenced code blocks.
- Keep escaped dollar signs and ordinary currency as prose.
- Preserve visible output and surrounding prose when TeX is malformed.
- Do not stage or modify the user's existing changes in `scripts/gate_slice7.py`, `src/paper_skill/p3_research.py`, `src/paper_skill/p4_write.py`, `src/paper_skill/p6_explorer.py`, or `artifacts/`.

---

### Task 1: Standard Markdown math rendering

**Files:**
- Modify: `dashboard/package.json`
- Modify: `dashboard/package-lock.json`
- Modify: `dashboard/src/lib/mathHtml.ts`
- Modify: `dashboard/src/lib/mathHtml.test.ts`
- Modify: `dashboard/src/components/Drawer.tsx`
- Modify: `dashboard/src/components/Drawer.test.tsx`

**Interfaces:**
- Consumes: `RichMarkdown({ glossary, markdown })`, `safeKatexOptions(displayMode)`, and `preserveMathForMarkdown(markdown)`.
- Produces: standard `$...$` and `$$...$$` rendering, legacy `\(...\)` compatibility, and `safeKatexPluginOptions()` for the rehype plugin.

- [ ] **Step 1: Install the two pinned parser/rendering plugins**

Run:

```powershell
cd dashboard
npm.cmd install --save-exact remark-math@6.0.0 rehype-katex@7.0.1
```

Expected: `package.json` and `package-lock.json` add exactly those dependencies; npm reports no vulnerabilities.

- [ ] **Step 2: Replace the legacy preprocessor assertions with compatibility behavior tests**

In `dashboard/src/lib/mathHtml.test.ts`, import `safeKatexPluginOptions` and replace the `preserveMathForMarkdown` display-escaping assertions with:

```ts
describe("preserveMathForMarkdown", () => {
  it("normalizes complete legacy inline math for remark-math", () => {
    expect(
      preserveMathForMarkdown(String.raw`Scale by \(\sqrt{d_k}\).`),
    ).toBe(String.raw`Scale by $\sqrt{d_k}$.`);
  });

  it("leaves display math, code, and incomplete legacy spans unchanged", () => {
    const markdown = String.raw`$$\sqrt{d_k}$$

\(unfinished

\`\(inline_code\)\`

\`\`\`tex
\(fenced_code\)
\`\`\``;

    expect(preserveMathForMarkdown(markdown)).toBe(markdown);
  });
});
```

Add this assertion beside the existing locked-down KaTeX option test:

```ts
expect(safeKatexPluginOptions()).toMatchObject({
  output: "html",
  strict: "error",
  throwOnError: false,
  trust: false,
});
```

- [ ] **Step 3: Add failing renderer regressions for the reported prose and Markdown edge cases**

In `dashboard/src/components/Drawer.test.tsx`, replace the old inline-delimiter assertion and add these focused behaviors:

```tsx
it("renders standard single-dollar inline math in the reported sentence", () => {
  const markdown = String.raw`The detection input is the model itself: $g_c(\cdot)$ is queried over the input domain $\mathcal{X}$, while the clean sample set $D$ appears only in the mitigation problem [§sec_1].`;
  const markup = renderToStaticMarkup(
    <RichMarkdown glossary={{}} markdown={markdown} />,
  );

  expect(markup.match(/class="katex"/g)).toHaveLength(3);
  expect(markup).not.toContain("$g_c");
  expect(markup).not.toContain("$\\mathcal{X}$");
  expect(markup).toContain("§sec_1");
});

it("keeps legacy inline math rendering through the standard pipeline", () => {
  const markup = renderToStaticMarkup(
    <RichMarkdown glossary={{}} markdown={String.raw`Scale by \(\sqrt{d_k}\).`} />,
  );

  expect(markup).toContain('class="katex"');
  expect(markup).not.toContain(String.raw`\(\sqrt{d_k}\)`);
});

it("renders math in lists and GFM tables", () => {
  const markdown = String.raw`- score $g_c(x)$

| domain |
| --- |
| $\mathcal{X}$ |`;
  const markup = renderToStaticMarkup(
    <RichMarkdown glossary={{}} markdown={markdown} />,
  );

  expect(markup).toContain("<li>");
  expect(markup).toContain("<table>");
  expect(markup.match(/class="katex"/g)).toHaveLength(2);
});

it("preserves code and escaped currency as prose", () => {
  const markdown = String.raw`Cost is \$5; keep \`$g_c(x)$\` literal.

\`\`\`tex
$D$
\`\`\``;
  const markup = renderToStaticMarkup(
    <RichMarkdown glossary={{}} markdown={markdown} />,
  );

  expect(markup).toContain("Cost is $5");
  expect(markup).toContain("<code>$g_c(x)$</code>");
  expect(markup).toContain("<code class=\"language-tex\">$D$");
});

it("keeps glossary decoration outside KaTeX output", () => {
  const markup = renderToStaticMarkup(
    <RichMarkdown
      glossary={{ model: "A learned function." }}
      markdown={String.raw`model $\operatorname{model}(x)$`}
    />,
  );

  expect(markup.match(/class="tooltip"/g)).toHaveLength(1);
  expect(markup).toContain('class="katex"');
});

it("leaves malformed TeX visible without throwing", () => {
  const markup = renderToStaticMarkup(
    <RichMarkdown glossary={{}} markdown={String.raw`Before $\notACommand{$ after.`} />,
  );

  expect(markup).toContain("Before");
  expect(markup).toContain("after");
  expect(markup).toContain("katex-error");
});
```

- [ ] **Step 4: Run the focused tests and verify RED**

Run:

```powershell
cd dashboard
npm.cmd test -- src/lib/mathHtml.test.ts src/components/Drawer.test.tsx
```

Expected: failures show that single-dollar math is still plain text, `safeKatexPluginOptions` is missing, and legacy normalization has not been implemented. Existing display-math tests should continue to pass.

- [ ] **Step 5: Convert the preprocessor into a code-aware legacy adapter**

In `dashboard/src/lib/mathHtml.ts`, retain the existing fence traversal in `preserveMathForMarkdown`, but replace `protectMathInProse` with this behavior:

```ts
function normalizeLegacyMathInProse(text: string): string {
  let output = "";
  let cursor = 0;

  while (cursor < text.length) {
    if (text[cursor] === "`") {
      let ticks = 1;
      while (text[cursor + ticks] === "`") ticks += 1;
      const delimiter = "`".repeat(ticks);
      const close = text.indexOf(delimiter, cursor + ticks);
      if (close < 0) return output + text.slice(cursor);
      output += text.slice(cursor, close + ticks);
      cursor = close + ticks;
      continue;
    }

    if (text.startsWith(String.raw`\(`, cursor)) {
      const close = text.indexOf(String.raw`\)`, cursor + 2);
      if (close < 0) return output + text.slice(cursor);
      output += `$${text.slice(cursor + 2, close)}$`;
      cursor = close + 2;
      continue;
    }

    output += text[cursor];
    cursor += 1;
  }

  return output;
}
```

Change both prose flushes in `preserveMathForMarkdown` to call `normalizeLegacyMathInProse`. Do not encode or rewrite `$$...$$`; `remark-math` owns display parsing.

Add a plugin-safe option source beside `safeKatexOptions`:

```ts
export function safeKatexPluginOptions() {
  return {
    output: SAFE_KATEX_OPTIONS.output,
    strict: SAFE_KATEX_OPTIONS.strict,
    throwOnError: false,
    trust: SAFE_KATEX_OPTIONS.trust,
  };
}
```

- [ ] **Step 6: Wire the standard remark/rehype pipeline and protect KaTeX subtrees**

In `dashboard/src/components/Drawer.tsx`, add:

```ts
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
```

Import `safeKatexPluginOptions` from `../lib/mathHtml`. Add this guard above `decorateChildren`:

```ts
function hasKatexClass(child: ReactNode) {
  if (!isValidElement<{ className?: unknown }>(child)) return false;
  const className = child.props.className;
  return typeof className === "string"
    && className.split(/\s+/).some((name) => (
      name === "katex" || name === "katex-display" || name === "katex-error"
    ));
}
```

Update the recursive branch in `decorateChildren` to include
`&& !hasKatexClass(child)`. Configure React Markdown as follows:

```tsx
<ReactMarkdown
  components={components}
  rehypePlugins={[[rehypeKatex, safeKatexPluginOptions()]]}
  remarkPlugins={[
    remarkGfm,
    [remarkMath, { singleDollarTextMath: true }],
  ]}
>
  {preserveMathForMarkdown(markdown)}
</ReactMarkdown>
```

- [ ] **Step 7: Run the focused tests and verify GREEN**

Run:

```powershell
cd dashboard
npm.cmd test -- src/lib/mathHtml.test.ts src/components/Drawer.test.tsx
```

Expected: both files pass; the reported sentence produces three KaTeX roots, legacy delimiters render, code remains literal, and malformed TeX does not throw.

- [ ] **Step 8: Commit the standard pipeline**

Run:

```powershell
git add dashboard/package.json dashboard/package-lock.json dashboard/src/lib/mathHtml.ts dashboard/src/lib/mathHtml.test.ts dashboard/src/components/Drawer.tsx dashboard/src/components/Drawer.test.tsx
git diff --cached --check
git commit -m "fix(ui): render standard markdown math"
```

Expected: one focused commit containing only the six listed files.

---

### Task 2: Full regression and production verification

**Files:**
- Verify only; no planned source changes.

**Interfaces:**
- Consumes: the completed standard Markdown math pipeline from Task 1.
- Produces: verification evidence for the dashboard and visualization bridge.

- [ ] **Step 1: Run the complete dashboard test suite**

Run:

```powershell
cd dashboard
npm.cmd test
```

Expected: all Vitest files pass with zero failures.

- [ ] **Step 2: Run the visualization and dashboard Python suites**

Run from the repository root:

```powershell
$env:PYTHONPATH='src'
python -m pytest -p no:cacheprovider tests/test_viz.py dashboard/tests -q
```

Expected: all tests pass with zero failures.

- [ ] **Step 3: Build the production dashboard**

Run:

```powershell
cd dashboard
npm.cmd run build
```

Expected: TypeScript and Vite exit successfully; the output includes the existing relative asset paths for nested dashboards.

- [ ] **Step 4: Audit scope and working-tree preservation**

Run from the repository root:

```powershell
git diff --check
git status --short
git show --stat --oneline HEAD
```

Expected: no whitespace errors; the math commit contains only the six Task 1 files; the user's pre-existing unstaged research files and `artifacts/` remain present and uncommitted.
