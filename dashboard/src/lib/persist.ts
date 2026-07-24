// R16.A1 — best-effort localStorage helpers, generalized from the
// panelSizing read/write pattern so session state and the mastery ledger can
// share one place that knows storage may be absent or disabled.
export type StorageLike = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
};

export function browserStorage(): StorageLike | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

// Returns `unknown` on purpose: stored JSON is user-editable, so every caller
// has to validate its shape rather than trust the parse.
export function readJSON(
  storage: StorageLike | null | undefined,
  key: string,
): unknown {
  if (!storage) return null;

  try {
    return JSON.parse(storage.getItem(key) ?? "null");
  } catch {
    return null;
  }
}

export function writeJSON(
  storage: StorageLike | null | undefined,
  key: string,
  value: unknown,
): void {
  if (!storage) return;

  try {
    storage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage is best-effort and may be disabled by the browser.
  }
}
