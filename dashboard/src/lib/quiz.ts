// R15.2 — typed access to the optional KE_DATA.quiz list.
// A build without --quiz has no key; every consumer goes through here.
import { KE_DATA } from "../data.gen";

export type QuizOption = { text: string; explain: string };

export type QuizItem = {
  id: string;
  nodeId: string;
  prompt: string;
  options: QuizOption[];
  correct: number;
  sourceRef: string;
};

export function quizFrom(data: unknown): QuizItem[] {
  const quiz = (data as { quiz?: QuizItem[] }).quiz;
  return quiz ?? [];
}

const QUIZ = quizFrom(KE_DATA);

export function getQuiz(): QuizItem[] {
  return QUIZ;
}
