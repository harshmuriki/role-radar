export type CompanyTestResult = {
  status: "queued" | "passed" | "failed";
  fetched_count: number | null;
  error: string | null;
};

export function testResultMessage(companyName: string, result: CompanyTestResult): string {
  if (result.status === "passed") {
    return `Test passed for ${companyName}: found ${result.fetched_count ?? 0} roles.`;
  }
  return `Test failed for ${companyName}: ${result.error || "The worker did not provide an error."}`;
}
