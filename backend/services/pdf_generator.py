"""
Génération PDF via WeasyPrint.
Compile les données, graphiques et résumé IA en un document PDF.
"""
import base64
from html import escape
from pathlib import Path
from weasyprint import HTML


LABELS = {
    "fr": {"title": "Rapport", "summary": "Résumé IA", "data": "Données", "generated": "Généré le"},
    "en": {"title": "Report", "summary": "AI Summary", "data": "Data", "generated": "Generated on"},
    "es": {"title": "Reporte", "summary": "Resumen IA", "data": "Datos", "generated": "Generado el"},
    "de": {"title": "Bericht", "summary": "KI-Zusammenfassung", "data": "Daten", "generated": "Erstellt am"},
}


def _build_html(data: list[dict], charts: list[Path], summary: str,
                title: str, language: str) -> str:
    """Construit le HTML du rapport pour conversion PDF."""
    labels = LABELS.get(language, LABELS["en"])

    charts_html = ""
    for chart_path in charts:
        if chart_path.exists():
            b64 = base64.b64encode(chart_path.read_bytes()).decode()
            charts_html += f'<img src="data:image/png;base64,{b64}" style="max-width:100%;margin:16px 0;" />'

    columns = list(data[0].keys()) if data else []
    header_row = "".join(f"<th>{escape(str(col))}</th>" for col in columns)
    body_rows = ""
    for row in data[:50]:
        cells = "".join(f"<td>{escape(str(row.get(col, '')))}</td>" for col in columns)
        body_rows += f"<tr>{cells}</tr>"

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="{language}">
<head>
<meta charset="utf-8"/>
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; color: #1a1a2e; }}
  h1 {{ color: #16213e; border-bottom: 3px solid #0f3460; padding-bottom: 8px; }}
  h2 {{ color: #0f3460; margin-top: 32px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 11px; }}
  th {{ background: #0f3460; color: white; padding: 8px 12px; text-align: left; }}
  td {{ padding: 6px 12px; border-bottom: 1px solid #e0e0e0; }}
  tr:nth-child(even) {{ background: #f8f9fa; }}
  .summary {{ background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 16px 0; line-height: 1.6; }}
  .footer {{ margin-top: 40px; font-size: 10px; color: #888; text-align: center; }}
</style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <p class="footer">{labels['generated']} {now} UTC</p>

  <h2>{labels['summary']}</h2>
  <div class="summary">{escape(summary)}</div>

  {charts_html}

  <h2>{labels['data']}</h2>
  <table>
    <thead><tr>{header_row}</tr></thead>
    <tbody>{body_rows}</tbody>
  </table>

  <div class="footer">One-Click Report AI v3.1</div>
</body>
</html>"""


async def generate_pdf(data: list[dict], charts: list[Path], summary: str,
                       title: str, language: str, output_dir: Path) -> Path:
    """Génère le PDF final et retourne le chemin du fichier."""
    html_content = _build_html(data, charts, summary, title, language)
    pdf_path = output_dir / "report.pdf"
    HTML(string=html_content).write_pdf(str(pdf_path))
    return pdf_path
