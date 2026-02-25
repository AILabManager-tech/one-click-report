"""
Génération de résumé IA via l'API OpenAI (compatible LiteLLM).
Produit un résumé structuré des données dans la langue cible.
"""
import os
import json
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPTS = {
    "fr": "Tu es un analyste de données expert. Résume les données fournies de manière claire et professionnelle en français. Identifie les tendances clés, anomalies et recommandations.",
    "en": "You are an expert data analyst. Summarize the provided data clearly and professionally in English. Identify key trends, anomalies, and recommendations.",
    "es": "Eres un analista de datos experto. Resume los datos proporcionados de manera clara y profesional en español. Identifica tendencias clave, anomalías y recomendaciones.",
    "de": "Du bist ein erfahrener Datenanalyst. Fasse die bereitgestellten Daten klar und professionell auf Deutsch zusammen. Identifiziere wichtige Trends, Anomalien und Empfehlungen.",
}

CONTEXT_HINTS = {
    "student": "Adapte le ton pour un contexte académique/étudiant.",
    "professional": "Utilise un ton formel et business.",
}


async def generate_summary(data: list[dict], language: str, context: str) -> str:
    """Appelle l'API LLM pour générer un résumé des données."""
    if not OPENAI_API_KEY:
        return _fallback_summary(data, language)

    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
    context_hint = CONTEXT_HINTS.get(context, "")

    data_preview = json.dumps(data[:20], ensure_ascii=False, default=str)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": f"{system_prompt} {context_hint}"},
                        {"role": "user", "content": f"Analyse ces données et fournis un résumé structuré :\n\n{data_preview}"},
                    ],
                    "max_tokens": 800,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    except Exception:
        return _fallback_summary(data, language)


def _fallback_summary(data: list[dict], language: str) -> str:
    """Résumé statistique basique sans LLM (mode dégradé)."""
    n_rows = len(data)
    n_cols = len(data[0]) if data else 0
    cols = list(data[0].keys()) if data else []

    templates = {
        "fr": f"Jeu de données contenant {n_rows} entrées et {n_cols} colonnes ({', '.join(cols)}). Activez la clé API OpenAI pour un résumé IA complet.",
        "en": f"Dataset containing {n_rows} entries and {n_cols} columns ({', '.join(cols)}). Enable the OpenAI API key for a full AI summary.",
        "es": f"Conjunto de datos con {n_rows} entradas y {n_cols} columnas ({', '.join(cols)}). Active la clave API de OpenAI para un resumen completo.",
        "de": f"Datensatz mit {n_rows} Einträgen und {n_cols} Spalten ({', '.join(cols)}). Aktivieren Sie den OpenAI-API-Schlüssel für eine vollständige KI-Zusammenfassung.",
    }
    return templates.get(language, templates["en"])
