import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import App from "./App";
import { KE_DATA } from "./data.gen";

describe("App", () => {
  it("renders the generated graph node count", () => {
    expect(renderToStaticMarkup(App())).toBe(
      `<div>${KE_DATA.nodes.length} nodes loaded</div>`,
    );
  });
});
