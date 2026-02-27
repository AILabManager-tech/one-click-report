"""
Tests for TextParser — CSV, TSV, markdown table, freeform detection.
"""
import pytest
from services.parsers.text_parser import TextParser


@pytest.fixture
def parser():
    return TextParser()


class TestSupports:
    def test_supports_txt(self, parser):
        assert parser.supports("data.txt", "") is True

    def test_supports_text_plain(self, parser):
        assert parser.supports("paste.txt", "text/plain") is True

    def test_supports_text_csv(self, parser):
        assert parser.supports("file", "text/csv") is True

    def test_rejects_xlsx(self, parser):
        assert parser.supports("data.xlsx", "") is False

    def test_rejects_pdf(self, parser):
        assert parser.supports("doc.pdf", "application/pdf") is False


class TestCSVDetection:
    @pytest.mark.asyncio
    async def test_basic_csv(self, parser, sample_csv_text):
        result = await parser.parse(sample_csv_text.encode(), "paste.txt")
        assert result.input_type == "paste"
        assert result.rows == 3
        assert result.confidence >= 0.9
        assert "name" in result.columns
        assert "age" in result.columns
        assert result.data[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_csv_with_quotes(self, parser):
        text = 'name,description\n"Smith, John","A person"\n"Doe, Jane","Another"\n'
        result = await parser.parse(text.encode(), "paste.txt")
        assert result.rows == 2
        assert result.data[0]["name"] == "Smith, John"

    @pytest.mark.asyncio
    async def test_large_csv(self, parser):
        header = "id,value\n"
        rows = "".join(f"{i},{i*10}\n" for i in range(500))
        result = await parser.parse((header + rows).encode(), "paste.txt")
        assert result.rows == 500


class TestTSVDetection:
    @pytest.mark.asyncio
    async def test_basic_tsv(self, parser, sample_tsv_text):
        result = await parser.parse(sample_tsv_text.encode(), "paste.txt")
        assert result.rows == 2
        assert result.confidence >= 0.85
        assert "name" in result.columns
        assert result.data[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_tsv_numbers(self, parser):
        text = "col1\tcol2\tcol3\n10\t20\t30\n40\t50\t60\n"
        result = await parser.parse(text.encode(), "paste.txt")
        assert result.rows == 2


class TestMarkdownTable:
    @pytest.mark.asyncio
    async def test_basic_markdown(self, parser, sample_markdown_table):
        result = await parser.parse(sample_markdown_table.encode(), "paste.txt")
        assert result.rows == 3
        assert result.confidence >= 0.8
        assert "Produit" in result.columns
        assert result.data[0]["Produit"] == "Pommes"

    @pytest.mark.asyncio
    async def test_markdown_without_separator(self, parser):
        text = "| A | B |\n| 1 | 2 |\n| 3 | 4 |\n"
        result = await parser.parse(text.encode(), "paste.txt")
        assert result.rows >= 2


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_text(self, parser):
        result = await parser.parse(b"", "paste.txt")
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_whitespace_only(self, parser):
        result = await parser.parse(b"   \n  \n  ", "paste.txt")
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_single_line(self, parser):
        """Single line = no structured data (no header+data)."""
        result = await parser.parse(b"just some text", "paste.txt")
        # Without an API key, freeform returns confidence 0
        assert result.confidence <= 0.1 or result.rows == 0
