import type { Language } from "@/types/report";

import fr from "@/locales/fr.json";
import en from "@/locales/en.json";
import es from "@/locales/es.json";
import de from "@/locales/de.json";

export const locales: Language[] = ["fr", "en", "es", "de"];
export const defaultLocale: Language = "fr";

const dictionaries = { fr, en, es, de } as const;

export function getDictionary(locale: string) {
  const lang = locales.includes(locale as Language) ? (locale as Language) : defaultLocale;
  return dictionaries[lang];
}

export function isValidLocale(locale: string): locale is Language {
  return locales.includes(locale as Language);
}
