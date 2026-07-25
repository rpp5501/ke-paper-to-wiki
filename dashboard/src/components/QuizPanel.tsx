// R15.2 — the Quiz panel: build-time authored items, graded offline in the
// browser (no runtime LLM, ever). Answering all of a node's items correctly
// marks that learn step complete. Renders nothing on a build without --quiz.
import { useState } from "react";

import { getQuiz, type QuizItem } from "../lib/quiz";
import { useApp } from "../store";
import SourceChip from "./SourceChip";
import { useNodeNavigation } from "./useNodeNavigation";

export type QuizItemViewProps = {
  answer: number | null;
  item: QuizItem;
  onAnswer: (index: number) => void;
  onGoToNode: (nodeId: string) => void;
};

export function QuizItemView({
  answer,
  item,
  onAnswer,
  onGoToNode,
}: QuizItemViewProps) {
  const answered = answer !== null;
  return (
    <li className="quiz-item">
      <div className="quiz-head">
        <span className="quiz-prompt">{item.prompt}</span>
        <button
          className="quiz-node"
          onClick={() => onGoToNode(item.nodeId)}
          title="Open this concept"
          type="button"
        >
          {item.nodeId}
        </button>
        {/* R16.C2 — provenance after the commit, never before: the section
            heading would give the answer away. */}
        {answered && (
          <SourceChip
            onOpen={() => onGoToNode(item.nodeId)}
            sourceRef={item.sectionRef}
          />
        )}
      </div>
      <ul className="quiz-options">
        {item.options.map((option, index) => {
          const isCorrect = index === item.correct;
          const isPicked = index === answer;
          const cls = !answered
            ? ""
            : isCorrect
              ? "correct"
              : isPicked
                ? "wrong"
                : "dim";
          return (
            <li key={option.text}>
              <button
                className={`quiz-option ${cls}`}
                disabled={answered}
                onClick={() => onAnswer(index)}
                type="button"
              >
                {option.text}
              </button>
              {answered && (isPicked || isCorrect) && (
                <p className="quiz-explain">{option.explain}</p>
              )}
            </li>
          );
        })}
      </ul>
    </li>
  );
}

export default function QuizPanel() {
  // Open state lives in the store so the review queue can open the quiz.
  const open = useApp((state) => state.quizOpen);
  const setOpen = useApp((state) => state.setQuizOpen);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const markStepComplete = useApp((state) => state.markStepComplete);
  const recordMastery = useApp((state) => state.recordMastery);
  const goToNode = useNodeNavigation();
  const items = getQuiz();

  if (items.length === 0) return null;

  const answeredCount = Object.keys(answers).length;
  const correctCount = items.filter(
    (item) => answers[item.id] === item.correct,
  ).length;

  const onAnswer = (item: QuizItem, index: number) => {
    const next = { ...answers, [item.id]: index };
    setAnswers(next);
    recordMastery(item.nodeId, index === item.correct);
    const nodeItems = items.filter((i) => i.nodeId === item.nodeId);
    if (nodeItems.every((i) => next[i.id] === i.correct)) {
      markStepComplete(item.nodeId);
    }
  };

  return (
    <div className="quiz-panel">
      <button
        aria-expanded={open}
        aria-haspopup="true"
        className="quiz-toggle"
        onClick={() => setOpen(!open)}
        type="button"
      >
        Quiz ({items.length})
      </button>
      {open && (
        <div className="quiz-pop">
          <p className="quiz-score" role="status">
            {answeredCount}/{items.length} answered · {correctCount} correct
          </p>
          <ul aria-label="Check your understanding" className="quiz-list">
            {items.map((item) => (
              <QuizItemView
                answer={answers[item.id] ?? null}
                item={item}
                key={item.id}
                onAnswer={(index) => onAnswer(item, index)}
                onGoToNode={(nodeId) => {
                  goToNode(nodeId);
                  setOpen(false);
                }}
              />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
