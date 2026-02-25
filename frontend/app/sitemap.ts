import type { MetadataRoute } from "next";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://frontend-ten-peach-80.vercel.app";
const locales = ["fr", "en", "es", "de"];

export default function sitemap(): MetadataRoute.Sitemap {
  const entries: MetadataRoute.Sitemap = [];

  // Page d'accueil pour chaque langue
  for (const locale of locales) {
    const languages: Record<string, string> = {};
    for (const l of locales) {
      languages[l] = `${BASE_URL}/${l}`;
    }
    languages["x-default"] = `${BASE_URL}/fr`;

    entries.push({
      url: `${BASE_URL}/${locale}`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: locale === "fr" ? 1.0 : 0.9,
      alternates: { languages },
    });
  }

  // Page racine (redirect)
  entries.push({
    url: BASE_URL,
    lastModified: new Date(),
    changeFrequency: "weekly",
    priority: 0.5,
  });

  return entries;
}
