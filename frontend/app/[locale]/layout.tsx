import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { locales, getDictionary } from "../i18n";
import "../globals.css";

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: { locale: string };
}): Promise<Metadata> {
  const { locale } = params;
  const t = getDictionary(locale);

  const alternates: Record<string, string> = {};
  for (const l of locales) {
    alternates[l] = `/${l}`;
  }

  return {
    title: t.meta.title,
    description: t.meta.description,
    alternates: {
      canonical: `/${locale}`,
      languages: alternates,
    },
  };
}

export default function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  if (!locales.includes(params.locale as any)) {
    notFound();
  }

  return (
    <html lang={params.locale} suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
        {locales.map((l) => (
          <link key={l} rel="alternate" hrefLang={l} href={`/${l}`} />
        ))}
        <link rel="alternate" hrefLang="x-default" href="/fr" />
      </head>
      <body className="font-sans">{children}</body>
    </html>
  );
}
