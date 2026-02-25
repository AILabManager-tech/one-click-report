"use client";

import { useState, useRef } from "react";
import type { Language, ChartType, ReportOutput } from "@/types/report";
import { uploadFile, compileReport, getPdfUrl } from "@/services/api";

interface FormTexts {
  upload_title: string;
  upload_desc: string;
  upload_btn: string;
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

export default function ReportForm({ t, lang }: ReportFormProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);
  const [title, setTitle] = useState("");
  const [context, setContext] = useState<"student" | "professional">("student");
  const [chartTypes, setChartTypes] = useState<ChartType[]>(["bar", "pie"]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReportOutput | null>(null);
  const [error, setError] = useState("");

  const handleFile = async (f: File) => {
    setFile(f);
    setError("");
    try {
      const res = await uploadFile(f);
      setData(res.data as Record<string, unknown>[]);
    } catch (e) {
      setError(String(e));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const toggleChart = (type: ChartType) => {
    setChartTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
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
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="generate" className="py-20">
      <div className="mx-auto max-w-3xl px-4">
        <div className="card space-y-8">
          {/* Upload */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            className="cursor-pointer rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 p-10 text-center transition-colors hover:border-brand-dark/30 hover:bg-gray-100"
          >
            <input
              ref={fileRef}
              type="file"
              accept=".csv,.json"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
            <svg className="mx-auto mb-4 h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
            </svg>
            <h3 className="mb-1 text-lg font-bold text-brand-navy">{t.upload_title}</h3>
            <p className="text-sm text-gray-500">{t.upload_desc}</p>
            {file && (
              <p className="mt-3 text-sm font-medium text-brand-dark">{file.name}</p>
            )}
          </div>

          {/* Config */}
          {data && (
            <div className="space-y-6">
              <div>
                <label className="mb-1 block text-sm font-semibold text-gray-700">
                  {t.title_label}
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder={t.title_placeholder}
                  className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-dark"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-gray-700">
                  {t.context_label}
                </label>
                <div className="flex gap-3">
                  {(["student", "professional"] as const).map((c) => (
                    <button
                      key={c}
                      onClick={() => setContext(c)}
                      className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                        context === c
                          ? "bg-brand-dark text-white"
                          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                      }`}
                    >
                      {c === "student" ? t.context_student : t.context_pro}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-gray-700">
                  {t.charts_label}
                </label>
                <div className="flex flex-wrap gap-2">
                  {(["bar", "pie", "line"] as ChartType[]).map((type) => (
                    <button
                      key={type}
                      onClick={() => toggleChart(type)}
                      className={`rounded-lg px-4 py-2 text-sm font-medium capitalize transition-colors ${
                        chartTypes.includes(type)
                          ? "bg-brand-accent text-white"
                          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleGenerate}
                disabled={loading}
                className="btn-primary w-full text-base py-4 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? t.generating : t.generate_btn}
              </button>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>
          )}

          {/* Result */}
          {result && (
            <div className="space-y-6 border-t border-gray-100 pt-6">
              <div>
                <h3 className="mb-3 text-lg font-bold text-brand-navy">{t.summary_title}</h3>
                <div className="rounded-xl bg-blue-50 p-5 text-sm leading-relaxed text-gray-700 whitespace-pre-wrap">
                  {result.summary}
                </div>
              </div>

              <a
                href={getPdfUrl(result.report_id)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-accent w-full text-center text-base py-4 block"
              >
                {t.download_pdf}
              </a>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
