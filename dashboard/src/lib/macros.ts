// Typed access to the optional KE_DATA.macros table — the paper's own \newcommand
// definitions, lifted from its preamble by latex_pack.
//
// p4_write reproduces equations VERBATIM from the pack (equation_fidelity
// "exact"), so a paper's private notation travels with them. Without the table
// KaTeX throws on the first unknown control sequence and renderMathToString
// falls back to printing raw source: the reader sees "\doo" where the paper
// means "do". A build without --pack has no `macros` key; consumers go through
// here, same as lib/source.ts.
import { KE_DATA } from "../data.gen";

/** A control sequence: a backslash followed by at least one letter. */
const CONTROL_SEQUENCE = /^\\[A-Za-z@]+$/;

/** localStorage is not the only untrusted input — the bundle is generated, but
 *  a malformed entry would make KaTeX throw for every equation on the page
 *  rather than just its own, so bad entries are dropped, not passed through. */
export function sanitizeMacros(
  raw: Record<string, unknown> | undefined | null,
): Record<string, string> {
  if (!raw || typeof raw !== "object") return {};
  const out: Record<string, string> = {};
  for (const [name, body] of Object.entries(raw)) {
    if (CONTROL_SEQUENCE.test(name) && typeof body === "string") {
      out[name] = body;
    }
  }
  return out;
}

const MACROS = sanitizeMacros(
  (KE_DATA as { macros?: Record<string, unknown> }).macros,
);

export function katexMacros(): Record<string, string> {
  return MACROS;
}
