# One-Click Report AI — Architecture v3.1

## Flux de données

```
┌──────────────┐     ┌──────────────────────────────────────┐
│  Next.js 14  │     │       FastAPI Backend (Fly.io)       │
│   (Vercel)   │     │                                      │
│              │────>│  POST /api/v1/reports/compile         │
│  Upload CSV  │     │    ├─ Validation Pydantic             │
│  ou JSON     │     │    ├─ render_charts() → PNG           │
│              │     │    ├─ generate_summary() → LLM API    │
│              │<────│    └─ generate_pdf() → WeasyPrint     │
│  Affichage   │     │                                      │
│  + Download  │     │  GET /api/v1/reports/{id}/download    │
└──────────────┘     └──────────────────────────────────────┘
```

## Stack

| Composant | Technologie | Déploiement |
|-----------|-------------|-------------|
| Frontend | Next.js 14, Tailwind CSS, TypeScript | Vercel |
| Backend | FastAPI, WeasyPrint, matplotlib | Fly.io (Docker) |
| IA | OpenAI API (gpt-4o-mini) | API externe |
| Auth | Supabase (Google OAuth + Magic Link) | Supabase Cloud |

## Fichier unique de configuration

Tout est centralisé dans `manifest.json` :
- Secrets (API keys, tokens)
- SEO metadata (4 langues)
- Configuration projet
- Paramètres de déploiement

## Commandes

```bash
# Vérification (dry-run)
bash deploy.sh --check

# Tout déployer
bash deploy.sh

# Backend seul
bash deploy.sh --backend-only

# Frontend seul
bash deploy.sh --frontend-only
```

## SEO

- Schema.org : SoftwareApplication + HowTo
- JSON-LD injecté dynamiquement
- Meta tags en 4 langues (FR/EN/ES/DE)
- Hreflang via sélecteur de langue client-side

## Gates

| Gate | Critère | Statut |
|------|---------|--------|
| W-01 | JSX/HTML valide (Tailwind, pas de style inline) | PASS |
| W-02 | Responsive Mobile-First (375px+) | PASS |
| W-03 | i18n FR/EN/ES/DE | PASS |
| C-01 | TypeScript interfaces (ReportInput/Output) | PASS |
| C-02 | generateReport() implémenté | PASS |
| A-01 | Infrastructure Vercel + Fly.io | PASS |
| A-02 | SEO Schema.org + meta multilingue | PASS |

**Score: 7/7 = 10.0** (seuil: 8.0)
