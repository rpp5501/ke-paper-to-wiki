import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { Chapter } from "../lib/article";
import type { MasteryLedger } from "../lib/mastery";
import { ProgressRailPresentation } from "./ProgressRail";

const chapters: Chapter[] = [
  { nodeId: "sdpa", title: "Scaled dot-product attention", tiers: [], sections: [], checkpointIds: [] },
  { nodeId: "softmax", title: "Softmax", tiers: [], sections: [], checkpointIds: [] },
];

function render(mastery: MasteryLedger) {
  return renderToStaticMarkup(
    <ProgressRailPresentation
      chapters={chapters}
      completedSteps={new Set()}
      hasClosing={false}
      hasNotation={false}
      learnIdx={null}
      mastery={mastery}
      onExplore={() => undefined}
      onJump={() => undefined}
    />,
  );
}

function ledger(level: string): MasteryLedger {
  return {
    sdpa: {
      level: level as MasteryLedger[string]["level"],
      read: false,
      streak: 0,
      lastAnswered: null,
      evidenceIds: [],
    },
  };
}

describe("ProgressRailPresentation mastery ring", () => {
  it.each(["reading", "read", "practiced", "mastered"])(
    "marks a %s step so the ring can grow with the evidence",
    (level) => {
      const markup = render(ledger(level));

      expect(markup).toContain(`data-mastery="${level}"`);
      // The ring is decorative; the level still has to reach a screen reader.
      expect(markup).toContain(`<span class="sr-only">${level}</span>`);
    },
  );

  it("leaves unseen steps unmarked so the rail stays quiet by default", () => {
    const markup = render({});

    expect(markup).not.toContain("data-mastery");
    expect(markup).not.toContain("sr-only");
  });

  it("marks only the step that has evidence", () => {
    const markup = render(ledger("mastered"));

    expect(markup.match(/data-mastery/g)).toHaveLength(1);
  });

  it("still renders the reading count and chapter titles", () => {
    const markup = render(ledger("mastered"));

    expect(markup).toContain("0 of 2 read");
    expect(markup).toContain("Scaled dot-product attention");
    expect(markup).toContain("Softmax");
  });

  it("restores sentinel-backed read progress independently of practice", () => {
    const persisted = ledger("practiced");
    persisted.sdpa.read = true;

    const markup = render(persisted);

    expect(markup).toContain("1 of 2 read");
    expect(markup).toContain('class="rail-status">Practiced');
  });
});
