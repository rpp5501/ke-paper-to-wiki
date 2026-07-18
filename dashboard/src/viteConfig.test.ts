import { describe, expect, it } from "vitest";

import config from "../vite.config";

describe("Vite production paths", () => {
  it("keeps dashboard assets relative to the hosting directory", () => {
    expect(config).toMatchObject({ base: "./" });
  });
});
