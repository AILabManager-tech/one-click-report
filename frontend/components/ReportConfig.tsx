"use client";

import type { ChartType } from "@/types/report";

interface ReportConfigProps {
  title: string;
  onTitleChange: (title: string) => void;
  context: "student" | "professional";
  onContextChange: (context: "student" | "professional") => void;
  chartTypes: ChartType[];
  onChartToggle: (type: ChartType) => void;
  onGenerate: () => void;
  loading: boolean;
  t: {
    title_label: string;
    title_placeholder: string;
    context_label: string;
    context_student: string;
    context_pro: string;
    charts_label: string;
    generate_btn: string;
    generating: string;
  };
}

export default function ReportConfig({
  title, onTitleChange, context, onContextChange,
  chartTypes, onChartToggle, onGenerate, loading, t,
}: ReportConfigProps) {
  return (
    <div className="space-y-6">
      <div>
        <label className="mb-1 block text-sm font-semibold text-gray-700">
          {t.title_label}
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
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
              onClick={() => onContextChange(c)}
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
              onClick={() => onChartToggle(type)}
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
        onClick={onGenerate}
        disabled={loading}
        className="btn-primary w-full text-base py-4 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? t.generating : t.generate_btn}
      </button>
    </div>
  );
}
