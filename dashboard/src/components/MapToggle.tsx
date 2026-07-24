// R15.10 — mind-map layout toggle (explore mode only). Switches the ELK
// algorithm between the default layered reading order and a radial
// mind-map arrangement. Pairs with the clusters view for theme coloring.
import CompactPill from "./CompactPill";
import { useApp } from "../store";

export type MapTogglePresentationProps = {
  active: boolean;
  onToggle: () => void;
  visible: boolean;
};

export function MapTogglePresentation({
  active,
  onToggle,
  visible,
}: MapTogglePresentationProps) {
  if (!visible) return null;
  return (
    <CompactPill
      active={active}
      aria-pressed={active}
      onClick={onToggle}
      title="Arrange the graph as a radial mind map"
    >
      Mind map
    </CompactPill>
  );
}

export default function MapToggle() {
  const mode = useApp((state) => state.mode);
  const layoutMode = useApp((state) => state.layoutMode);
  const setLayoutMode = useApp((state) => state.setLayoutMode);

  return (
    <MapTogglePresentation
      active={layoutMode === "radial"}
      onToggle={() =>
        setLayoutMode(layoutMode === "radial" ? "layered" : "radial")
      }
      visible={mode === "explore"}
    />
  );
}
