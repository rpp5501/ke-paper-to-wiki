// Select-to-look-up: highlight a phrase, get what the bundle knows about it.
// The hover glossary only fires on terms someone wrote a note for, so this is
// the answer for the ones it missed.
//
// Behavioural shell only. The cascade is lib/lookup.ts and the markup is
// LookupPopover, both pure and tested; what lives here is the DOM wiring that
// vitest's `environment: "node"` cannot exercise.
import { useEffect, useState } from "react";

import { KE_DATA } from "../data.gen";
import { insideKnownTerm, lookup, type LookupData, type LookupResult } from "../lib/lookup";
import { getSections } from "../lib/source";
import type { KENode } from "../types";
import LookupPopover from "./LookupPopover";

const NODES = KE_DATA.nodes as KENode[];
const PAGES = KE_DATA.pages as Record<string, string>;

/** The page's first line of TL;DR — what the tour already uses to describe a
 *  concept in one sentence. */
function tldrOf(nodeId: string): string {
  const body = PAGES[nodeId] ?? "";
  const after = body.split("{#tldr}")[1] ?? "";
  return after.split(/\n#{2,}/)[0].trim().split("\n\n")[0]?.trim() ?? "";
}

type Anchor = { phrase: string; result: LookupResult | null; x: number; y: number };

export default function SelectionLookup({
  glossary,
  onOpenConcept,
}: {
  glossary: Record<string, string>;
  onOpenConcept?: (nodeId: string) => void;
}) {
  const [anchor, setAnchor] = useState<Anchor | null>(null);

  useEffect(() => {
    function offerLookup(event: Event) {
      // A click inside the popover is not a new selection: without this,
      // dismissing it re-opened it on the same still-selected phrase.
      if ((event.target as Element | null)?.closest?.(".lookup-popover")) return;
      const selection = window.getSelection();
      const phrase = selection?.toString() ?? "";
      if (!phrase.trim() || selection?.isCollapsed) {
        setAnchor(null);
        return;
      }
      // Defer to the hover rather than stack a second explanation on it.
      if (insideKnownTerm(phrase, glossary)) {
        setAnchor(null);
        return;
      }
      const data: LookupData = {
        glossary,
        nodes: NODES.map((n) => ({ id: n.id, label: n.label, tldr: tldrOf(n.id) })),
        sections: getSections(),
      };
      const result = lookup(phrase, data);
      // Nothing to say, so say nothing. The anchor used to be set even when
      // the cascade returned null, which put a "No entry for …" dialog on
      // screen every time anyone highlighted a word to copy it.
      if (result === null) {
        setAnchor(null);
        return;
      }
      const box = selection?.getRangeAt(0).getBoundingClientRect();
      setAnchor({
        phrase: phrase.trim(),
        result,
        x: box?.left ?? 0,
        y: (box?.bottom ?? 0) + window.scrollY,
      });
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setAnchor(null);
    }

    // selectionchange fires on every mousemove of a drag, so the popover used
    // to appear and chase the cursor while the reader was still choosing what
    // to highlight. It now only clears here; the offer waits for the gesture
    // to finish.
    function clearWhenSelectionGoes() {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed || !selection.toString().trim()) {
        setAnchor(null);
      }
    }

    document.addEventListener("selectionchange", clearWhenSelectionGoes);
    document.addEventListener("mouseup", offerLookup);
    document.addEventListener("keyup", offerLookup);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("selectionchange", clearWhenSelectionGoes);
      document.removeEventListener("mouseup", offerLookup);
      document.removeEventListener("keyup", offerLookup);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [glossary]);

  if (!anchor) return null;

  return (
    <div
      className="lookup-anchor"
      style={{ left: anchor.x, position: "absolute", top: anchor.y }}
    >
      <LookupPopover
        onDismiss={() => setAnchor(null)}
        onOpenConcept={onOpenConcept}
        phrase={anchor.phrase}
        result={anchor.result}
      />
    </div>
  );
}
