import { describe, expect, it } from "vitest";

import {
  MASTERY_STORAGE_KEY,
  markRead,
  markReading,
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
  it("records a correct application as practice before mastery", () => {
    const ledger = recordAnswer(
      {}, "sdpa", true, AT, "checkpoint-1", "application",
    );

    expect(recordFor(ledger, "sdpa")).toEqual({
      level: "practiced",
      read: false,
      streak: 1,
      lastAnswered: AT.toISOString(),
      evidenceIds: ["checkpoint-1"],
    });
  });

  it("earns mastered only after two distinct correct applications", () => {
    let ledger = recordAnswer(
      {}, "sdpa", true, AT, "checkpoint-1", "application",
    );
    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "checkpoint-2", "application",
    );

    expect(recordFor(ledger, "sdpa").level).toBe("mastered");
    expect(recordFor(ledger, "sdpa").streak).toBe(2);
  });

  it("does not count repeated applications as distinct mastery evidence", () => {
    let ledger = recordAnswer(
      {}, "sdpa", true, AT, "checkpoint-1", "application",
    );
    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "checkpoint-1", "application",
    );

    expect(recordFor(ledger, "sdpa").level).toBe("practiced");

    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "checkpoint-2", "application",
    );
    expect(recordFor(ledger, "sdpa").level).toBe("mastered");
  });

  it.each(["prediction", "interpretation", "debug", "viz"] as const)(
    "treats a correct %s response as practice, not mastery evidence",
    (kind) => {
      let ledger = recordAnswer({}, "sdpa", true, AT, "one", kind);
      ledger = recordAnswer(ledger, "sdpa", true, AT, "two", kind);

      expect(recordFor(ledger, "sdpa")).toMatchObject({
        level: "practiced",
        evidenceIds: [],
      });
    },
  );

  it("does not let an unclassified answer award mastery", () => {
    let ledger = recordAnswer({}, "sdpa", true, AT, "one");
    ledger = recordAnswer(ledger, "sdpa", true, AT, "two");

    expect(recordFor(ledger, "sdpa").level).toBe("practiced");
  });

  it("requires two new distinct applications after the most recent wrong answer", () => {
    let ledger = recordAnswer(
      {}, "sdpa", true, AT, "checkpoint-1", "application",
    );
    ledger = recordAnswer(
      ledger, "sdpa", false, AT, "checkpoint-1", "application",
    );
    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "checkpoint-2", "application",
    );

    expect(recordFor(ledger, "sdpa").level).toBe("practiced");

    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "checkpoint-3", "application",
    );
    expect(recordFor(ledger, "sdpa").level).toBe("mastered");
  });

  it("demotes mastery and resets evidence on a wrong answer", () => {
    let ledger = recordAnswer(
      {}, "sdpa", true, AT, "checkpoint-1", "application",
    );
    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "checkpoint-2", "application",
    );
    ledger = recordAnswer(ledger, "sdpa", false, AT, undefined, "application");

    expect(recordFor(ledger, "sdpa")).toMatchObject({
      level: "practiced",
      streak: 0,
      evidenceIds: [],
    });
  });

  it("records a first wrong answer as practice", () => {
    const ledger = recordAnswer(
      {}, "sdpa", false, AT, "checkpoint-1", "application",
    );

    expect(recordFor(ledger, "sdpa").level).toBe("practiced");
    expect(recordFor(ledger, "sdpa").streak).toBe(0);
  });

  it("does not mutate the ledger it is given", () => {
    const before: MasteryLedger = {};
    recordAnswer(before, "sdpa", true, AT, "checkpoint-1", "application");

    expect(before).toEqual({});
  });
});

describe("reading states", () => {
  it("persists the unseen to reading to read path", () => {
    const reading = markReading({}, "sdpa");
    const read = markRead(reading, "sdpa");

    expect(recordFor(reading, "sdpa").level).toBe("reading");
    expect(recordFor(read, "sdpa").level).toBe("read");
    expect(recordFor(reading, "sdpa").read).toBe(false);
    expect(recordFor(read, "sdpa").read).toBe(true);
  });

  it("keeps read completion separate from later application mastery", () => {
    let ledger = markRead({}, "sdpa");
    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "one", "application",
    );
    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "two", "application",
    );

    expect(recordFor(ledger, "sdpa")).toMatchObject({
      level: "mastered",
      read: true,
    });
  });

  it("records a completed read without lowering practice or its evidence", () => {
    const answered = recordAnswer(
      {}, "sdpa", true, AT, "checkpoint-1", "application",
    );

    expect(markReading(answered, "sdpa")).toBe(answered);
    expect(markRead(answered, "sdpa")).toMatchObject({
      sdpa: { level: "practiced", read: true, evidenceIds: ["checkpoint-1"] },
    });
  });
});

describe("ledger persistence", () => {
  it("restores a written ledger (reload)", () => {
    const storage = memoryStorage();
    const ledger = recordAnswer(
      {}, "sdpa", true, AT, "checkpoint-1", "application",
    );
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
        attention: { level: "practiced", streak: 1, lastAnswered: null },
      }),
    });

    expect(Object.keys(readLedger(storage))).toEqual(["attention"]);
  });

  it("coerces a corrupt streak instead of trusting it", () => {
    const storage = memoryStorage({
      [MASTERY_STORAGE_KEY]: JSON.stringify({
        sdpa: { level: "practiced", streak: -4, lastAnswered: 7 },
      }),
    });

    expect(readLedger(storage).sdpa).toEqual({
      level: "practiced",
      read: false,
      streak: 0,
      lastAnswered: null,
      evidenceIds: [],
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
    return {
      level: "practiced" as const,
      read: false,
      streak,
      lastAnswered,
      evidenceIds: [],
    };
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
    const ledger: MasteryLedger = {
      untouched: {
        level: "reading",
        read: false,
        streak: 0,
        lastAnswered: null,
        evidenceIds: [],
      },
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
    let ledger = recordAnswer(
      {}, "sdpa", true, AT, "checkpoint-1", "application",
    );
    ledger = recordAnswer(
      ledger, "sdpa", true, AT, "checkpoint-2", "application",
    );
    ledger = recordAnswer(
      ledger, "attention", true, AT, "checkpoint-3", "application",
    );
    ledger = markReading(ledger, "softmax");

    expect(masteredCount(ledger)).toBe(1);
  });
});
