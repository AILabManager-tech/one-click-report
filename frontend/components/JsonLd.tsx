import type { Language } from "@/types/report";

interface JsonLdProps {
  lang: Language;
}

export default function JsonLd({ lang }: JsonLdProps) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "One-Click Report AI",
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web, iOS, Android",
    inLanguage: [lang],
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
      description: "Freemium instant PDF report generator with AI summary",
    },
    featureList: [
      "AI-powered report summary",
      "Interactive charts (bar, pie, line)",
      "PDF export with professional layout",
      "Multilingual support (FR, EN, ES, DE)",
    ],
  };

  const howTo = {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name: "How to generate an instant report",
    step: [
      {
        "@type": "HowToStep",
        position: 1,
        name: "Upload your data",
        text: "Upload a CSV or JSON file with your raw data.",
      },
      {
        "@type": "HowToStep",
        position: 2,
        name: "Configure your report",
        text: "Choose title, context (student/professional), and chart types.",
      },
      {
        "@type": "HowToStep",
        position: 3,
        name: "Generate and download",
        text: "Click generate to get your PDF with AI summary and charts.",
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(howTo) }}
      />
    </>
  );
}
