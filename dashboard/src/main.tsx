import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { KE_DATA } from "./data.gen";
import { layoutGraph } from "./lib/layout";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

void layoutGraph(KE_DATA.nodes, KE_DATA.edges).catch((error: unknown) => {
  console.error("ELK worker layout failed", error);
});
