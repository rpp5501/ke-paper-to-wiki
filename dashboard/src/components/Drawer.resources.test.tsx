import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { GoDeeperResources } from "./Drawer";

// The shipped AIAYN fixture predates resource embeds, so this path is
// unreachable through KE_DATA -- same reasoning as Drawer.bridge.test.tsx
// for the "See it in code" bridge path. Tested directly with injected
// resources instead of threading a fixture through data.gen.ts.

describe("GoDeeperResources", () => {
  it("renders nothing for an empty resource list", () => {
    const markup = renderToStaticMarkup(<GoDeeperResources resources={[]} />);
    expect(markup).toBe("");
  });

  it("renders each resource as a ResourceEmbed", () => {
    const markup = renderToStaticMarkup(
      <GoDeeperResources
        resources={[
          {
            url: "https://example.com/post",
            title: "A blog explainer",
            type: "blog",
            why: "Good intuition-first walkthrough.",
            embed: { kind: "link" },
          },
          {
            url: "https://example.com/diagram.png",
            title: "Attention diagram",
            type: "diagram",
            embed: { kind: "image", src: "https://example.com/diagram.png" },
          },
        ]}
      />,
    );

    expect(markup).toContain("A blog explainer");
    expect(markup).toContain("Good intuition-first walkthrough.");
    expect(markup).toContain('src="https://example.com/diagram.png"');
  });
});
