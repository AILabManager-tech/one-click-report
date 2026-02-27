import type { ReportInput, ReportOutput, UploadResponse, ParseResponse } from "@/types/report";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/api/v1/reports/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(`Upload échoué: ${res.statusText}`);
  return res.json();
}

export async function compileReport(input: ReportInput): Promise<ReportOutput> {
  const res = await fetch(`${API_URL}/api/v1/reports/compile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!res.ok) throw new Error(`Génération échouée: ${res.statusText}`);
  return res.json();
}

export function getPdfUrl(reportId: string): string {
  return `${API_URL}/api/v1/reports/${reportId}/download`;
}

export function getChartUrl(reportId: string, index: number): string {
  return `${API_URL}/api/v1/reports/${reportId}/chart/${index}`;
}

export async function parseInput(
  file?: File,
  text?: string,
  options?: Record<string, unknown>
): Promise<ParseResponse> {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (text) formData.append("text", text);
  if (options) formData.append("options", JSON.stringify(options));

  const res = await fetch(`${API_URL}/api/v1/reports/parse`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `Parse failed: ${res.statusText}`);
  }
  return res.json();
}

interface ValidationResult {
  data: Record<string, unknown>[];
  warnings: string[];
  isValid: boolean;
}

// TODO(human): Implement validateAndTransform()
// This function receives raw uploaded data and should return cleaned data + diagnostics.
// Consider: numeric vs categorical detection, max row limit, null/empty handling.
// Return { data: cleaned[], warnings: string[], isValid: boolean }
export function validateAndTransform(
  rawData: Record<string, unknown>[]
): ValidationResult {
  return { data: rawData, warnings: [], isValid: true };
}
