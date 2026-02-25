"use client";

import { useState } from "react";

interface FAQItem {
  q: string;
  a: string;
}

interface FAQProps {
  items: FAQItem[];
  title: string;
}

export default function FAQ({ items, title }: FAQProps) {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section id="faq" className="bg-gray-50 py-20">
      <div className="mx-auto max-w-3xl px-4">
        <h2 className="mb-10 text-center text-3xl font-extrabold text-brand-navy md:text-4xl">
          {title}
        </h2>
        <div className="space-y-3">
          {items.map((item, i) => (
            <div key={i} className="card">
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="flex w-full items-center justify-between text-left"
                aria-expanded={open === i}
              >
                <h3 className="pr-4 text-base font-semibold text-brand-navy">
                  {item.q}
                </h3>
                <svg
                  className={`h-5 w-5 shrink-0 text-gray-400 transition-transform ${
                    open === i ? "rotate-180" : ""
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                </svg>
              </button>
              {open === i && (
                <p className="mt-3 text-sm leading-relaxed text-gray-600">
                  {item.a}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
