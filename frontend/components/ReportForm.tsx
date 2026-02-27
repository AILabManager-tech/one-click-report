"use client";

import { useState } from "react";
import type { Language, ChartType, ReportOutput, ParseResponse } from "@/types/report";
import { uploadFile, compileReport, parseInput } from "@/services/api";
import InputSelector from "./InputSelector";
import FileUploader from "./FileUploader";
import TextPaster from "./TextPaster";
import SheetSelector from "./SheetSelector";
import DataPreview from "./DataPreview";
import ReportConfig from "./ReportConfig";
import ReportResult from "./ReportResult";

interface FormTexts {
  upload_title: string;
  upload_desc: string;
  upload_desc_v2: string;
  upload_btn: string;
  tab_upload: string;
  tab_paste: string;
  paste_placeholder: string;
  paste_btn: string;
  preview_title: string;
  preview_confirm: string;
  preview_retry: string;
  preview_confidence: string;
  preview_rows_count: string;
  preview_warnings: string;
  sheet_select: string;
  parsing: string;
  no_data_found: string;
  format_detected: string;
  title_label: string;
  title_placeholder: string;
  context_label: string;
  context_student: string;
  context_pro: string;
  charts_label: string;
  generate_btn: string;
  generating: string;
  download_pdf: string;
  summary_title: string;
}

interface ReportFormProps {
  t: FormTexts;
  lang: Language;
}

type Step = "input" | "sheet-select" | "preview" | "config" | "result";

export default function ReportForm({ t, lang }: ReportFormProps) {
  const [step, setStep] = useState<Step>("input");
  const [tab, setTab] = useState<"upload" | "paste">("upload");
  const [fileName, setFileName] = useState("");
  const [parsing, setParsing] = useState(false);
  const [parseResult, setParseResult] = useState<ParseResponse | null>(null);
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);

  // Report config state
  const [title, setTitle] = useState("");
  const [context, setContext] = useState<"student" | "professional">("student");
  const [chartTypes, setChartTypes] = useState<ChartType[]>(["bar", "pie"]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReportOutput | null>(null);
  const [error, setError] = useState("");

  const safeError = (e: unknown): string => {
    const msg = e instanceof Error ? e.message : String(e);
    if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) return "Connection error. Please try again.";
    if (msg.includes("413") || msg.includes("too large")) return "File too large (max 20 MB).";
    if (msg.includes("415") || msg.includes("format")) return "Unsupported format.";
    if (msg.includes("429")) return "Too many requests. Please wait.";
    return msg || "An error occurred. Please try again.";
  };

  const isNewFormat = (file: File): boolean => {
    const name = file.name.toLowerCase();
    return /\.(xlsx|xls|pdf|jpg|jpeg|png|heic)$/.test(name);
  };

  const handleFile = async (file: File) => {
    setFileName(file.name);
    setError("");
    setParsing(true);
    setPendingFile(file);

    try {
      if (isNewFormat(file)) {
        // New formats → /parse endpoint
        const res = await parseInput(file);
        setParseResult(res);

        if (res.needs_user_input) {
          setStep("sheet-select");
        } else {
          setStep("preview");
        }
      } else {
        // CSV/JSON → legacy /upload endpoint for retrocompat
        const res = await uploadFile(file);
        setData(res.data as Record<string, unknown>[]);
        setStep("config");
      }
    } catch (e) {
      setError(safeError(e));
    } finally {
      setParsing(false);
    }
  };

  const handlePaste = async (text: string) => {
    setError("");
    setParsing(true);
    try {
      const res = await parseInput(undefined, text);
      setParseResult(res);
      setStep("preview");
    } catch (e) {
      setError(safeError(e));
    } finally {
      setParsing(false);
    }
  };

  const handleSheetSelect = async (sheet: string) => {
    if (!pendingFile) return;
    setError("");
    setParsing(true);
    try {
      const res = await parseInput(pendingFile, undefined, { sheet });
      setParseResult(res);
      setStep("preview");
    } catch (e) {
      setError(safeError(e));
    } finally {
      setParsing(false);
    }
  };

  const handlePreviewConfirm = () => {
    if (parseResult) {
      setData(parseResult.data);
      setStep("config");
    }
  };

  const handleRetry = () => {
    setStep("input");
    setParseResult(null);
    setData(null);
    setFileName("");
    setPendingFile(null);
    setResult(null);
    setError("");
  };

  const handleGenerate = async () => {
    if (!data) return;
    setLoading(true);
    setError("");
    try {
      const report = await compileReport({
        data,
        language: lang,
        context,
        title: title || t.title_placeholder,
        chart_types: chartTypes,
      });
      setResult(report);
      setStep("result");
    } catch (e) {
      setError(safeError(e));
    } finally {
      setLoading(false);
    }
  };

  const toggleChart = (type: ChartType) => {
    setChartTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  return (
    <section id="generate" className="py-20">
      <div className="mx-auto max-w-3xl px-4">
        <div className="card space-y-8">
          {/* Step: Input */}
          {step === "input" ? (
            <>
              <InputSelector activeTab={tab} onTabChange={setTab} t={t} />
              {tab === "upload" ? (
                <FileUploader onFile={handleFile} fileName={fileName} loading={parsing} t={t} />
              ) : (
                <TextPaster onSubmit={handlePaste} loading={parsing} t={t} />
              )}
            </>
          ) : null}

          {/* Step: Sheet selection (Excel multi-sheet) */}
          {step === "sheet-select" && parseResult?.options?.sheets ? (
            <SheetSelector
              sheets={parseResult.options.sheets as string[]}
              onSelect={handleSheetSelect}
              t={t}
            />
          ) : null}

          {/* Step: Data preview */}
          {step === "preview" && parseResult ? (
            <DataPreview
              parseResult={parseResult}
              onConfirm={handlePreviewConfirm}
              onRetry={handleRetry}
              t={t}
            />
          ) : null}

          {/* Step: Report configuration */}
          {step === "config" && data ? (
            <ReportConfig
              title={title}
              onTitleChange={setTitle}
              context={context}
              onContextChange={setContext}
              chartTypes={chartTypes}
              onChartToggle={toggleChart}
              onGenerate={handleGenerate}
              loading={loading}
              t={t}
            />
          ) : null}

          {/* Step: Result */}
          {step === "result" && result ? (
            <ReportResult result={result} t={t} />
          ) : null}

          {/* Error display */}
          {error ? (
            <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>
          ) : null}

          {/* Back to start (visible when not on input step) */}
          {step !== "input" && step !== "result" ? (
            <button
              onClick={handleRetry}
              className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
            >
              &larr; {t.preview_retry}
            </button>
          ) : null}
        </div>
      </div>
    </section>
  );
}
