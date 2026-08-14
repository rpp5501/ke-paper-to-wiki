import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { embeddableResources, GoDeeperResources } from "./Drawer";

// The shipped AIAYN fixture predates resource embeds, so this path is
// unreachable through KE_DATA -- same reasoning as Drawer.bridge.test.tsx
// for the "See it in code" bridge path. Tested directly with injected
// resources instead of threading a fixture through data.gen.ts.

const LINK_RESOURCE = {
  url: "https://example.com/post",
  title: "A blog explainer",
  type: "blog",
  why: "Good intuition-first walkthrough.",
  embed: { kind: "link" },
};

const IMAGE_RESOURCE = {
  url: "https://example.com/diagram.png",
  title: "Attention diagram",
  type: "diagram",
  embed: { kind: "image", src: "https://example.com/diagram.png" },
};

const VIDEO_RESOURCE = {
  url: "https://www.youtube.com/watch?v=abc123",
  title: "Transformers explained",
  type: "lecture",
  embed: {
    kind: "video",
    src: "https://img.youtube.com/vi/abc123/hqdefault.jpg",
    href: "https://www.youtube.com/watch?v=abc123",
  },
};

describe("embeddableResources", () => {
  // P4's uncited-resource gate guarantees the go-deeper prose already links
  // every resource -- a link-kind card would just repeat what's already
  // there, so only resources whose picture prose can't carry get a card.
  it("keeps only image and video resources, in order, dropping link resources", () => {
    expect(embeddableResources([LINK_RESOURCE, IMAGE_RESOURCE, VIDEO_RESOURCE]))
      .toEqual([IMAGE_RESOURCE, VIDEO_RESOURCE]);
  });

  it("drops a malformed embed (missing src, degrades to link) same as an explicit link kind", () => {
    const malformedImage = { ...IMAGE_RESOURCE, embed: { kind: "image" } };
    expect(embeddableResources([malformedImage])).toEqual([]);
  });

  it("returns an empty list for an empty list", () => {
    expect(embeddableResources([])).toEqual([]);
  });
});

describe("GoDeeperResources", () => {
  it("renders nothing for an empty resource list", () => {
    const markup = renderToStaticMarkup(<GoDeeperResources resources={[]} />);
    expect(markup).toBe("");
  });

  // A note whose resources are all plain links must look exactly as it did
  // before Task 4 -- no empty container, no heading, no stray separator.
  it("renders nothing when every resource is a plain link", () => {
    const markup = renderToStaticMarkup(
      <GoDeeperResources resources={[LINK_RESOURCE]} />,
    );
    expect(markup).toBe("");
  });

  it("renders a card for image and video resources but skips link resources entirely", () => {
    const markup = renderToStaticMarkup(
      <GoDeeperResources resources={[LINK_RESOURCE, IMAGE_RESOURCE, VIDEO_RESOURCE]} />,
    );

    expect(markup).not.toContain("A blog explainer");
    expect(markup).toContain('src="https://example.com/diagram.png"');
    expect(markup).toMatch(/<a[^>]*href="https:\/\/www\.youtube\.com\/watch\?v=abc123"/);
  });
});
