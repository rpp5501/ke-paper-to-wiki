// scripts/mermaid_parse.mjs — exit 0 iff stdin parses as mermaid,
// exit 1 on a genuine parse failure, exit 2 if the mermaid package itself
// isn't installed (dynamic import so that case is catchable, not a crash).
// setup once: npm i mermaid (in paper-skill/)
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
  } catch { process.exit(1); }
});
