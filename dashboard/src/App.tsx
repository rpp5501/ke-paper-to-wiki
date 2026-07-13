import { ReactFlowProvider } from "@xyflow/react";

import Canvas from "./components/Canvas";
import Legend from "./components/Legend";

export default function App() {
  return (
    <ReactFlowProvider>
      <div className="shell">
        <aside className="sidebar" id="left-panel" />
        <main className="main">
          <header className="topbar" id="topbar" />
          <div className="workspace">
            <div className="canvas-wrap">
              <Canvas />
              <Legend />
              <div id="playerbar" />
              <div id="tour-overlay" />
            </div>
            <aside className="drawer" id="drawer" />
          </div>
        </main>
      </div>
    </ReactFlowProvider>
  );
}
