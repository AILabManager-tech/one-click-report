"use client";

import { useParams } from "next/navigation";
import dynamic from "next/dynamic";
import type { Language } from "@/types/report";
import { getDictionary } from "../i18n";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Footer from "@/components/Footer";
import AdUnit from "@/components/AdUnit";
import JsonLd from "@/components/JsonLd";

const ReportForm = dynamic(() => import("@/components/ReportForm"), {
  loading: () => <div className="py-20 text-center text-gray-400">...</div>,
});
const FAQ = dynamic(() => import("@/components/FAQ"), {
  loading: () => <div className="py-20" />,
});

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
          <AdUnit slot="SLOT_AFTER_HERO" format="horizontal" className="mx-auto max-w-4xl px-4 py-4" />
          <Features t={t.features} />
          <ReportForm t={t.form} lang={locale} />
          <AdUnit slot="SLOT_AFTER_FORM" format="auto" className="mx-auto max-w-3xl px-4 py-6" />
          <FAQ items={(t as any).faq} title={(t as any).faq_title} />
        </main>
        <Footer t={t.footer} />
      </div>
    </>
  );
}
