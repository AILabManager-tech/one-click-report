"use client";

import Link from "next/link";
import type { Language } from "@/types/report";

interface NavbarProps {
  t: { home: string; generate: string; pricing: string; lang: string };
  lang: Language;
}

const LANGUAGES: { code: Language; flag: string }[] = [
  { code: "fr", flag: "FR" },
  { code: "en", flag: "EN" },
  { code: "es", flag: "ES" },
  { code: "de", flag: "DE" },
];

export default function Navbar({ t, lang }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/80 backdrop-blur-md">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href={`/${lang}`} className="text-xl font-extrabold text-brand-dark">
          OneClick<span className="text-brand-accent">Report</span>
        </Link>

        <div className="hidden items-center gap-6 md:flex">
          <a href="#features" className="text-sm font-medium text-gray-600 hover:text-brand-dark">
            {t.home}
          </a>
          <a href="#generate" className="text-sm font-medium text-gray-600 hover:text-brand-dark">
            {t.generate}
          </a>
        </div>

        <div className="flex items-center gap-1">
          {LANGUAGES.map((l) => (
            <Link
              key={l.code}
              href={`/${l.code}`}
              className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold transition-colors ${
                lang === l.code
                  ? "bg-brand-dark text-white"
                  : "text-gray-500 hover:bg-gray-100"
              }`}
            >
              {l.flag}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
