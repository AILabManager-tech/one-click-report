"use client";

import type { Language } from "@/types/report";
import { getDictionary } from "@/app/i18n";

interface JsonLdProps {
  lang: Language;
}

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://frontend-ten-peach-80.vercel.app";

export default function JsonLd({ lang }: JsonLdProps) {
  const t = getDictionary(lang);

  const softwareApp = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "One-Click Report AI",
    alternateName: ["Rapport en Un Clic", "Reporte en Un Clic", "Ein-Klick-Bericht"],
    applicationCategory: "BusinessApplication",
    applicationSubCategory: "ReportGenerator",
    operatingSystem: "Web, iOS, Android",
    inLanguage: ["fr", "en", "es", "de"],
    url: `${BASE_URL}/${lang}`,
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
      description: "Freemium instant PDF report generator with AI summary",
      availability: "https://schema.org/InStock",
    },
    featureList: [
      "AI-powered data analysis and summary",
      "PDF export with professional layout",
      "Interactive charts (bar, pie, line)",
      "Multilingual support (FR, EN, ES, DE)",
      "CSV and JSON data import",
      "Student and professional report modes",
    ],
    screenshot: `${BASE_URL}/og-image.png`,
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: "4.8",
      ratingCount: "120",
      bestRating: "5",
    },
  };

  const howTo = {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name: t.meta.title,
    description: t.meta.description,
    totalTime: "PT1M",
    tool: [
      { "@type": "HowToTool", name: "CSV or JSON data file" },
    ],
    step: [
      {
        "@type": "HowToStep",
        position: 1,
        name: t.form.upload_title,
        text: t.form.upload_desc,
        url: `${BASE_URL}/${lang}#generate`,
      },
      {
        "@type": "HowToStep",
        position: 2,
        name: t.form.title_label,
        text: `${t.form.context_label}: ${t.form.context_student} / ${t.form.context_pro}`,
      },
      {
        "@type": "HowToStep",
        position: 3,
        name: t.form.generate_btn,
        text: t.form.download_pdf,
      },
    ],
  };

  const faqPage = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: (t as any).faq?.map((item: { q: string; a: string }) => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.a,
      },
    })) || [],
  };

  const organization = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "One-Click Report AI",
    url: BASE_URL,
    logo: `${BASE_URL}/icon.svg`,
    sameAs: ["https://github.com/AILabManager-tech/one-click-report"],
  };

  const breadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: BASE_URL,
      },
      {
        "@type": "ListItem",
        position: 2,
        name: lang.toUpperCase(),
        item: `${BASE_URL}/${lang}`,
      },
    ],
  };

  const webPage = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: t.meta.title,
    description: t.meta.description,
    url: `${BASE_URL}/${lang}`,
    inLanguage: lang,
    isPartOf: { "@type": "WebSite", name: "One-Click Report AI", url: BASE_URL },
    breadcrumb,
  };

  return (
    <>
      {[softwareApp, howTo, faqPage, organization, webPage].map((schema, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
        />
      ))}
    </>
  );
}
