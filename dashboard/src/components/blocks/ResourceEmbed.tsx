/** One resource from a concept's research note. `embed` is classified at
 *  build time (Task 2's embed_kind) so the browser never fetches a url just
 *  to find out what it is. */
export type ResourceEmbedData = {
  url: string;
  title: string;
  type?: string;
  why?: string;
  anchor?: string;
  embed?: unknown;
};

type Embed =
  | { kind: "link" }
  | { kind: "image"; src: string }
  | { kind: "video"; src: string; href: string };

/** A missing or malformed embed -- an older bundle, or a field a future
 *  format changes -- degrades to a plain link, same as before this field
 *  existed. Never to nothing. */
export function normalizeEmbed(embed: unknown): Embed {
  if (embed && typeof embed === "object") {
    const candidate = embed as { kind?: unknown; src?: unknown; href?: unknown };
    if (candidate.kind === "image" && typeof candidate.src === "string") {
      return { kind: "image", src: candidate.src };
    }
    if (
      candidate.kind === "video"
      && typeof candidate.src === "string"
      && typeof candidate.href === "string"
    ) {
      return { kind: "video", src: candidate.src, href: candidate.href };
    }
  }
  return { kind: "link" };
}

/** Play triangle drawn by hand -- no icon fetched from anywhere, per the
 *  no-third-party-JS rule this component exists to uphold. */
function PlayGlyph() {
  return (
    <svg aria-hidden="true" className="resource-embed-play" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="11" />
      <polygon points="9.5,7.5 9.5,16.5 17,12" />
    </svg>
  );
}

export default function ResourceEmbed({ resource }: { resource: ResourceEmbedData }) {
  const embed = normalizeEmbed(resource.embed);
  const why = resource.why?.trim();
  const anchor = resource.anchor?.trim();

  if (embed.kind === "image") {
    return (
      <figure className="resource-embed resource-embed-image">
        <a href={resource.url} rel="noreferrer" target="_blank">
          <img
            alt={resource.title}
            loading="lazy"
            referrerPolicy="no-referrer"
            src={embed.src}
          />
        </a>
        {(anchor || why) && (
          <figcaption>
            {anchor && <span className="resource-embed-anchor">{anchor}</span>}
            {why && <span className="resource-embed-why">{why}</span>}
          </figcaption>
        )}
      </figure>
    );
  }

  if (embed.kind === "video") {
    return (
      <figure className="resource-embed resource-embed-video">
        <a href={embed.href} rel="noreferrer" target="_blank">
          <span className="resource-embed-thumb">
            <img
              alt={resource.title}
              loading="lazy"
              referrerPolicy="no-referrer"
              src={embed.src}
            />
            <PlayGlyph />
          </span>
        </a>
        <figcaption>
          <span className="resource-embed-title">{resource.title}</span>
          {anchor && (
            <>
              {" "}
              <span className="resource-embed-anchor">{anchor}</span>
            </>
          )}
          {why && <span className="resource-embed-why"> — {why}</span>}
        </figcaption>
      </figure>
    );
  }

  return (
    <figure className="resource-embed resource-embed-link">
      <a href={resource.url} rel="noreferrer" target="_blank">{resource.title}</a>
      {(anchor || why) && (
        <figcaption>
          {anchor && <span className="resource-embed-anchor">{anchor}</span>}
          {why && <span className="resource-embed-why">{why}</span>}
        </figcaption>
      )}
    </figure>
  );
}
