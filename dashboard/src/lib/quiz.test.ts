import { describe, expect, it } from "vitest";

import { quizFrom, type QuizItem } from "./quiz";

const current: QuizItem = {
  id: "current",
  nodeId: "sid",
  prompt: "Apply SID",
  options: [{ text: "A", explain: "Because" }],
  correct: 0,
  sourceRef: "#mechanics",
};

const legacy: QuizItem = { ...current, id: "legacy" };

describe("quizFrom", () => {
  it("prefers v2 checkpoints over the legacy quiz alias", () => {
    expect(quizFrom({ checkpoints: [current], quiz: [legacy] })).toEqual([current]);
  });

  it("supports the quiz alias for one compatibility cycle", () => {
    expect(quizFrom({ quiz: [legacy] })).toEqual([legacy]);
  });
});
