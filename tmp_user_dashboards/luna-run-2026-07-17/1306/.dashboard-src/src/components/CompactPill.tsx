import { forwardRef, type ButtonHTMLAttributes } from "react";

type CompactPillProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  active?: boolean;
};

const CompactPill = forwardRef<HTMLButtonElement, CompactPillProps>(
  function CompactPill({ active = false, children, className = "", ...props }, ref) {
    return (
      <button
        {...props}
        className={`pill-hit ${className}`.trim()}
        ref={ref}
        type={props.type ?? "button"}
      >
        <span className={`pill${active ? " active" : ""}`}>{children}</span>
      </button>
    );
  },
);

export default CompactPill;
