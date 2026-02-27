"use client";

import { useState } from "react";

interface TextPasterProps {
  onSubmit: (text: string) => void;
  loading?: boolean;
  t: {
    paste_placeholder: string;
    paste_btn: string;
    parsing: string;
  };
}

export default function TextPaster({ onSubmit, loading, t }: TextPasterProps) {
  const [text, setText] = useState("");

  return (
    <div className="space-y-3">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={t.paste_placeholder}
        rows={8}
        className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm focus:border-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-dark resize-y"
      />
      <button
        onClick={() => text.trim() && onSubmit(text.trim())}
        disabled={!text.trim() || loading}
        className="btn-primary w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? t.parsing : t.paste_btn}
      </button>
    </div>
  );
}
