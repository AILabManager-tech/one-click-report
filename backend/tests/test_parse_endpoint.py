"""
Tests for the /api/v1/reports/parse endpoint (integration tests).
Uses mocks for pdf_generator and chart_renderer to avoid matplotlib/weasyprint deps.
"""
import io
import json
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

# Mock heavy dependencies before importing main
mock_pdf = MagicMock()
mock_pdf.generate_pdf = AsyncMock(return_value="/tmp/fake.pdf")
sys.modules["services.pdf_generator"] = mock_pdf

mock_charts = MagicMock()
mock_charts.render_charts = AsyncMock(return_value=[])
sys.modules["services.chart_renderer"] = mock_charts

mock_summary = MagicMock()
mock_summary.generate_summary = AsyncMock(return_value="Mock summary")
sys.modules["services.ai_summary"] = mock_summary

from httpx import AsyncClient, ASGITransport
from main import app, limiter

# Disable rate limiting for tests
limiter.enabled = False


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest_asyncio.fixture
async def client(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestParseEndpoint:
    @pytest.mark.asyncio
    async def test_no_input_returns_400(self, client):
        resp = await client.post("/api/v1/reports/parse")
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_xlsx_upload(self, client, sample_xlsx_bytes):
        files = {"file": ("test.xlsx", io.BytesIO(sample_xlsx_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        resp = await client.post("/api/v1/reports/parse", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["input_type"] == "excel"
        assert data["rows"] == 3
        assert data["confidence"] == 1.0
        assert "Produit" in data["columns"]

    @pytest.mark.asyncio
    async def test_xlsx_multisheet_needs_input(self, client, sample_xlsx_multisheet_bytes):
        files = {"file": ("multi.xlsx", io.BytesIO(sample_xlsx_multisheet_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        resp = await client.post("/api/v1/reports/parse", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_user_input"] is True
        assert "Ventes" in data["options"]["sheets"]

    @pytest.mark.asyncio
    async def test_xlsx_with_sheet_option(self, client, sample_xlsx_multisheet_bytes):
        files = {"file": ("multi.xlsx", io.BytesIO(sample_xlsx_multisheet_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        resp = await client.post(
            "/api/v1/reports/parse",
            files=files,
            data={"options": json.dumps({"sheet": "Achats"})},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_user_input"] is False
        assert data["rows"] == 1
        assert "Fournisseur" in data["columns"]

    @pytest.mark.asyncio
    async def test_text_paste_csv(self, client, sample_csv_text):
        resp = await client.post(
            "/api/v1/reports/parse",
            data={"text": sample_csv_text},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["input_type"] == "paste"
        assert data["rows"] == 3
        assert "name" in data["columns"]

    @pytest.mark.asyncio
    async def test_text_paste_tsv(self, client, sample_tsv_text):
        resp = await client.post(
            "/api/v1/reports/parse",
            data={"text": sample_tsv_text},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["rows"] == 2

    @pytest.mark.asyncio
    async def test_text_paste_markdown(self, client, sample_markdown_table):
        resp = await client.post(
            "/api/v1/reports/parse",
            data={"text": sample_markdown_table},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["rows"] == 3
        assert "Produit" in data["columns"]

    @pytest.mark.asyncio
    async def test_unsupported_format_returns_415(self, client):
        files = {"file": ("data.parquet", io.BytesIO(b"some data"), "application/octet-stream")}
        resp = await client.post("/api/v1/reports/parse", files=files)
        assert resp.status_code == 415

    @pytest.mark.asyncio
    async def test_invalid_magic_bytes_returns_400(self, client):
        files = {"file": ("fake.xlsx", io.BytesIO(b"not excel data"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        resp = await client.post("/api/v1/reports/parse", files=files)
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_pdf_returns_400(self, client):
        files = {"file": ("fake.pdf", io.BytesIO(b"not a pdf"), "application/pdf")}
        resp = await client.post("/api/v1/reports/parse", files=files)
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_parse_response_structure(self, client, sample_xlsx_bytes):
        """Verify the full ParseResponse structure."""
        files = {"file": ("test.xlsx", io.BytesIO(sample_xlsx_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        resp = await client.post("/api/v1/reports/parse", files=files)
        data = resp.json()
        # All required fields present
        assert "input_type" in data
        assert "data" in data
        assert "rows" in data
        assert "columns" in data
        assert "confidence" in data
        assert "warnings" in data
        assert "preview_rows" in data
        assert "needs_user_input" in data
        assert "options" in data
        # Types
        assert isinstance(data["data"], list)
        assert isinstance(data["columns"], list)
        assert isinstance(data["confidence"], (int, float))
        assert isinstance(data["warnings"], list)
        assert isinstance(data["preview_rows"], list)
        assert isinstance(data["needs_user_input"], bool)


class TestUploadEndpointRetrocompat:
    """Verify the old /upload endpoint still works."""

    @pytest.mark.asyncio
    async def test_csv_upload(self, client, sample_csv_text):
        files = {"file": ("data.csv", io.BytesIO(sample_csv_text.encode()), "text/csv")}
        resp = await client.post("/api/v1/reports/upload", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["rows"] == 3
        assert "name" in data["columns"]

    @pytest.mark.asyncio
    async def test_json_upload(self, client):
        content = json.dumps([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        files = {"file": ("data.json", io.BytesIO(content.encode()), "application/json")}
        resp = await client.post("/api/v1/reports/upload", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["rows"] == 2

    @pytest.mark.asyncio
    async def test_upload_unsupported_format(self, client):
        files = {"file": ("data.xml", io.BytesIO(b"<data/>"), "text/xml")}
        resp = await client.post("/api/v1/reports/upload", files=files)
        assert resp.status_code == 400


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "operational"
