// Validate every math expression in the given markdown files through KaTeX
// in the same strict mode the app uses (throwOnError): $...$, $$...$$,
// \(...\), \[...\], plus the LaTeX inside `annotated-eq` and `derivation`
// fenced content blocks. Exit non-zero on any failure.
// Usage: node katexcheck.mjs <file.md> [file.md ...]
import katex from "katex";
import { readFileSync } from "node:fs";
import { parse as parseYaml } from "yaml";

const files = process.argv.slice(2);
let total = 0, failures = 0;

function blocks(src) {
  const out = [];
  // fenced content blocks with LaTeX payloads (checked, then stripped so the
  // generic matchers below don't re-scan their bodies)
  const fence = /^```(annotated-eq|derivation)\r?\n([\s\S]*?)\r?\n```$/gm;
  for (const m of src.matchAll(fence)) {
    try {
      const data = parseYaml(m[2]);
      if (m[1] === "annotated-eq") {
        if (typeof data?.latex === "string") out.push([data.latex, true]);
        for (const term of data?.terms ?? []) {
          if (typeof term?.tex === "string") out.push([term.tex, false]);
        }
      } else {
        for (const step of data?.steps ?? []) {
          if (typeof step?.latex === "string") out.push([step.latex, true]);
        }
      }
    } catch (e) {
      out.push([null, `content-block ${m[1]}: invalid YAML :: ${String(e.message)}`]);
    }
  }
  let text = src.replace(/^```[\w-]+\r?\n[\s\S]*?\r?\n```$/gm, "");
  // display math $$...$$ and \[...\]
  for (const m of text.matchAll(/\$\$([\s\S]+?)\$\$/g)) out.push([m[1], true]);
  for (const m of text.matchAll(/\\\[([\s\S]+?)\\\]/g)) out.push([m[1], true]);
  text = text.replace(/\$\$[\s\S]+?\$\$/g, "").replace(/\\\[[\s\S]+?\\\]/g, "");
  // inline math \(...\) and $...$ (skip escaped \$)
  for (const m of text.matchAll(/\\\(([\s\S]+?)\\\)/g)) out.push([m[1], false]);
  text = text.replace(/\\\([\s\S]+?\\\)/g, "");
  for (const m of text.matchAll(/(?<!\\)\$([^$\n]+?)(?<!\\)\$/g))
    out.push([m[1], false]);
  return out;
}

for (const file of files) {
  const src = readFileSync(file, "utf8");
  for (const [tex, displayMode] of blocks(src)) {
    total++;
    if (tex === null) {
      failures++;
      console.error(`FAIL ${file}: ${displayMode}`);
      continue;
    }
    try {
      katex.renderToString(tex, { displayMode, throwOnError: true, strict: "error" });
    } catch (e) {
      failures++;
      console.error(`FAIL ${file}: ${tex.slice(0, 60)} :: ${String(e.message).slice(0, 120)}`);
    }
  }
}
console.log(`katex: ${total} blocks, ${failures} failures`);
process.exit(failures ? 1 : 0);
