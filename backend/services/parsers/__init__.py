"""
Parser registry — routes files to the correct parser based on extension/content type.
"""
from .base import BaseParser, ParseResponse
from .excel_parser import ExcelParser
from .text_parser import TextParser
from .pdf_parser import PdfParser
from .image_parser import ImageParser

# Registry: instantiated parsers checked in order
_PARSERS: list[BaseParser] = [
    ExcelParser(),
    PdfParser(),
    ImageParser(),
    TextParser(),  # Last: catches text/plain and paste
]


def register_parser(parser: BaseParser) -> None:
    """Add a parser to the registry."""
    _PARSERS.append(parser)


def get_parser(filename: str, content_type: str) -> BaseParser | None:
    """Return the first parser that supports this file type."""
    for parser in _PARSERS:
        if parser.supports(filename, content_type):
            return parser
    return None


__all__ = ["BaseParser", "ParseResponse", "get_parser", "register_parser"]
