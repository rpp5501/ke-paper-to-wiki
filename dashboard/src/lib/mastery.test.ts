import { describe, expect, it } from "vitest";

import {
  MASTERY_STORAGE_KEY,
  markSeen,
  masteredCount,
  readLedger,
  recordAnswer,
  recordFor,
  reviewQueue,
  writeLedger,
  type MasteryLedger,
} from "./mastery";

const AT = new Date("2026-07-24T12:00:00.000Z");

function memoryStorage(seed: Record<string, string> = {}) {
  const data = { ...seed };
  return {
    getItem: (key: string) => data[key] ?? null,
    setItem: (key: string, value: string) => {
      data[key] = value;
    },
  };
}

describe("recordAnswer", () => {
  it("raises level and streak on a correct answer", () => {
    const ledger = recordAnswer({}, "sdpa", true, AT);

    expect(recordFor(ledger, "sdpa")).toEqual({
      level: "quizzed",
      streak: 1,
      lastAnswered: AT.toISOString(),
    });
  });

  it("earns mastered on a second consecutive correct answer", () => {
    let ledger = recordAnswer({}, "sdpa", true, AT);
    ledger = recordAnswer(ledger, "sdpa", true, AT);

    expect(recordFor(ledger, "sdpa").level).toBe("mastered");
    expect(recordFor(ledger, "sdpa").streak).toBe(2);
  });

  it("resets the streak on a wrong answer but keeps the level", () => {
    let ledger = recordAnswer({}, "sdpa", true, AT);
    ledger = recordAnswer(ledger, "sdpa", true, AT);
    ledger = recordAnswer(ledger, "sdpa", false, AT);

    // Level never falls: engagement is not un-earned by one wrong answer.
    expect(recordFor(ledger, "sdpa").level).toBe("mastered");
    expect(recordFor(ledger, "sdpa").streak).toBe(0);
  });

  it("raises a first wrong answer to quizzed, not beyond", () => {
    const ledger = recordAnswer({}, "sdpa", false, AT);

    expect(recordFor(ledger, "sdpa").level).toBe("quizzed");
    expect(recordFor(ledger, "sdpa").streak).toBe(0);
  });

  it("does not mutate the ledger it is given", () => {
    const before: MasteryLedger = {};
    recordAnswer(before, "sdpa", true, AT);

    expect(before).toEqual({});
  });
});

describe("markSeen", () => {
  it("promotes an unseen node to seen", () => {
    expect(recordFor(markSeen({}, "sdpa"), "sdpa").level).toBe("seen");
  });

  it("never lowers an existing level or touches the streak", () => {
    const answered = recordAnswer({}, "sdpa", true, AT);

    // Same object back — a no-op must not churn subscribers.
    expect(markSeen(answered, "sdpa")).toBe(answered);
  });
});

describe("ledger persistence", () => {
  it("restores a written ledger (reload)", () => {
    const storage = memoryStorage();
    const ledger = recordAnswer({}, "sdpa", true, AT);
    writeLedger(ledger, storage);

    expect(readLedger(storage)).toEqual(ledger);
  });

  it("returns an empty ledger when storage is absent or blank", () => {
    expect(readLedger(null)).toEqual({});
    expect(readLedger(memoryStorage())).toEqual({});
  });

  it("drops hand-edited entries with an unknown level", () => {
    const storage = memoryStorage({
      [MASTERY_STORAGE_KEY]: JSON.stringify({
        sdpa: { level: "godlike", streak: 99, lastAnswered: null },
        attention: { level: "quizzed", streak: 1, lastAnswered: null },
      }),
    });

    expect(Object.keys(readLedger(storage))).toEqual(["attention"]);
  });

  it("coerces a corrupt streak instead of trusting it", () => {
    const storage = memoryStorage({
      [MASTERY_STORAGE_KEY]: JSON.stringify({
        sdpa: { level: "quizzed", streak: -4, lastAnswered: 7 },
      }),
    });

    expect(readLedger(storage).sdpa).toEqual({
      level: "quizzed",
      streak: 0,
      lastAnswered: null,
    });
  });

  it("survives malformed JSON", () => {
    expect(readLedger(memoryStorage({ [MASTERY_STORAGE_KEY]: "{oops" }))).toEqual({});
  });
});

describe("reviewQueue", () => {
  const NOW = new Date("2026-07-24T12:00:00.000Z");
  const daysAgo = (n: number) =>
    new Date(NOW.getTime() - n * 24 * 60 * 60 * 1000).toISOString();

  function entry(streak: number, lastAnswered: string | null) {
    return { level: "quizzed" as const, streak, lastAnswered };
  }

  it("queues a node whose streak just broke", () => {
    const ledger: MasteryLedger = { sdpa: entry(0, daysAgo(0)) };

    expect(reviewQueue(ledger, NOW)).toEqual(["sdpa"]);
  });

  it("queues correct-but-stale evidence past the window", () => {
    const ledger: MasteryLedger = {
      fresh: entry(3, daysAgo(13)),
      stale: entry(3, daysAgo(15)),
    };

    expect(reviewQueue(ledger, NOW)).toEqual(["stale"]);
  });

  it("leaves never-answered nodes out entirely", () => {
    // They have streak 0 too — queueing them would mean the whole graph.
    const ledger: MasteryLedger = {
      untouched: { level: "seen", streak: 0, lastAnswered: null },
      answered: entry(0, daysAgo(1)),
    };

    expect(reviewQueue(ledger, NOW)).toEqual(["answered"]);
  });

  it("returns an empty queue when everything is fresh", () => {
    expect(reviewQueue({ sdpa: entry(2, daysAgo(1)) }, NOW)).toEqual([]);
    expect(reviewQueue({}, NOW)).toEqual([]);
  });

  it("ignores an unparseable timestamp rather than queueing on NaN", () => {
    expect(reviewQueue({ sdpa: entry(2, "not-a-date") }, NOW)).toEqual([]);
  });

  it("honours a caller-supplied window", () => {
    const ledger: MasteryLedger = { sdpa: entry(3, daysAgo(5)) };

    expect(reviewQueue(ledger, NOW, 14)).toEqual([]);
    expect(reviewQueue(ledger, NOW, 3)).toEqual(["sdpa"]);
  });
});

describe("masteredCount", () => {
  it("counts only mastered nodes", () => {
    let ledger = recordAnswer({}, "sdpa", true, AT);
    ledger = recordAnswer(ledger, "sdpa", true, AT);
    ledger = recordAnswer(ledger, "attention", true, AT);
    ledger = markSeen(ledger, "softmax");

    expect(masteredCount(ledger)).toBe(1);
  });
});
