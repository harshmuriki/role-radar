import { describe, expect, it } from "vitest";
import { testResultMessage } from "./company-test";

describe("testResultMessage", () => {
  it("reports an immediately completed successful test", () => {
    expect(testResultMessage("Acme", { status: "passed", fetched_count: 2, error: null }))
      .toBe("Test passed for Acme: found 2 roles.");
  });

  it("reports a worker failure without hiding its cause", () => {
    expect(testResultMessage("Acme", { status: "failed", fetched_count: null, error: "Unsupported ATS" }))
      .toBe("Test failed for Acme: Unsupported ATS");
  });
});
