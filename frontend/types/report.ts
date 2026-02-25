export type Language = "fr" | "en" | "es" | "de";
export type UserContext = "student" | "professional";
export type ChartType = "bar" | "pie" | "line";

export interface ReportInput {
  data: Record<string, unknown>[];
  language: Language;
  context: UserContext;
  title: string;
  chart_types: ChartType[];
}

export interface ReportOutput {
  report_id: string;
  pdf_url: string;
  charts: string[];
  summary: string;
  language: Language;
  created_at: string;
}

export interface UploadResponse {
  rows: number;
  columns: string[];
  data: Record<string, unknown>[];
}
