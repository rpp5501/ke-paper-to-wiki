import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { QuizItem } from "../lib/quiz";
import { InlineCheckpointPresentation } from "./InlineCheckpoint";

const item: QuizItem = {
  id: "sid-application-1",
  nodeId: "structural-intervention-distance",
  chapterId: "what-sid-measures",
  kind: "application",
  placement: "chapter-end",
  prompt: "Which ordered pair contributes one SID error?",
  options: [
    { text: "Pair A", explain: "Correct because adjustment fails." },
    { text: "Pair B", explain: "This intervention remains valid." },
  ],
  correct: 0,
  sourceRef: "#the-math",
};

describe("InlineCheckpointPresentation", () => {
  it("frames the check as optional and leaves the next chapter unlocked", () => {
    const markup = renderToStaticMarkup(
      <InlineCheckpointPresentation
        answer={null}
        item={item}
        onAnswer={() => {}}
        onGoToNode={() => {}}
      />,
    );

    expect(markup).toContain("Optional application check");
    expect(markup).toContain("Which ordered pair");
    expect(markup).toContain("Skip it and keep reading");
  });
});
