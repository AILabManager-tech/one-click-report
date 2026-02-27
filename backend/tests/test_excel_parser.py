"""
Tests for ExcelParser — .xlsx and .xls support.
"""
import pytest
from services.parsers.excel_parser import ExcelParser


@pytest.fixture
def parser():
    return ExcelParser()


class TestSupports:
    def test_supports_xlsx(self, parser):
        assert parser.supports("data.xlsx", "") is True

    def test_supports_xls(self, parser):
        assert parser.supports("report.xls", "") is True

    def test_supports_xlsx_content_type(self, parser):
        assert parser.supports("file", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") is True

    def test_rejects_csv(self, parser):
        assert parser.supports("data.csv", "") is False

    def test_rejects_pdf(self, parser):
        assert parser.supports("doc.pdf", "") is False

    def test_supports_case_insensitive(self, parser):
        assert parser.supports("DATA.XLSX", "") is True


class TestParseXlsx:
    @pytest.mark.asyncio
    async def test_basic_xlsx(self, parser, sample_xlsx_bytes):
        result = await parser.parse(sample_xlsx_bytes, "test.xlsx")
        assert result.input_type == "excel"
        assert result.rows == 3
        assert result.confidence == 1.0
        assert "Produit" in result.columns
        assert "Quantité" in result.columns
        assert "Prix" in result.columns
        assert len(result.preview_rows) == 3

    @pytest.mark.asyncio
    async def test_xlsx_data_content(self, parser, sample_xlsx_bytes):
        result = await parser.parse(sample_xlsx_bytes, "test.xlsx")
        first_row = result.data[0]
        assert first_row["Produit"] == "Pommes"
        assert first_row["Quantité"] == 100
        assert first_row["Prix"] == 2.5

    @pytest.mark.asyncio
    async def test_multisheet_needs_user_input(self, parser, sample_xlsx_multisheet_bytes):
        result = await parser.parse(sample_xlsx_multisheet_bytes, "multi.xlsx")
        assert result.needs_user_input is True
        assert "sheets" in result.options
        assert "Ventes" in result.options["sheets"]
        assert "Achats" in result.options["sheets"]
        assert result.data == []

    @pytest.mark.asyncio
    async def test_multisheet_with_selection(self, parser, sample_xlsx_multisheet_bytes):
        result = await parser.parse(
            sample_xlsx_multisheet_bytes, "multi.xlsx", {"sheet": "Achats"}
        )
        assert result.needs_user_input is False
        assert result.rows == 1
        assert "Fournisseur" in result.columns
        assert result.data[0]["Fournisseur"] == "FournisseurA"

    @pytest.mark.asyncio
    async def test_invalid_magic_bytes(self, parser):
        with pytest.raises(ValueError, match="bad magic bytes"):
            await parser.parse(b"not a real xlsx file", "fake.xlsx")

    @pytest.mark.asyncio
    async def test_empty_sheet(self, parser):
        import openpyxl
        from io import BytesIO

        wb = openpyxl.Workbook()
        # Leave active sheet empty
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        content = buf.read()

        result = await parser.parse(content, "empty.xlsx")
        assert result.rows == 0
        assert result.data == []

    @pytest.mark.asyncio
    async def test_float_to_int_conversion(self, parser):
        """Excel stores integers as floats — verify conversion."""
        import openpyxl
        from io import BytesIO

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["id", "value"])
        ws.append([1.0, 42.0])  # Floats that are really ints
        ws.append([2.0, 3.14])  # Actual float

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        result = await parser.parse(buf.read(), "ints.xlsx")
        assert result.data[0]["id"] == 1  # int, not 1.0
        assert result.data[1]["value"] == 3.14  # stays float
