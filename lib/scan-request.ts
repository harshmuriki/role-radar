export type ScanRequestResult = {
  status: "queued" | "running" | "completed" | "failed";
  error: string | null;
};

export function scanStatusMessage(request: ScanRequestResult): string {
  if (request.status === "completed") return "Scan complete. Your latest matching roles are ready.";
  if (request.status === "failed") return `Scan failed: ${request.error || "The worker did not provide an error."}`;
  return "Running your scan now…";
}
