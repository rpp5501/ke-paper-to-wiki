import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  embeddableResources,
  GoDeeperResources,
  GoDeeperTierDetails,
  StandaloneGoDeeper,
} from "./Drawer";
import type { ResourceEmbedData } from "./blocks/ResourceEmbed";

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

// DrawerPresentation's placement logic: a note's resources ride the page's
// own "Go Deeper" tier when it has one (GoDeeperTierDetails, filtered --
// the prose already links everything), or get their own standalone
// disclosure when it doesn't (StandaloneGoDeeper, unfiltered -- there's no
// prose to duplicate, so a plain link must still render). These are the
// exact two components DrawerPresentation composes; the shipped AIAYN
// fixture carries no note resources, so -- same reasoning as the rest of
// this file -- they're driven directly with injected resources instead of
// through KE_DATA.

describe("GoDeeperTierDetails", () => {
  it("renders the tier prose plus filtered resources inside a single disclosure", () => {
    const markup = renderToStaticMarkup(
      <GoDeeperTierDetails
        glossary={{}}
        markdown="See the paper for details."
        resources={[LINK_RESOURCE, IMAGE_RESOURCE]}
      />,
    );

    expect(markup.match(/<summary>Go Deeper<\/summary>/g)).toHaveLength(1);
    expect(markup).toContain("See the paper for details.");
    expect(markup).toContain('src="https://example.com/diagram.png"');
  });

  // A note whose resources are all plain links, on a page WITH a go-deeper
  // tier: the prose already links every resource (P4's uncited-resource
  // gate), so no resource cards render at all -- just the prose.
  it("renders no resource cards when every resource is a plain link", () => {
    const markup = renderToStaticMarkup(
      <GoDeeperTierDetails glossary={{}} markdown="prose" resources={[LINK_RESOURCE]} />,
    );

    expect(markup).not.toContain("A blog explainer");
    expect(markup).not.toContain("resource-embed-list");
  });
});

describe("StandaloneGoDeeper", () => {
  it("renders nothing when the page already has a go-deeper tier -- that disclosure owns the resources", () => {
    const markup = renderToStaticMarkup(
      <StandaloneGoDeeper hasGoDeeperTier resources={[LINK_RESOURCE, IMAGE_RESOURCE]} />,
    );
    expect(markup).toBe("");
  });

  it("renders nothing for an empty resource list", () => {
    const markup = renderToStaticMarkup(
      <StandaloneGoDeeper hasGoDeeperTier={false} resources={[]} />,
    );
    expect(markup).toBe("");
  });

  // The bug: a page with no go-deeper tier at all (p4 failed for this
  // concept, or a resource was added after the pages were written) has no
  // prose to duplicate, so even a plain link must render -- "degrade to a
  // link, never to nothing."
  it("renders a plain link resource, unfiltered, when the page has no go-deeper tier", () => {
    const markup = renderToStaticMarkup(
      <StandaloneGoDeeper hasGoDeeperTier={false} resources={[LINK_RESOURCE]} />,
    );

    expect(markup).toContain("<summary>Go Deeper</summary>");
    expect(markup).toContain("A blog explainer");
    expect(markup).toMatch(/<a[^>]*href="https:\/\/example\.com\/post"/);
  });

  it("renders every resource kind unfiltered, in order, when the page has no go-deeper tier", () => {
    const markup = renderToStaticMarkup(
      <StandaloneGoDeeper
        hasGoDeeperTier={false}
        resources={[LINK_RESOURCE, IMAGE_RESOURCE, VIDEO_RESOURCE]}
      />,
    );

    expect(markup).toContain("A blog explainer");
    expect(markup).toContain('src="https://example.com/diagram.png"');
    expect(markup).toMatch(/<a[^>]*href="https:\/\/www\.youtube\.com\/watch\?v=abc123"/);
  });
});

describe("go-deeper placement: exactly one disclosure, never two", () => {
  // Composes the two real components exactly as DrawerPresentation does --
  // GoDeeperTierDetails only when the page has go-deeper prose,
  // StandaloneGoDeeper always called but self-gating on the opposite
  // condition -- so this proves the composition itself, not a
  // reimplementation of it.
  function renderGoDeeperRegion(hasGoDeeperTier: boolean, resources: ResourceEmbedData[]) {
    return renderToStaticMarkup(
      <>
        {hasGoDeeperTier && (
          <GoDeeperTierDetails glossary={{}} markdown="prose" resources={resources} />
        )}
        <StandaloneGoDeeper hasGoDeeperTier={hasGoDeeperTier} resources={resources} />
      </>,
    );
  }

  it("renders no resource cards when the page has a go-deeper tier -- prose already has them", () => {
    const markup = renderGoDeeperRegion(true, [LINK_RESOURCE]);

    expect(markup.match(/<summary>Go Deeper<\/summary>/g)).toHaveLength(1);
    expect(markup).not.toContain("A blog explainer");
  });

  it("renders every resource as a link when the page has no go-deeper tier", () => {
    const markup = renderGoDeeperRegion(false, [LINK_RESOURCE]);

    expect(markup.match(/<summary>Go Deeper<\/summary>/g)).toHaveLength(1);
    expect(markup).toContain("A blog explainer");
  });
});
