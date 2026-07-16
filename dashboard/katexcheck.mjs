// Validate every $...$ / $$...$$ block in the given markdown files through
// KaTeX in the same strict mode the app uses (throwOnError). Exit non-zero on
// any failure. Usage: node katexcheck.mjs <file.md> [file.md ...]
import katex from "katex";
import { readFileSync } from "node:fs";

const files = process.argv.slice(2);
let total = 0, failures = 0;

function blocks(src) {
  const out = [];
  // display math $$...$$
  for (const m of src.matchAll(/\$\$([\s\S]+?)\$\$/g)) out.push([m[1], true]);
  const noDisplay = src.replace(/\$\$[\s\S]+?\$\$/g, "");
  // inline math $...$ (skip escaped \$)
  for (const m of noDisplay.matchAll(/(?<!\\)\$([^$\n]+?)(?<!\\)\$/g))
    out.push([m[1], false]);
  return out;
}

for (const file of files) {
  const src = readFileSync(file, "utf8");
  for (const [tex, displayMode] of blocks(src)) {
    total++;
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
