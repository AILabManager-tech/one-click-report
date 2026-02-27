"use client";

import type { ParseResponse } from "@/types/report";

interface DataPreviewProps {
  parseResult: ParseResponse;
  onConfirm: () => void;
  onRetry: () => void;
  t: {
    preview_title: string;
    preview_confirm: string;
    preview_retry: string;
    preview_confidence: string;
    preview_rows_count: string;
    preview_warnings: string;
    format_detected: string;
  };
}

export default function DataPreview({ parseResult, onConfirm, onRetry, t }: DataPreviewProps) {
  const { preview_rows, columns, rows, confidence, warnings, input_type } = parseResult;

  return (
    <div className="space-y-4">
      {/* Header: format + confidence */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-brand-navy">{t.preview_title}</h3>
        <div className="flex items-center gap-3 text-sm">
          <span className="rounded-full bg-blue-100 px-3 py-1 font-medium text-blue-700">
            {t.format_detected.replace("{format}", input_type.toUpperCase())}
          </span>
          <span className={`rounded-full px-3 py-1 font-medium ${
            confidence >= 0.8 ? "bg-green-100 text-green-700" :
            confidence >= 0.5 ? "bg-yellow-100 text-yellow-700" :
            "bg-red-100 text-red-700"
          }`}>
            {t.preview_confidence}: {Math.round(confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Row count */}
      <p className="text-sm text-gray-500">
        {t.preview_rows_count.replace("{count}", String(rows))}
      </p>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="rounded-lg bg-yellow-50 p-3">
          <p className="mb-1 text-sm font-semibold text-yellow-800">{t.preview_warnings}</p>
          <ul className="list-inside list-disc text-sm text-yellow-700">
            {warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}

      {/* Table */}
      {preview_rows.length > 0 && columns.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                {columns.map((col) => (
                  <th key={col} className="whitespace-nowrap px-4 py-2 text-left font-semibold text-gray-700">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {preview_rows.map((row, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  {columns.map((col) => (
                    <td key={col} className="whitespace-nowrap px-4 py-2 text-gray-600">
                      {row[col] != null ? String(row[col]) : "—"}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button onClick={onRetry} className="flex-1 rounded-lg border border-gray-200 px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50">
          {t.preview_retry}
        </button>
        <button onClick={onConfirm} className="btn-primary flex-1 py-3">
          {t.preview_confirm}
        </button>
      </div>
    </div>
  );
}
