"use client";

import type { ReportOutput } from "@/types/report";
import { getPdfUrl } from "@/services/api";

interface ReportResultProps {
  result: ReportOutput;
  t: {
    summary_title: string;
    download_pdf: string;
  };
}

export default function ReportResult({ result, t }: ReportResultProps) {
  return (
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
  );
}
