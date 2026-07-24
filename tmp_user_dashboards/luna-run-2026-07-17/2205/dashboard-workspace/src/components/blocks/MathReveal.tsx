import { useState, type ReactNode } from "react";

export default function MathReveal({
  children,
  expandAll,
  shape,
}: {
  children: ReactNode;
  expandAll: boolean;
  shape: string;
}) {
  const [open, setOpen] = useState(false);
  const isOpen = expandAll || open;
  return (
    <details
      className="math-reveal"
      onToggle={(event) => {
        if (!expandAll) setOpen(event.currentTarget.open);
      }}
      open={isOpen}
    >
      <summary className="math-reveal-summary">
        <span className="math-reveal-shape">{shape}</span>
        {!isOpen && <span className="math-reveal-hint">Show the math</span>}
      </summary>
      <div className="math-reveal-body">{children}</div>
    </details>
  );
}
