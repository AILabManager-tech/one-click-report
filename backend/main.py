"""
One-Click Report API — FastAPI Backend
Traitement des données, génération PDF, résumé IA
"""
import os
import io
import csv
import json
import re
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services.pdf_generator import generate_pdf
from services.ai_summary import generate_summary
from services.chart_renderer import render_charts
from services.parsers import get_parser, ParseResponse

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="One-Click Report API",
    version="3.1",
    description="Transform raw data into visual PDF reports with AI summaries",
    docs_url=None if os.getenv("PRODUCTION") else "/docs",
    redoc_url=None,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many requests"})


# CORS — origines strictes
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

REPORTS_DIR = Path("/tmp/reports")
REPORTS_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB (images haute résolution)
MAX_DATA_ROWS = 10_000
REPORT_ID_PATTERN = re.compile(r"^[a-f0-9]{8}$")
ALLOWED_CHART_TYPES = {"bar", "pie", "line"}


class ReportRequest(BaseModel):
    data: list[dict] = Field(..., description="Raw data rows")
    language: str = Field(default="fr", pattern="^(fr|en|es|de)$")
    context: str = Field(default="student", pattern="^(student|professional)$")
    title: str = Field(default="Mon Rapport", max_length=200)
    chart_types: list[str] = Field(default=["bar", "pie"])

    @field_validator("chart_types")
    @classmethod
    def validate_chart_types(cls, v: list[str]) -> list[str]:
        if len(v) > 5:
            raise ValueError("Maximum 5 chart types")
        for ct in v:
            if ct not in ALLOWED_CHART_TYPES:
                raise ValueError(f"Unknown chart type: {ct}")
        return v

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: list[dict]) -> list[dict]:
        if not v:
            raise ValueError("Data cannot be empty")
        if len(v) > MAX_DATA_ROWS:
            raise ValueError(f"Maximum {MAX_DATA_ROWS} rows")
        return v


class ReportResponse(BaseModel):
    report_id: str
    pdf_url: str
    charts: list[str]
    summary: str
    language: str
    created_at: str


def _validate_report_id(report_id: str) -> None:
    """Valide le format du report_id et empêche le path traversal."""
    if not REPORT_ID_PATTERN.match(report_id):
        raise HTTPException(status_code=400, detail="Invalid report ID")


@app.get("/health")
@limiter.limit("30/minute")
async def health(request: Request):
    return {
        "status": "operational",
        "version": "3.1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/reports/compile", response_model=ReportResponse)
@limiter.limit("10/minute")
async def compile_report(req: ReportRequest, request: Request):
    """Orchestre la génération complète du rapport en un appel."""
    report_id = uuid.uuid4().hex[:8]
    report_dir = REPORTS_DIR / report_id
    report_dir.mkdir(exist_ok=True)

    try:
        charts = await render_charts(
            data=req.data,
            chart_types=req.chart_types,
            output_dir=report_dir
        )

        summary = await generate_summary(
            data=req.data,
            language=req.language,
            context=req.context
        )

        pdf_path = await generate_pdf(
            data=req.data,
            charts=charts,
            summary=summary,
            title=req.title,
            language=req.language,
            output_dir=report_dir
        )

        return ReportResponse(
            report_id=report_id,
            pdf_url=f"/api/v1/reports/{report_id}/download",
            charts=[f"/api/v1/reports/{report_id}/chart/{i}" for i in range(len(charts))],
            summary=summary,
            language=req.language,
            created_at=datetime.now(timezone.utc).isoformat()
        )

    except Exception as e:
        logger.exception("Report generation failed for report_id=%s", report_id)
        raise HTTPException(status_code=500, detail="Report generation failed")


@app.get("/api/v1/reports/{report_id}/download")
@limiter.limit("20/minute")
async def download_report(report_id: str, request: Request):
    """Télécharge le PDF généré."""
    _validate_report_id(report_id)
    pdf_path = (REPORTS_DIR / report_id / "report.pdf").resolve()

    if not pdf_path.is_relative_to(REPORTS_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"report-{report_id}.pdf"
    )


@app.get("/api/v1/reports/{report_id}/chart/{index}")
@limiter.limit("30/minute")
async def get_chart(report_id: str, index: int, request: Request):
    """Récupère un graphique PNG individuel."""
    _validate_report_id(report_id)
    if index < 0 or index > 10:
        raise HTTPException(status_code=400, detail="Invalid chart index")

    chart_path = (REPORTS_DIR / report_id / f"chart_{index}.png").resolve()

    if not chart_path.is_relative_to(REPORTS_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")

    return FileResponse(chart_path, media_type="image/png")


@app.post("/api/v1/reports/parse")
@limiter.limit("10/minute")
async def parse_input(
    request: Request,
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    input_type: str | None = Form(None),
    options: str = Form("{}"),
):
    """Parse any input (Excel, PDF, image, pasted text) into structured data."""
    try:
        parsed_options = json.loads(options)
    except json.JSONDecodeError:
        parsed_options = {}

    # Determine content and filename
    if file and file.filename:
        content = await file.read(MAX_UPLOAD_SIZE + 1)
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 20MB)")
        filename = file.filename
        content_type = file.content_type or ""
    elif text:
        content = text.encode("utf-8")
        filename = "paste.txt"
        content_type = "text/plain"
    else:
        raise HTTPException(status_code=400, detail="No file or text provided")

    # Route to the correct parser
    parser = get_parser(filename, content_type)
    if parser is None:
        raise HTTPException(
            status_code=415,
            detail="Unsupported format. Use Excel, PDF, image, or paste text.",
        )

    try:
        result = await parser.parse(content, filename, parsed_options)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Parse failed for file=%s", filename)
        raise HTTPException(status_code=500, detail="Parsing failed")

    if not result.data and not result.needs_user_input:
        raise HTTPException(status_code=400, detail="No data found in input")

    return result.model_dump()


@app.post("/api/v1/reports/upload")
@limiter.limit("10/minute")
async def upload_data(file: UploadFile = File(...), request: Request = None):
    """Upload un fichier CSV/JSON et retourne les données parsées."""
    content = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    filename = file.filename or ""

    try:
        if filename.endswith(".json"):
            data = json.loads(content)
            if not isinstance(data, list):
                raise HTTPException(status_code=400, detail="JSON root must be an array")
        elif filename.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            data = []
            for i, row in enumerate(reader):
                if i >= MAX_DATA_ROWS:
                    break
                data.append(row)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported format. Use CSV or JSON."
            )
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid file content")

    if not data:
        raise HTTPException(status_code=400, detail="File contains no data")

    data = data[:MAX_DATA_ROWS]

    return {
        "rows": len(data),
        "columns": list(data[0].keys()) if data else [],
        "data": data,
    }
