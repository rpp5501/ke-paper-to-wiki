import { useRef, type PointerEvent } from "react";

import {
  widthFromKeyboard,
  type PanelBounds,
  type PanelId,
} from "../lib/panelSizing";

type PanelSide = "left" | "right";

type PanelResizerProps = {
  bounds: PanelBounds;
  id: PanelId;
  label: string;
  onChange: (width: number) => void;
  onReset: () => void;
  side: PanelSide;
  value: number;
};

export function resizeFromPointer(
  side: PanelSide,
  startX: number,
  clientX: number,
  startWidth: number,
  bounds: PanelBounds,
): number {
  const delta = side === "left" ? clientX - startX : startX - clientX;
  return Math.min(bounds.max, Math.max(bounds.min, Math.round(startWidth + delta)));
}

export default function PanelResizer({
  bounds,
  id,
  label,
  onChange,
  onReset,
  side,
  value,
}: PanelResizerProps) {
  const drag = useRef<{
    pointerId: number;
    startX: number;
    startWidth: number;
  } | null>(null);

  const endPointer = (event: PointerEvent<HTMLDivElement>) => {
    if (drag.current?.pointerId !== event.pointerId) return;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    drag.current = null;
  };

  return (
    <div
      aria-label={label}
      aria-orientation="vertical"
      aria-valuemax={bounds.max}
      aria-valuemin={bounds.min}
      aria-valuenow={value}
      className={`panel-resizer panel-resizer-${side}`}
      data-panel={id}
      onDoubleClick={onReset}
      onKeyDown={(event) => {
        const next = widthFromKeyboard(event.key, event.shiftKey, value, bounds);
        if (next === null) return;
        event.preventDefault();
        onChange(next);
      }}
      onPointerCancel={endPointer}
      onPointerDown={(event) => {
        drag.current = {
          pointerId: event.pointerId,
          startX: event.clientX,
          startWidth: value,
        };
        event.currentTarget.setPointerCapture(event.pointerId);
      }}
      onPointerMove={(event) => {
        const active = drag.current;
        if (!active || active.pointerId !== event.pointerId) return;
        onChange(resizeFromPointer(
          side,
          active.startX,
          event.clientX,
          active.startWidth,
          bounds,
        ));
      }}
      onPointerUp={endPointer}
      role="separator"
      tabIndex={0}
    />
  );
}
