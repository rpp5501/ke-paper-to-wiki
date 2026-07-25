// R15.1 — typed access to the optional KE_DATA.nextSteps list.
// A build without --next-steps has no key; every consumer goes through here.
import { KE_DATA } from "../data.gen";

export type NextStep = {
  title: string;
  rationale: string;
  kind: string;
  nodes: string[];
  sources: string[];
  confirmed: boolean;
};

export function nextStepsFrom(data: unknown): NextStep[] {
  const steps = (data as { nextSteps?: NextStep[] }).nextSteps;
  return steps ?? [];
}

const NEXT_STEPS = nextStepsFrom(KE_DATA);

export function getNextSteps(): NextStep[] {
  return NEXT_STEPS;
}
