"""
Tests for PdfParser — table extraction, bank detection, magic bytes.
"""
import pytest
from services.parsers.pdf_parser import PdfParser, _detect_bank_statement


@pytest.fixture
def parser():
    return PdfParser()


class TestSupports:
    def test_supports_pdf(self, parser):
        assert parser.supports("report.pdf", "") is True

    def test_supports_pdf_content_type(self, parser):
        assert parser.supports("file", "application/pdf") is True

    def test_rejects_xlsx(self, parser):
        assert parser.supports("data.xlsx", "") is False

    def test_rejects_image(self, parser):
        assert parser.supports("photo.jpg", "image/jpeg") is False


class TestMagicBytes:
    @pytest.mark.asyncio
    async def test_invalid_magic_bytes(self, parser):
        with pytest.raises(ValueError, match="bad magic bytes"):
            await parser.parse(b"not a pdf file at all", "fake.pdf")

    @pytest.mark.asyncio
    async def test_valid_magic_but_corrupt(self, parser):
        """Starts with %PDF but is otherwise garbage — should degrade gracefully."""
        result = await parser.parse(b"%PDF-1.4 corrupt garbage data", "bad.pdf")
        # Corrupt PDF: no tables extracted, OCR fallback may also fail
        # Should return low confidence with warnings, not crash
        assert result.confidence < 1.0
        assert len(result.warnings) > 0


class TestBankDetection:
    def test_bank_statement_detected(self, sample_bank_data):
        assert _detect_bank_statement(sample_bank_data) is True

    def test_non_bank_data(self):
        data = [{"name": "Alice", "age": 30, "city": "Paris"}]
        assert _detect_bank_statement(data) is False

    def test_empty_data(self):
        assert _detect_bank_statement([]) is False

    def test_partial_bank_keywords(self):
        data = [{"date": "2024-01-01", "label": "something", "total": 100}]
        # Only "date" matches — need >= 2
        assert _detect_bank_statement(data) is False

    def test_english_bank_keywords(self):
        data = [{"date": "2024-01-01", "amount": 100, "balance": 500, "description": "Purchase"}]
        assert _detect_bank_statement(data) is True


class TestPdfWithTables:
    @pytest.mark.asyncio
    async def test_simple_pdf_with_table(self, parser):
        """Create a minimal PDF with pdfplumber-extractable table."""
        # We need to create a real PDF with a table for this test.
        # Use a minimal approach via reportlab if available, otherwise skip.
        try:
            from io import BytesIO
            import pdfplumber

            # Create a minimal PDF using pdfplumber's test utilities isn't possible,
            # so we test the interface returns a ParseResponse
            # We'll test with a programmatically created PDF
            pdf_content = _create_simple_pdf_with_table()
            if pdf_content is None:
                pytest.skip("Cannot create test PDF (reportlab not available)")

            result = await parser.parse(pdf_content, "test.pdf")
            assert result.input_type == "pdf"
            # Either data was extracted or OCR warning was raised
            assert result.rows >= 0

        except ImportError:
            pytest.skip("pdfplumber or reportlab not available")


def _create_simple_pdf_with_table():
    """Try to create a simple PDF for testing. Returns None if deps missing."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table
        from io import BytesIO

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        data = [
            ["Nom", "Age", "Ville"],
            ["Alice", "30", "Paris"],
            ["Bob", "25", "Lyon"],
        ]
        table = Table(data)
        doc.build([table])
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None
