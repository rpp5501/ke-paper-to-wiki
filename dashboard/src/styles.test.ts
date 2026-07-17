import { describe, expect, it } from "vitest";

import styles from "./styles.css?raw";

function zIndexFor(css: string, selector: string) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const rule = css.match(new RegExp(`${escaped}\\s*\\{([^}]*)\\}`));
  const match = rule?.[1].match(/z-index:\s*(\d+)/);
  return match ? Number(match[1]) : null;
}

describe("responsive layer ordering", () => {
  it("sizes desktop support panels with adjustable CSS variables", () => {
    expect(styles).toMatch(/\.sidebar\s*\{[^}]*width:\s*var\(--diagnostics-width/s);
    expect(styles).toMatch(/\.drawer\s*\{[^}]*width:\s*var\(--drawer-width/s);
    expect(styles).toMatch(/\.progress-rail\s*\{[^}]*width:\s*var\(--guided-rail-width/s);
    expect(styles).toMatch(/@media \(max-width: 899px\)[\s\S]*\.panel-resizer\s*\{[^}]*display:\s*none/s);
  });

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

  it("keeps code excerpts class-based and makes mobile overlays non-overlapping", () => {
    expect(styles).toMatch(/\.code-viewer\s*\{[^}]*font-size:\s*var\(--fs-small\)/s);
    expect(styles).toMatch(/\.code-viewer\s*\{[^}]*padding:\s*10px/s);
    expect(styles).toMatch(/\.code-viewer\s*\{[^}]*overflow-x:\s*auto/s);
    expect(styles).toContain(".token.keyword");

    const mobileStart = styles.indexOf("@media (max-width: 639px)");
    const reducedMotionStart = styles.indexOf("@media (prefers-reduced-motion: reduce)");
    const mobileCss = styles.slice(mobileStart, reducedMotionStart);
    expect(mobileCss).toMatch(/\.tour-overlay\s*\{[^}]*bottom:/s);
    expect(mobileCss).toMatch(/\.react-flow__controls\s*\{[^}]*top:/s);
    expect(mobileCss).toMatch(/\.legend\s*\{[^}]*top:/s);
  });

  it("reserves player space globally and shifts controls beside overlay drawers", () => {
    expect(styles).toMatch(
      /\.tour-overlay\s*\{[^}]*bottom:\s*max\(92px,/s,
    );
    expect(styles).toMatch(
      /\.workspace\.drawer-open \.playerbar\s*\{[^}]*right:/s,
    );
    expect(styles).toMatch(
      /\.workspace\.drawer-open \.tour-overlay\s*\{[^}]*right:/s,
    );
  });
});

describe("reader v2 design tokens", () => {
  it("defines the token set", () => {
    for (const token of ["--bg-page", "--bg-rail", "--bg-card", "--ink", "--accent",
      "--fs-body: 18px", "--fs-small: 14px", "--lh-body: 1.65",
      "--article-width: 700px", "--term-1", "--term-5", "--font-body"]) {
      expect(styles).toContain(token);
    }
  });

  it("has no sub-14px font sizes anywhere", () => {
    const sizes = [...styles.matchAll(/font-size:\s*([\d.]+)px/g)].map((m) => Number(m[1]));
    expect(sizes.filter((s) => s < 14)).toEqual([]);
  });
});

describe("learn mode styling", () => {
  it("styles learn mode with only locked palette colors", () => {
    const start = styles.indexOf("/* ── Learn mode");
    expect(start).toBeGreaterThan(-1);
    const learnCss = styles.slice(start);
    const allowed = new Set([
      "#64748b", "#4a9b5e", "#cc8855", "#475569", "#f97316",
      "#0e1626", "#1c2a44", "#3b2f14", "#3a1420", "#fff", "#ffffff",
    ]);
    const hexes = learnCss.match(/#[0-9a-fA-F]{3,8}/g) ?? [];
    const offenders = hexes.filter((hex) => !allowed.has(hex.toLowerCase()));
    expect(offenders).toEqual([]);
  });

  it("keeps learn-mode transitions within the motion contract", () => {
    const start = styles.indexOf("/* ── Learn mode");
    const learnCss = styles.slice(start);
    expect(learnCss).not.toContain("transition: all");
  });
});
