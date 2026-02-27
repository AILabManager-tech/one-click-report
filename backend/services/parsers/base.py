"""
Base parser interface and shared response model.
All parsers inherit from BaseParser and return ParseResponse.
"""
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class ParseResponse(BaseModel):
    input_type: str = Field(..., description="excel, pdf, image, paste")
    data: list[dict] = Field(default_factory=list, description="Structured data rows")
    rows: int = 0
    columns: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
    preview_rows: list[dict] = Field(default_factory=list, description="First 10 rows")
    needs_user_input: bool = False
    options: dict = Field(default_factory=dict)


class BaseParser(ABC):
    """Abstract base class for all input parsers."""

    @abstractmethod
    async def parse(
        self, content: bytes, filename: str, options: dict | None = None
    ) -> ParseResponse:
        """Parse raw content into structured data."""
        ...

    @abstractmethod
    def supports(self, filename: str, content_type: str) -> bool:
        """Return True if this parser handles the given file type."""
        ...

    @staticmethod
    def _preview(data: list[dict], n: int = 10) -> list[dict]:
        """Return first n rows as preview."""
        return data[:n]

    @staticmethod
    def _detect_columns(data: list[dict]) -> list[str]:
        """Extract column names from data."""
        if not data:
            return []
        return list(data[0].keys())
