"use client";

import { useRef } from "react";

interface FileUploaderProps {
  onFile: (file: File) => void;
  fileName?: string;
  loading?: boolean;
  t: {
    upload_title: string;
    upload_desc_v2: string;
    parsing: string;
  };
}

const ACCEPTED_FORMATS = ".csv,.json,.xlsx,.xls,.pdf,.jpg,.jpeg,.png,.heic";

export default function FileUploader({ onFile, fileName, loading, t }: FileUploaderProps) {
  const fileRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  };

  return (
    <div
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      onClick={() => !loading && fileRef.current?.click()}
      className={`cursor-pointer rounded-xl border-2 border-dashed bg-gray-50 p-10 text-center transition-colors ${
        loading
          ? "border-brand-dark/30 bg-gray-100"
          : "border-gray-200 hover:border-brand-dark/30 hover:bg-gray-100"
      }`}
    >
      <input
        ref={fileRef}
        type="file"
        accept={ACCEPTED_FORMATS}
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
      {loading ? (
        <div className="flex flex-col items-center gap-3">
          <svg className="h-10 w-10 animate-spin text-brand-dark" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-sm font-medium text-brand-dark">{t.parsing}</p>
        </div>
      ) : (
        <>
          <svg className="mx-auto mb-4 h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
          </svg>
          <h3 className="mb-1 text-lg font-bold text-brand-navy">{t.upload_title}</h3>
          <p className="text-sm text-gray-500">{t.upload_desc_v2}</p>
          {fileName && (
            <p className="mt-3 text-sm font-medium text-brand-dark">{fileName}</p>
          )}
        </>
      )}
    </div>
  );
}
