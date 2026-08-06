// scripts/mermaid_parse.mjs — exit 0 iff stdin parses as mermaid,
// exit 1 on a genuine parse failure, exit 2 when the check cannot run here.
// setup once: npm i mermaid (in paper-skill/). Note that installing it is not
// sufficient on its own: mermaid >= 11 needs a browser DOM, so under bare node
// every input reports 2 (skipped) until a DOM (jsdom or similar) is supplied.
// Until then the real check on a diagram is the dashboard, which renders it
// and falls back to showing the source when it will not parse.
const chunks = [];
process.stdin.on("data", c => chunks.push(c));
process.stdin.on("end", async () => {
  let mermaid;
  try {
    ({ default: mermaid } = await import("mermaid"));
  } catch {
    process.exit(2);
  }
  try {
    await mermaid.parse(chunks.join(""));
    process.exit(0);
  } catch (err) {
    // mermaid >= 11 initialises DOMPurify against a browser DOM, so under bare
    // node it dies with "purify.addHook is not a function" before it ever looks
    // at the diagram. That is this machine failing to run the check, not the
    // author writing a bad graph -- and exit 1 is blocking, so calling it a
    // parse failure would fail every page that carries a valid diagram.
    // A grammar error arrives as mermaid's own parse error, never a TypeError.
    if (err instanceof TypeError) process.exit(2);
    process.exit(1);
  }
});
