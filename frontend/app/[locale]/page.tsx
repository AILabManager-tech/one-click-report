"use client";

import { useParams } from "next/navigation";
import type { Language } from "@/types/report";
import { getDictionary } from "../i18n";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import ReportForm from "@/components/ReportForm";
import Footer from "@/components/Footer";
import JsonLd from "@/components/JsonLd";

export default function LocalePage() {
  const params = useParams();
  const locale = (params.locale as Language) || "fr";
  const t = getDictionary(locale);

  return (
    <>
      <JsonLd lang={locale} />
      <div className="min-h-screen flex flex-col">
        <Navbar t={t.nav} lang={locale} />
        <main className="flex-1">
          <Hero t={t.hero} />
          <Features t={t.features} />
          <ReportForm t={t.form} lang={locale} />
        </main>
        <Footer t={t.footer} />
      </div>
    </>
  );
}
