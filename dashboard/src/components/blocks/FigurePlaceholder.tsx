import type { FigureBlock } from "../../lib/contentBlocks";

export default function FigurePlaceholder({ block }: { block: FigureBlock }) {
  return (
    <figure className="figure-placeholder" data-figure-id={block.id}>
      <div className="figure-placeholder-body">
        <span aria-hidden="true" className="figure-placeholder-icon">◈</span>
        <span>Interactive figure — coming soon</span>
      </div>
      {block.caption && <figcaption>{block.caption}</figcaption>}
    </figure>
  );
}
