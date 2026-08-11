import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import ConceptThreads from "./ConceptThreads";

const THREADS = {
  buildsOn: [
    { id: "background", label: "Background: Reducing Sequential Computation" },
    { id: "why-self-attention", label: "Why Self-Attention" },
  ],
  setsUp: [
    { id: "constituency", label: "English Constituency Parsing" },
    { id: "results", label: "Machine Translation Results" },
  ],
};

describe("ConceptThreads", () => {
  it("names what the reader needed first", () => {
    const html = renderToStaticMarkup(<ConceptThreads threads={THREADS} />);

    expect(html).toContain("Why Self-Attention");
    expect(html).toContain("Builds on");
  });

  it("names what this concept unlocks", () => {
    const html = renderToStaticMarkup(<ConceptThreads threads={THREADS} />);

    expect(html).toContain("Machine Translation Results");
    expect(html).toContain("Sets up");
  });

  it("links to the concept's own chapter so the thread is walkable", () => {
    const html = renderToStaticMarkup(<ConceptThreads threads={THREADS} />);

    expect(html).toContain('href="#why-self-attention"');
    expect(html).toContain('href="#results"');
  });

  it("renders nothing at all when a concept has no threads", () => {
    /* Half the concepts in a real graph are joined only by part-of. An empty
       "Builds on —" heading is noise on every one of those pages. */
    const html = renderToStaticMarkup(
      <ConceptThreads threads={{ buildsOn: [], setsUp: [] }} />,
    );

    expect(html).toBe("");
  });

  it("shows only the half that exists", () => {
    const html = renderToStaticMarkup(
      <ConceptThreads threads={{ buildsOn: [], setsUp: THREADS.setsUp }} />,
    );

    expect(html).not.toContain("Builds on");
    expect(html).toContain("Sets up");
  });

  it("survives a bundle built before threads existed", () => {
    expect(renderToStaticMarkup(<ConceptThreads threads={undefined} />)).toBe("");
  });
});

describe("ConceptThreads reachability", () => {
  /* The guided view renders only the chapters on the reading path, so a
     thread can name a concept that has no anchor on this page. Rendering it
     as a link produces a click that scrolls nowhere -- worse than plain text,
     because it silently teaches the reader the navigation is broken. */
  it("does not link to a concept that is not on the page", () => {
    const html = renderToStaticMarkup(
      <ConceptThreads reachable={new Set(["results"])} threads={THREADS} />,
    );

    expect(html).not.toContain('href="#why-self-attention"');
    expect(html).toContain("Why Self-Attention");
  });

  it("still links the ones that are there", () => {
    const html = renderToStaticMarkup(
      <ConceptThreads reachable={new Set(["results"])} threads={THREADS} />,
    );

    expect(html).toContain('href="#results"');
  });

  it("links everything when no reachable set is given", () => {
    const html = renderToStaticMarkup(<ConceptThreads threads={THREADS} />);

    expect(html).toContain('href="#why-self-attention"');
  });
});
