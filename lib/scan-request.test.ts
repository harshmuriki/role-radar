import { describe, expect, it } from "vitest";
import { scanStatusMessage } from "./scan-request";

describe("scanStatusMessage", () => {
  it("reports a completed dashboard-requested scan", () => {
    expect(scanStatusMessage({ status: "completed", error: null }))
      .toBe("Scan complete. Your latest matching roles are ready.");
  });

  it("preserves a scan failure reason", () => {
    expect(scanStatusMessage({ status: "failed", error: "Supabase unavailable" }))
      .toBe("Scan failed: Supabase unavailable");
  });
});
