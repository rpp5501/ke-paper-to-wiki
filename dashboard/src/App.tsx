import { useEffect, useState } from "react";
import { KE_DATA } from "./data.gen";
import { layoutGraph } from "./lib/layout";

export default function App() {
  const [layoutSize, setLayoutSize] = useState<number>();

  useEffect(() => {
    let cancelled = false;
    void layoutGraph(KE_DATA.nodes, KE_DATA.edges)
      .then((positions) => {
        if (!cancelled) setLayoutSize(positions.size);
      })
      .catch((error: unknown) => {
        console.error("ELK worker layout failed", error);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return <div data-layout-nodes={layoutSize}>{KE_DATA.nodes.length} nodes loaded</div>;
}
