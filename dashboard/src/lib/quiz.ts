// V2 reads the checkpoint contract; `quiz` remains a one-cycle legacy alias.
// A build without --quiz has neither key, so every consumer goes through here.
import { KE_DATA } from "../data.gen";

export type QuizOption = { text: string; explain: string };

export type QuizItem = {
  id: string;
  nodeId: string;
  chapterId?: string;
  kind?: "prediction" | "application" | "debug" | "interpretation";
  placement?: "after-intuition" | "after-mechanics" | "chapter-end";
  prompt: string;
  options: QuizOption[];
  correct: number;
  /** R15.2 in-page anchor, e.g. '#the-math'. */
  sourceRef: string;
  /** R16.C2 paper-span ref, validated at build time against KE_DATA.sections. */
  sectionRef?: string;
};

export function quizFrom(data: unknown): QuizItem[] {
  const bundle = data as { checkpoints?: QuizItem[]; quiz?: QuizItem[] };
  return bundle.checkpoints ?? bundle.quiz ?? [];
}

const QUIZ = quizFrom(KE_DATA);

export function getQuiz(): QuizItem[] {
  return QUIZ;
}
