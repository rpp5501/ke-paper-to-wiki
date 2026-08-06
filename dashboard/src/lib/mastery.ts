// The mastery ledger records learner evidence per concept. It is deliberately
// not a score: reading and assessment are separate, and a wrong answer revokes
// mastery until two new, distinct application successes are recorded.
import {
  browserStorage,
  readJSON,
  writeJSON,
  type StorageLike,
} from "./persist";

export type MasteryLevel =
  | "unseen"
  | "reading"
  | "read"
  | "practiced"
  | "mastered";
export type MasteryEvidenceKind =
  | "prediction"
  | "application"
  | "debug"
  | "interpretation"
  | "viz";
export type MasteryRecord = {
  level: MasteryLevel;
  /** True only after the guided route's end-of-chapter sentinel. */
  read: boolean;
  streak: number;
  lastAnswered: string | null;
  /** Distinct, correct application checkpoints since the latest wrong answer. */
  evidenceIds: string[];
};
export type MasteryLedger = Record<string, MasteryRecord>;

// v1 could not distinguish application evidence from ordinary quiz answers.
// Starting a new ledger avoids displaying unverified legacy mastery as proof.
export const MASTERY_STORAGE_KEY = "paper-dashboard.mastery.v2";

/** Distinct application-level successes required for mastery. */
export const MASTERY_STREAK = 2;

export const LEVELS: MasteryLevel[] = [
  "unseen", "reading", "read", "practiced", "mastered",
];

export const EMPTY_RECORD: MasteryRecord = {
  level: "unseen",
  read: false,
  streak: 0,
  lastAnswered: null,
  evidenceIds: [],
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

function promote(
  ledger: MasteryLedger,
  nodeId: string,
  level: MasteryLevel,
): MasteryLedger {
  const previous = recordFor(ledger, nodeId);
  if (rank(previous.level) >= rank(level)) return ledger;
  return { ...ledger, [nodeId]: { ...previous, level } };
}

/** The learner has entered a concept; this is not evidence that it was read. */
export function markReading(ledger: MasteryLedger, nodeId: string): MasteryLedger {
  return promote(ledger, nodeId, "reading");
}

/** The guided route's end-of-chapter sentinel was reached. */
export function markRead(ledger: MasteryLedger, nodeId: string): MasteryLedger {
  const previous = recordFor(ledger, nodeId);
  if (previous.read && rank(previous.level) >= rank("read")) return ledger;
  return {
    ...ledger,
    [nodeId]: {
      ...previous,
      level: higherLevel(previous.level, "read"),
      read: true,
    },
  };
}

/**
 * One graded answer. Only `application` checkpoints can add mastery evidence;
 * the other interactions still show meaningful practice without minting a
 * mastery badge. Missing kinds deliberately behave as non-application legacy
 * answers, so callers must classify new assessment content explicitly.
 */
export function recordAnswer(
  ledger: MasteryLedger,
  nodeId: string,
  correct: boolean,
  now: Date = new Date(),
  evidenceId?: string,
  kind: MasteryEvidenceKind = "prediction",
): MasteryLedger {
  const previous = recordFor(ledger, nodeId);
  const streak = correct ? previous.streak + 1 : 0;
  const evidenceIds = !correct
    ? []
    : kind === "application" && evidenceId
      ? [...new Set([...previous.evidenceIds, evidenceId])]
      : previous.evidenceIds;
  const earned: MasteryLevel = evidenceIds.length >= MASTERY_STREAK
    ? "mastered"
    : "practiced";

  return {
    ...ledger,
    [nodeId]: {
      level: correct ? higherLevel(previous.level, earned) : "practiced",
      read: previous.read,
      streak,
      lastAnswered: now.toISOString(),
      evidenceIds,
    },
  };
}

export function masteredCount(ledger: MasteryLedger): number {
  return Object.values(ledger).filter((record) => record.level === "mastered").length;
}

/** Days after which correct-but-old evidence is worth revisiting. */
export const REVIEW_AFTER_DAYS = 14;

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
    if (!LEVELS.includes(record.level as MasteryLevel)) continue;

    ledger[nodeId] = {
      level: record.level as MasteryLevel,
      read: record.read === true || record.level === "read",
      streak: typeof record.streak === "number" && Number.isFinite(record.streak)
        ? Math.max(0, Math.round(record.streak))
        : 0,
      lastAnswered: typeof record.lastAnswered === "string"
        ? record.lastAnswered
        : null,
      evidenceIds: Array.isArray(record.evidenceIds)
        ? [...new Set(record.evidenceIds.filter(
          (value): value is string => typeof value === "string" && value.length > 0,
        ))]
        : [],
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
