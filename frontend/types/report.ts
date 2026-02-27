export type Language = "fr" | "en" | "es" | "de";
export type UserContext = "student" | "professional";
export type ChartType = "bar" | "pie" | "line";
export type InputFormat = "csv" | "json" | "excel" | "pdf" | "image" | "paste";

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

export interface ParseResponse {
  input_type: InputFormat;
  data: Record<string, unknown>[];
  rows: number;
  columns: string[];
  confidence: number;
  warnings: string[];
  preview_rows: Record<string, unknown>[];
  needs_user_input: boolean;
  options: Record<string, unknown>;
}
