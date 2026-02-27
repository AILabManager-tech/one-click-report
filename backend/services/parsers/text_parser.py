"""
Text parser — handles pasted text (CSV, TSV, markdown tables, freeform).
Detects structured formats first, falls back to GPT-4o-mini for freeform.
"""
import csv
import io
import json
import os
import re
import logging

import httpx

from .base import BaseParser, ParseResponse

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MAX_TEXT_SIZE = 500_000  # ~500KB of text
MAX_ROWS = 10_000


class TextParser(BaseParser):
    def supports(self, filename: str, content_type: str) -> bool:
        return filename.lower().endswith(".txt") or content_type in {
            "text/plain",
            "text/csv",
            "text/tab-separated-values",
        }

    async def parse(
        self, content: bytes, filename: str, options: dict | None = None
    ) -> ParseResponse:
        text = content[:MAX_TEXT_SIZE].decode("utf-8", errors="replace").strip()
        if not text:
            return ParseResponse(input_type="paste", confidence=0.0, warnings=["Empty input"])

        # Try structured formats in order
        result = _try_csv(text)
        if result:
            return result

        result = _try_tsv(text)
        if result:
            return result

        result = _try_markdown_table(text)
        if result:
            return result

        # Freeform → LLM structuring
        return await _llm_structure(text)


def _try_csv(text: str) -> ParseResponse | None:
    """Try parsing as CSV (comma-separated)."""
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(text[:2048])
        if dialect.delimiter != ",":
            return None
    except csv.Error:
        # Check if it looks like CSV manually
        lines = text.strip().split("\n")
        if len(lines) < 2 or "," not in lines[0]:
            return None

    try:
        reader = csv.DictReader(io.StringIO(text))
        data = []
        for i, row in enumerate(reader):
            if i >= MAX_ROWS:
                break
            data.append(dict(row))

        if not data:
            return None

        return ParseResponse(
            input_type="paste",
            data=data,
            rows=len(data),
            columns=list(data[0].keys()),
            confidence=0.95,
            preview_rows=data[:10],
        )
    except Exception:
        return None


def _try_tsv(text: str) -> ParseResponse | None:
    """Try parsing as tab-separated values."""
    lines = text.strip().split("\n")
    if len(lines) < 2:
        return None

    # Check if tabs are present consistently
    tab_counts = [line.count("\t") for line in lines[:5]]
    if not tab_counts or tab_counts[0] == 0:
        return None
    if not all(c == tab_counts[0] for c in tab_counts):
        return None

    try:
        reader = csv.DictReader(io.StringIO(text), delimiter="\t")
        data = []
        for i, row in enumerate(reader):
            if i >= MAX_ROWS:
                break
            data.append(dict(row))

        if not data:
            return None

        return ParseResponse(
            input_type="paste",
            data=data,
            rows=len(data),
            columns=list(data[0].keys()),
            confidence=0.9,
            preview_rows=data[:10],
        )
    except Exception:
        return None


def _try_markdown_table(text: str) -> ParseResponse | None:
    """Try parsing a markdown-style table (| col1 | col2 |)."""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if len(lines) < 3:
        return None

    # Must have pipes
    if "|" not in lines[0]:
        return None

    # Parse header
    header_line = lines[0].strip("|").strip()
    headers = [h.strip() for h in header_line.split("|") if h.strip()]
    if not headers:
        return None

    # Skip separator line (---| or ---|---)
    start = 1
    if re.match(r"^[\s|:-]+$", lines[1]):
        start = 2

    data = []
    for line in lines[start : start + MAX_ROWS]:
        if not line or "|" not in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        row = {}
        for i, h in enumerate(headers):
            row[h] = cells[i] if i < len(cells) else ""
        data.append(row)

    if not data:
        return None

    return ParseResponse(
        input_type="paste",
        data=data,
        rows=len(data),
        columns=headers,
        confidence=0.85,
        preview_rows=data[:10],
    )


async def _llm_structure(text: str) -> ParseResponse:
    """Use GPT-4o-mini to structure freeform text into JSON data."""
    if not OPENAI_API_KEY:
        return ParseResponse(
            input_type="paste",
            confidence=0.0,
            warnings=["Freeform text detected but no AI key configured for structuring."],
        )

    # Limit text sent to LLM
    preview_text = text[:4000]

    prompt = (
        "Extract structured data from the following text. "
        "Return ONLY a JSON array of objects with consistent keys. "
        "If the text contains a table, list, or any structured data, extract it. "
        "If no structured data can be found, return an empty array [].\n\n"
        f"Text:\n{preview_text}"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a data extraction assistant. Return ONLY valid JSON arrays. No markdown, no explanation.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()

            # Strip markdown code fences if present
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*", "", content)
                content = re.sub(r"\s*```$", "", content)

            data = json.loads(content)
            if not isinstance(data, list):
                data = [data] if isinstance(data, dict) else []

            if not data:
                return ParseResponse(
                    input_type="paste",
                    confidence=0.0,
                    warnings=["AI could not extract structured data from this text."],
                )

            return ParseResponse(
                input_type="paste",
                data=data,
                rows=len(data),
                columns=list(data[0].keys()) if data else [],
                confidence=0.7,
                preview_rows=data[:10],
                warnings=["Data structured by AI — please verify accuracy."],
            )

    except Exception as e:
        logger.warning("LLM structuring failed: %s", e)
        return ParseResponse(
            input_type="paste",
            confidence=0.0,
            warnings=["Failed to structure text with AI."],
        )
