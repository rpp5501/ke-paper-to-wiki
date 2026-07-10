// scripts/mermaid_parse.mjs — exit 0 iff stdin parses as mermaid
// setup once: npm i mermaid (in paper-skill/)
import mermaid from "mermaid";
const chunks = [];
process.stdin.on("data", c => chunks.push(c));
process.stdin.on("end", async () => {
  try {
    await mermaid.parse(chunks.join(""));
    process.exit(0);
  } catch { process.exit(1); }
});
