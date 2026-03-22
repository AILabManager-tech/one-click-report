# One-Click Report AI — Rapports visuels PDF en un clic

Transformez vos données brutes en rapports PDF visuels avec résumés IA. Supporte 4 langues (FR/EN/ES/DE) et plusieurs formats d'entrée (Excel, PDF, images, collage texte).

> Développé par [Mark Systems](https://github.com/AILabManager-tech/mark-systems).

## Fonctionnalités

- Upload multi-format : Excel (.xlsx/.xls), PDF, images (OCR), collage texte
- Génération de rapports PDF avec graphiques (WeasyPrint + Matplotlib)
- Résumés IA via OpenAI
- Interface web 4 langues (FR / EN / ES / DE)
- Graphiques interactifs (Recharts)
- Rate limiting (SlowAPI)
- Déploiement Docker (backend + frontend + nginx)

## Architecture

```
one-click-report/
├── backend/           # FastAPI (Python)
│   ├── main.py        # API endpoints
│   ├── services/      # Logique métier (parsing, génération PDF, IA)
│   ├── templates/     # Templates de rapports
│   └── tests/         # Tests backend
├── frontend/          # Next.js 14 (TypeScript)
│   ├── app/           # Pages
│   ├── components/    # Composants UI
│   ├── locales/       # Traductions (fr, en, es, de)
│   └── services/      # Appels API
├── docker-compose.yml # Orchestration services
└── nginx-report.conf  # Reverse proxy
```

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | FastAPI, Python 3 |
| PDF | WeasyPrint + Matplotlib |
| Parsing | openpyxl, pdfplumber, pytesseract (OCR), Pillow |
| IA | OpenAI API (résumés) |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Graphiques | Recharts |
| i18n | 4 langues (fr, en, es, de) |
| Infra | Docker Compose, Nginx |
| BDD | Supabase (optionnel) |

## Démarrage

### Docker (recommandé)

```bash
cp manifest.example.json manifest.json
# Éditer manifest.json avec vos clés API

docker compose up --build
# Frontend : http://localhost:3001
# Backend  : http://localhost:8081
```

### Développement local

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8080

# Frontend
cd frontend
npm install
npm run dev
```

## Déploiement

Production sur IONOS avec Docker Compose + Nginx reverse proxy.

URL : [report.marksystems.ca](https://report.marksystems.ca)

## Licence

Propriétaire — Mark Systems © 2026

---

# One-Click Report AI — Visual PDF Reports in One Click

Transform raw data into visual PDF reports with AI summaries. Supports 4 languages (FR/EN/ES/DE) and multiple input formats (Excel, PDF, images, text paste).

> Built by [Mark Systems](https://github.com/AILabManager-tech/mark-systems).

## Features

- Multi-format upload: Excel (.xlsx/.xls), PDF, images (OCR), text paste
- PDF report generation with charts (WeasyPrint + Matplotlib)
- AI summaries via OpenAI
- Web interface in 4 languages (FR / EN / ES / DE)
- Interactive charts (Recharts)
- Rate limiting (SlowAPI)
- Docker deployment (backend + frontend + nginx)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3 |
| PDF | WeasyPrint + Matplotlib |
| Parsing | openpyxl, pdfplumber, pytesseract (OCR), Pillow |
| AI | OpenAI API (summaries) |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Charts | Recharts |
| i18n | 4 languages (fr, en, es, de) |
| Infra | Docker Compose, Nginx |
| DB | Supabase (optional) |

## Getting Started

### Docker (recommended)

```bash
cp manifest.example.json manifest.json
# Edit manifest.json with your API keys

docker compose up --build
# Frontend: http://localhost:3001
# Backend:  http://localhost:8081
```

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8080

# Frontend
cd frontend
npm install
npm run dev
```

## Deployment

Production on IONOS with Docker Compose + Nginx reverse proxy.

URL: [report.marksystems.ca](https://report.marksystems.ca)

## License

Proprietary — Mark Systems © 2026
