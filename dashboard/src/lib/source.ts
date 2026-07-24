// R15.11 show-source — typed access to the optional KE_DATA.sections map.
// A build without --pack has no `sections` key; every consumer goes through here.
import { KE_DATA } from "../data.gen";

export type SourceSection = { title: string; text: string };

/** TS port of build_data.py's `section_key` — joins pack ids such as
 *  `sec_3_2_1` to graph refs such as `sec:3.2.1`. Same test vectors both sides. */
export function sectionKey(value: string | null | undefined): string {
  const cleaned = String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/§/g, "")
    .replace(/^sec(?:tion)?[:._-]*/, "");
  return (cleaned.match(/\d+|[a-z]+/g) ?? []).join(".");
}

export function sectionFor(
  sourceRef: string | null | undefined,
  sections: Record<string, SourceSection>,
): ({ ref: string } & SourceSection) | undefined {
  const ref = sectionKey(sourceRef);
  const section = ref ? sections[ref] : undefined;
  return section ? { ref, ...section } : undefined;
}

const SECTIONS = (KE_DATA as { sections?: Record<string, SourceSection> })
  .sections ?? {};

export function getSections(): Record<string, SourceSection> {
  return SECTIONS;
}
