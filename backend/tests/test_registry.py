"""
Tests for parser registry — routing logic.
"""
from services.parsers import get_parser
from services.parsers.excel_parser import ExcelParser
from services.parsers.pdf_parser import PdfParser
from services.parsers.image_parser import ImageParser
from services.parsers.text_parser import TextParser


class TestGetParser:
    def test_xlsx_routes_to_excel(self):
        p = get_parser("data.xlsx", "")
        assert isinstance(p, ExcelParser)

    def test_xls_routes_to_excel(self):
        p = get_parser("old.xls", "")
        assert isinstance(p, ExcelParser)

    def test_pdf_routes_to_pdf(self):
        p = get_parser("report.pdf", "")
        assert isinstance(p, PdfParser)

    def test_jpg_routes_to_image(self):
        p = get_parser("photo.jpg", "")
        assert isinstance(p, ImageParser)

    def test_png_routes_to_image(self):
        p = get_parser("screen.png", "image/png")
        assert isinstance(p, ImageParser)

    def test_heic_routes_to_image(self):
        p = get_parser("IMG.HEIC", "")
        assert isinstance(p, ImageParser)

    def test_txt_routes_to_text(self):
        p = get_parser("paste.txt", "text/plain")
        assert isinstance(p, TextParser)

    def test_csv_content_type_routes_to_text(self):
        p = get_parser("file", "text/csv")
        assert isinstance(p, TextParser)

    def test_unknown_returns_none(self):
        p = get_parser("data.parquet", "application/octet-stream")
        assert p is None

    def test_unknown_extension_returns_none(self):
        p = get_parser("archive.zip", "")
        assert p is None
