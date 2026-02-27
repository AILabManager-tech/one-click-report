"""
PDF parser — extracts tables from PDF files.
Primary: pdfplumber table extraction.
Fallback: OCR via pytesseract + pdf2image.
Bank statement detection with AI categorization.
"""
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

PDF_MAGIC = b"%PDF"
MAX_PAGES = 20
MAX_ROWS = 10_000


class PdfParser(BaseParser):
    def supports(self, filename: str, content_type: str) -> bool:
        return (
            filename.lower().endswith(".pdf")
            or content_type == "application/pdf"
        )

    async def parse(
        self, content: bytes, filename: str, options: dict | None = None
    ) -> ParseResponse:
        if not content[:4].startswith(PDF_MAGIC):
            raise ValueError("Invalid PDF file (bad magic bytes)")

        # Try table extraction first
        data, warnings = _extract_tables(content)

        if data:
            # Check if it looks like a bank statement
            is_bank = _detect_bank_statement(data)
            if is_bank and OPENAI_API_KEY:
                data, cat_warnings = await _categorize_transactions(data)
                warnings.extend(cat_warnings)

            return ParseResponse(
                input_type="pdf",
                data=data[:MAX_ROWS],
                rows=min(len(data), MAX_ROWS),
                columns=list(data[0].keys()) if data else [],
                confidence=0.9,
                preview_rows=data[:10],
                warnings=warnings,
            )

        # Fallback: OCR
        logger.info("No tables found in PDF, falling back to OCR")
        return await _ocr_fallback(content, warnings)


def _extract_tables(content: bytes) -> tuple[list[dict], list[str]]:
    """Extract tables from PDF using pdfplumber."""
    import pdfplumber

    warnings: list[str] = []
    all_data: list[dict] = []

    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            page_count = len(pdf.pages)
            if page_count > MAX_PAGES:
                warnings.append(f"PDF has {page_count} pages, only first {MAX_PAGES} processed.")

            for page in pdf.pages[:MAX_PAGES]:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # First non-empty row as headers
                    header_idx = 0
                    for i, row in enumerate(table):
                        if any(cell and cell.strip() for cell in row):
                            header_idx = i
                            break

                    headers = [
                        str(cell).strip() if cell else f"col_{j}"
                        for j, cell in enumerate(table[header_idx])
                    ]

                    for row in table[header_idx + 1:]:
                        if not any(cell and str(cell).strip() for cell in row):
                            continue
                        record = {}
                        for j, header in enumerate(headers):
                            val = row[j] if j < len(row) else None
                            record[header] = str(val).strip() if val else None
                        all_data.append(record)

    except Exception as e:
        logger.warning("pdfplumber extraction failed: %s", e)
        warnings.append("Table extraction encountered issues.")

    return all_data, warnings


def _detect_bank_statement(data: list[dict]) -> bool:
    """Heuristic: detect if data looks like bank transactions."""
    if not data:
        return False

    cols_lower = {k.lower() for k in data[0].keys()}
    bank_keywords = {"date", "montant", "amount", "débit", "crédit", "debit", "credit",
                     "solde", "balance", "description", "libellé", "référence"}
    matches = cols_lower & bank_keywords
    return len(matches) >= 2


async def _categorize_transactions(data: list[dict]) -> tuple[list[dict], list[str]]:
    """Use GPT-4o-mini to add category to bank transactions."""
    warnings: list[str] = []
    preview = json.dumps(data[:30], ensure_ascii=False, default=str)

    prompt = (
        "Categorize each bank transaction. Add a 'category' field to each object. "
        "Categories: Alimentation, Transport, Logement, Santé, Loisirs, Revenus, "
        "Abonnements, Shopping, Épargne, Autre. "
        "Return ONLY the JSON array with the added category field.\n\n"
        f"Transactions:\n{preview}"
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
                        {"role": "system", "content": "You categorize bank transactions. Return ONLY valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 3000,
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()

            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*", "", content)
                content = re.sub(r"\s*```$", "", content)

            categorized = json.loads(content)
            if isinstance(categorized, list) and categorized:
                # Merge categories back: categorized covers first 30, rest keep original
                for i, item in enumerate(categorized):
                    if i < len(data) and isinstance(item, dict) and "category" in item:
                        data[i]["category"] = item["category"]
                warnings.append("AI-categorized bank transactions (verify accuracy).")
                return data, warnings

    except Exception as e:
        logger.warning("Transaction categorization failed: %s", e)
        warnings.append("Could not auto-categorize transactions.")

    return data, warnings


async def _ocr_fallback(content: bytes, existing_warnings: list[str]) -> ParseResponse:
    """OCR fallback: convert PDF pages to images, then extract text."""
    warnings = list(existing_warnings)
    warnings.append("No tables found — using OCR text extraction.")

    try:
        from pdf2image import convert_from_bytes
        import pytesseract

        images = convert_from_bytes(content, first_page=1, last_page=MAX_PAGES, dpi=200)
        all_text = []
        for img in images:
            text = pytesseract.image_to_string(img, lang="fra+eng")
            all_text.append(text)

        full_text = "\n".join(all_text).strip()
        if not full_text:
            return ParseResponse(
                input_type="pdf",
                confidence=0.0,
                warnings=warnings + ["OCR produced no text."],
            )

        # Try to structure the OCR text
        from .text_parser import TextParser
        text_parser = TextParser()
        result = await text_parser.parse(full_text.encode("utf-8"), "ocr.txt")
        result.input_type = "pdf"
        result.warnings = warnings + result.warnings
        result.confidence = min(result.confidence, 0.6)
        return result

    except ImportError as e:
        logger.warning("OCR dependencies not available: %s", e)
        warnings.append("OCR not available (missing system dependencies).")
        return ParseResponse(input_type="pdf", confidence=0.0, warnings=warnings)
    except Exception as e:
        logger.warning("OCR fallback failed: %s", e)
        warnings.append(f"OCR failed: {e}")
        return ParseResponse(input_type="pdf", confidence=0.0, warnings=warnings)
