import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import ResourceEmbed from "./ResourceEmbed";

describe("ResourceEmbed", () => {
  it("renders an image resource as an img whose src is the resource url", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/diagram.png",
          title: "Attention diagram",
          type: "diagram",
          why: "Shows the QKV flow end to end.",
          embed: { kind: "image", src: "https://example.com/diagram.png" },
        }}
      />,
    );

    expect(html).toContain('src="https://example.com/diagram.png"');
    expect(html).toContain("<img");
  });

  it("renders a video resource's thumbnail, links the anchor at the watch url, and never an iframe", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://www.youtube.com/watch?v=abc123",
          title: "Transformers explained",
          type: "lecture",
          why: "A walkthrough of the architecture.",
          embed: {
            kind: "video",
            src: "https://img.youtube.com/vi/abc123/hqdefault.jpg",
            href: "https://www.youtube.com/watch?v=abc123",
          },
        }}
      />,
    );

    expect(html).toContain('src="https://img.youtube.com/vi/abc123/hqdefault.jpg"');
    expect(html).toMatch(/<a[^>]*href="https:\/\/www\.youtube\.com\/watch\?v=abc123"/);
    expect(html).not.toContain("<iframe");
  });

  it("renders a link resource as an anchor with no img", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/post",
          title: "A blog explainer",
          type: "blog",
          why: "Good intuition-first walkthrough.",
          embed: { kind: "link" },
        }}
      />,
    );

    expect(html).toMatch(/<a[^>]*href="https:\/\/example\.com\/post"/);
    expect(html).not.toContain("<img");
  });

  it("treats a missing embed as a plain link, never nothing, for bundles built before embeds existed", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/old",
          title: "Pre-embed resource",
          type: "paper",
        }}
      />,
    );

    expect(html).toMatch(/<a[^>]*href="https:\/\/example\.com\/old"/);
    expect(html).not.toContain("<img");
  });

  it("treats a malformed embed (unknown kind) as a plain link", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/weird",
          title: "Weird resource",
          type: "paper",
          embed: { kind: "gif" },
        }}
      />,
    );

    expect(html).toMatch(/<a[^>]*href="https:\/\/example\.com\/weird"/);
    expect(html).not.toContain("<img");
  });

  it("treats an explicit null embed as a plain link", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/null-embed",
          title: "Null embed resource",
          type: "paper",
          embed: null,
        }}
      />,
    );

    expect(html).toMatch(/<a[^>]*href="https:\/\/example\.com\/null-embed"/);
    expect(html).not.toContain("<img");
  });

  it("treats an image embed missing src as a plain link", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/no-src",
          title: "Image missing src",
          type: "diagram",
          embed: { kind: "image" },
        }}
      />,
    );

    expect(html).toMatch(/<a[^>]*href="https:\/\/example\.com\/no-src"/);
    expect(html).not.toContain("<img");
  });

  it("treats a video embed missing href as a plain link", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/no-href",
          title: "Video missing href",
          type: "lecture",
          embed: { kind: "video", src: "https://example.com/thumb.jpg" },
        }}
      />,
    );

    expect(html).toMatch(/<a[^>]*href="https:\/\/example\.com\/no-href"/);
    expect(html).not.toContain("<img");
  });

  it("gives every remote img referrerPolicy=no-referrer and every outbound anchor rel containing noreferrer", () => {
    const image = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/diagram.png",
          title: "Attention diagram",
          type: "diagram",
          embed: { kind: "image", src: "https://example.com/diagram.png" },
        }}
      />,
    );
    expect(image).toContain('referrerPolicy="no-referrer"');
    expect(image).toMatch(/<a[^>]*rel="[^"]*noreferrer[^"]*"/);

    const video = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://www.youtube.com/watch?v=abc123",
          title: "Transformers explained",
          type: "lecture",
          embed: {
            kind: "video",
            src: "https://img.youtube.com/vi/abc123/hqdefault.jpg",
            href: "https://www.youtube.com/watch?v=abc123",
          },
        }}
      />,
    );
    expect(video).toContain('referrerPolicy="no-referrer"');
    expect(video).toMatch(/<a[^>]*rel="[^"]*noreferrer[^"]*"/);

    const link = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/post",
          title: "A blog explainer",
          type: "blog",
          embed: { kind: "link" },
        }}
      />,
    );
    expect(link).toMatch(/<a[^>]*rel="[^"]*noreferrer[^"]*"/);
  });

  it("uses the resource title as the image's alt text", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/diagram.png",
          title: "Attention diagram",
          type: "diagram",
          embed: { kind: "image", src: "https://example.com/diagram.png" },
        }}
      />,
    );
    expect(html).toMatch(/alt="Attention diagram"/);
  });

  it("loads images lazily", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/diagram.png",
          title: "Attention diagram",
          type: "diagram",
          embed: { kind: "image", src: "https://example.com/diagram.png" },
        }}
      />,
    );
    expect(html).toContain('loading="lazy"');
  });

  it("renders a resource missing why without an empty caption element", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/post",
          title: "A blog explainer",
          type: "blog",
          embed: { kind: "link" },
        }}
      />,
    );

    expect(html).not.toContain("<figcaption></figcaption>");
    expect(html).not.toMatch(/<figcaption[^>]*>\s*<\/figcaption>/);
  });

  it("renders an image resource missing why without an empty caption element", () => {
    const html = renderToStaticMarkup(
      <ResourceEmbed
        resource={{
          url: "https://example.com/diagram.png",
          title: "Attention diagram",
          type: "diagram",
          embed: { kind: "image", src: "https://example.com/diagram.png" },
        }}
      />,
    );

    expect(html).not.toContain("<figcaption></figcaption>");
    expect(html).not.toMatch(/<figcaption[^>]*>\s*<\/figcaption>/);
  });
});
