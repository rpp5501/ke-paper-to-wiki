import { useState } from "react";

import type { QuizItem } from "../lib/quiz";
import { useApp } from "../store";
import { QuizItemView } from "./QuizPanel";
import { useNodeNavigation } from "./useNodeNavigation";

export function InlineCheckpointPresentation({
  answer,
  item,
  onAnswer,
  onGoToNode,
}: {
  answer: number | null;
  item: QuizItem;
  onAnswer: (index: number) => void;
  onGoToNode: (nodeId: string) => void;
}) {
  return (
    <aside className="inline-checkpoint">
      <div className="checkpoint-heading">
        <p className="checkpoint-eyebrow">
          Optional {item.kind ?? "interpretation"} check
        </p>
        <p className="checkpoint-skip">Skip it and keep reading; mastery waits.</p>
      </div>
      <ol className="quiz-list">
        <QuizItemView
          answer={answer}
          item={item}
          onAnswer={onAnswer}
          onGoToNode={onGoToNode}
        />
      </ol>
    </aside>
  );
}

export default function InlineCheckpoint({ item }: { item: QuizItem }) {
  const [answer, setAnswer] = useState<number | null>(null);
  const recordMastery = useApp((state) => state.recordMastery);
  const goToNode = useNodeNavigation();
  return (
    <InlineCheckpointPresentation
      answer={answer}
      item={item}
      onAnswer={(index) => {
        setAnswer(index);
        recordMastery(
          item.nodeId,
          index === item.correct,
          item.id,
          item.kind ?? "prediction",
        );
      }}
      onGoToNode={goToNode}
    />
  );
}
