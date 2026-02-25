import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { notFound } from "next/navigation";
import { locales, getDictionary } from "../i18n";
import "../globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://oneclick.report";

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
  const og = (t as any).og || t.meta;

  const languages: Record<string, string> = {};
  for (const l of locales) {
    languages[l] = `${BASE_URL}/${l}`;
  }
  languages["x-default"] = `${BASE_URL}/fr`;

  return {
    title: t.meta.title,
    description: t.meta.description,
    keywords: (t.meta as any).keywords,
    metadataBase: new URL(BASE_URL),
    alternates: {
      canonical: `/${locale}`,
      languages,
    },
    openGraph: {
      type: "website",
      locale: locale === "fr" ? "fr_FR" : locale === "en" ? "en_US" : locale === "es" ? "es_ES" : "de_DE",
      url: `${BASE_URL}/${locale}`,
      title: og.title,
      description: og.description,
      siteName: "One-Click Report AI",
      images: [
        {
          url: `${BASE_URL}/og-image.png`,
          width: 1200,
          height: 630,
          alt: og.image_alt || t.meta.title,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: og.title,
      description: og.description,
      images: [`${BASE_URL}/og-image.png`],
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        "max-video-preview": -1,
        "max-image-preview": "large",
        "max-snippet": -1,
      },
    },
    other: {
      "google-site-verification": process.env.NEXT_PUBLIC_GOOGLE_VERIFICATION || "",
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
    <html lang={params.locale} className={inter.variable} suppressHydrationWarning>
      <head>
        {locales.map((l) => (
          <link key={l} rel="alternate" hrefLang={l} href={`${BASE_URL}/${l}`} />
        ))}
        <link rel="alternate" hrefLang="x-default" href={`${BASE_URL}/fr`} />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7824408396443112"
          crossOrigin="anonymous"
        />
      </head>
      <body className="font-sans">
        {children}
      </body>
    </html>
  );
}
