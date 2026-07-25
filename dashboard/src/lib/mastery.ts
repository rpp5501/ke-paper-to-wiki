// R16.A1 — the mastery ledger: evidence of understanding per node, gathered
// from quiz answers and R13 viz bet outcomes (the two feed one ledger — that
// is the R13 fold). Deliberately not a score: no points, no XP, no
// leaderboard. Levels only ever climb, so a wrong answer never erases that
// the learner engaged; the streak is the part that decays, and a zeroed
// streak is what surfaces a node for review.
import {
  browserStorage,
  readJSON,
  writeJSON,
  type StorageLike,
} from "./persist";

export type MasteryLevel = "unseen" | "seen" | "quizzed" | "mastered";
export type MasteryRecord = {
  level: MasteryLevel;
  streak: number;
  lastAnswered: string | null;
};
export type MasteryLedger = Record<string, MasteryRecord>;

export const MASTERY_STORAGE_KEY = "paper-dashboard.mastery.v1";

/** Consecutive correct answers that earn "mastered". */
export const MASTERY_STREAK = 2;

export const LEVELS: MasteryLevel[] = ["unseen", "seen", "quizzed", "mastered"];

export const EMPTY_RECORD: MasteryRecord = {
  level: "unseen",
  streak: 0,
  lastAnswered: null,
};

function rank(level: MasteryLevel): number {
  return LEVELS.indexOf(level);
}

export function higherLevel(a: MasteryLevel, b: MasteryLevel): MasteryLevel {
  return rank(a) >= rank(b) ? a : b;
}

export function recordFor(ledger: MasteryLedger, nodeId: string): MasteryRecord {
  return ledger[nodeId] ?? EMPTY_RECORD;
}

/** Node was opened — the weakest evidence there is. Never lowers a level. */
export function markSeen(ledger: MasteryLedger, nodeId: string): MasteryLedger {
  const previous = recordFor(ledger, nodeId);
  if (rank(previous.level) >= rank("seen")) return ledger;

  return { ...ledger, [nodeId]: { ...previous, level: "seen" } };
}

/** One graded answer: a quiz item or a resolved viz bet. */
export function recordAnswer(
  ledger: MasteryLedger,
  nodeId: string,
  correct: boolean,
  now: Date = new Date(),
): MasteryLedger {
  const previous = recordFor(ledger, nodeId);
  const streak = correct ? previous.streak + 1 : 0;
  const earned: MasteryLevel = streak >= MASTERY_STREAK ? "mastered" : "quizzed";

  return {
    ...ledger,
    [nodeId]: {
      level: higherLevel(previous.level, earned),
      streak,
      lastAnswered: now.toISOString(),
    },
  };
}

export function masteredCount(ledger: MasteryLedger): number {
  return Object.values(ledger).filter((r) => r.level === "mastered").length;
}

/** Days after which correct-but-old evidence is worth revisiting. */
export const REVIEW_AFTER_DAYS = 14;

// R16.A3 — nodes whose evidence just broke (streak reset) or has gone stale.
// Only answered nodes qualify: an untouched node has streak 0 too, and
// queueing the whole graph for "review" would be meaningless. Plain date
// math, no scheduler and no notifications — Anki export stays the heavy-SRS
// path.
export function reviewQueue(
  ledger: MasteryLedger,
  now: Date = new Date(),
  staleDays: number = REVIEW_AFTER_DAYS,
): string[] {
  const cutoff = now.getTime() - staleDays * 24 * 60 * 60 * 1000;

  return Object.entries(ledger)
    .filter(([, record]) => {
      if (record.lastAnswered === null) return false;
      if (record.streak === 0) return true;

      const answeredAt = Date.parse(record.lastAnswered);
      return Number.isFinite(answeredAt) && answeredAt < cutoff;
    })
    .map(([nodeId]) => nodeId)
    .sort();
}

export function readLedger(
  storage: StorageLike | null | undefined = browserStorage(),
): MasteryLedger {
  const raw = readJSON(storage, MASTERY_STORAGE_KEY);
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return {};

  const ledger: MasteryLedger = {};
  for (const [nodeId, value] of Object.entries(raw as Record<string, unknown>)) {
    if (!value || typeof value !== "object") continue;

    const record = value as Partial<MasteryRecord>;
    // An unknown level means a ledger written by a future (or hand-edited)
    // build — drop the entry rather than let it leak into level comparisons.
    if (!LEVELS.includes(record.level as MasteryLevel)) continue;

    ledger[nodeId] = {
      level: record.level as MasteryLevel,
      streak: typeof record.streak === "number" && Number.isFinite(record.streak)
        ? Math.max(0, Math.round(record.streak))
        : 0,
      lastAnswered: typeof record.lastAnswered === "string"
        ? record.lastAnswered
        : null,
    };
  }
  return ledger;
}

export function writeLedger(
  ledger: MasteryLedger,
  storage: StorageLike | null | undefined = browserStorage(),
): void {
  writeJSON(storage, MASTERY_STORAGE_KEY, ledger);
}
