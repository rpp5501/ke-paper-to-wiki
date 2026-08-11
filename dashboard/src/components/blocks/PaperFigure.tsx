import type { FigureBlock } from "../../lib/contentBlocks";
import FigurePlaceholder from "./FigurePlaceholder";

/** Figures the pack recovered, keyed by the id a ```figure block names. */
export type PaperFigures = Record<
  string,
  { caption: string; section: string; images: string[] }
>;

/**
 * The paper's own figure, when we have the image for it.
 *
 * A ```figure block carries only an id, so the caption and the file come from
 * the pack. Two things stay deliberate: a figure with no image (TikZ draws
 * itself, and some references resolve to nothing) falls back to the
 * placeholder rather than a broken <img>, and images load lazily because one
 * page of DDIM can pull several megabytes.
 */
export default function PaperFigure({
  block,
  figures,
}: {
  block: FigureBlock;
  figures?: PaperFigures;
}) {
  const entry = figures?.[block.id];
  // The writer's caption wins: it is written for this page, while the pack's
  // is the paper's own and often assumes the surrounding text.
  const caption = block.caption || entry?.caption || "";

  if (!entry?.images?.length) {
    return <FigurePlaceholder block={{ ...block, caption }} />;
  }

  return (
    <figure className="paper-figure" data-figure-id={block.id}>
      <div className="paper-figure-panels">
        {entry.images.map((src) => (
          <img
            key={src}
            src={`/${src}`}
            alt={caption || `Figure ${block.id}`}
            loading="lazy"
          />
        ))}
      </div>
      {caption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
