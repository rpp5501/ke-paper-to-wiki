import { describe, expect, it } from "vitest";

import styles from "./styles.css?raw";

function zIndexFor(css: string, selector: string) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const rule = css.match(new RegExp(`${escaped}\\s*\\{([^}]*)\\}`));
  const match = rule?.[1].match(/z-index:\s*(\d+)/);
  return match ? Number(match[1]) : null;
}

describe("responsive layer ordering", () => {
  it("keeps the mobile drawer above its backdrop", () => {
    const mobileStart = styles.indexOf("@media (max-width: 899px)");
    const mobileEnd = styles.indexOf("@media (max-width: 639px)");
    const mobileCss = styles.slice(mobileStart, mobileEnd);

    const backdropZ = zIndexFor(styles, ".drawer-backdrop");
    const drawerZ = zIndexFor(mobileCss, ".drawer:not(:empty)");

    expect(backdropZ).not.toBeNull();
    expect(drawerZ).not.toBeNull();
    expect(drawerZ).toBeGreaterThan(backdropZ as number);
  });

  it("uses the approved accent token and persistent recognition for drawer links", () => {
    const rule = styles.match(
      /\.drawer-note a,\s*\.tier-body a\s*\{([^}]*)\}/,
    );

    expect(rule?.[1]).toContain("color: var(--accent)");
    expect(rule?.[1]).toContain("text-decoration: underline");
    expect(rule?.[1]).not.toMatch(/#[0-9a-f]{3,8}/i);
  });
});
