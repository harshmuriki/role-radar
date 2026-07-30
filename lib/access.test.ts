import { describe, expect, it } from "vitest";
import { accessDeniedMessage } from "./access";

describe("accessDeniedMessage", () => {
  it("identifies a signed-in email that is not on the allowlist", () => {
    expect(accessDeniedMessage("blocked@example.com")).toBe(
      "blocked@example.com is not approved for Role Radar.",
    );
  });
});
