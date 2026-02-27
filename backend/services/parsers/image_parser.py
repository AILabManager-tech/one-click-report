"""
Image parser — OCR extraction from images.
Supports: JPG, PNG, HEIC.
Pre-processing: EXIF rotation, RGB conversion, resize.
Fallback: GPT-4 Vision for low-confidence OCR.
"""
import io
import json
import os
import re
import base64
import logging

import httpx

from .base import BaseParser, ParseResponse

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif"}
IMAGE_CONTENT_TYPES = {
    "image/jpeg", "image/png", "image/heic", "image/heif",
}

# Magic bytes
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG"
HEIF_MAGIC_OFFSETS = [(4, b"ftyp")]  # HEIC/HEIF: "ftyp" at offset 4

MAX_IMAGE_DIMENSION = 4000  # px
MIN_OCR_CONFIDENCE = 60  # percent


class ImageParser(BaseParser):
    def supports(self, filename: str, content_type: str) -> bool:
        ext = _get_ext(filename)
        return ext in IMAGE_EXTENSIONS or content_type in IMAGE_CONTENT_TYPES

    async def parse(
        self, content: bytes, filename: str, options: dict | None = None
    ) -> ParseResponse:
        _validate_magic(content, filename)
        img = _load_image(content, filename)
        img = _preprocess(img)

        # OCR
        text, confidence = _ocr_image(img)

        if confidence < MIN_OCR_CONFIDENCE and OPENAI_API_KEY:
            logger.info("OCR confidence %.0f%% < %d%%, trying GPT-4 Vision", confidence, MIN_OCR_CONFIDENCE)
            return await _vision_fallback(content, filename, text, confidence)

        if not text.strip():
            return ParseResponse(
                input_type="image",
                confidence=0.0,
                warnings=["No text detected in image."],
            )

        # Structure the OCR text
        from .text_parser import TextParser
        text_parser = TextParser()
        result = await text_parser.parse(text.encode("utf-8"), "ocr.txt")
        result.input_type = "image"
        result.confidence = min(result.confidence, confidence / 100)
        return result


def _get_ext(filename: str) -> str:
    filename = filename.lower()
    for ext in IMAGE_EXTENSIONS:
        if filename.endswith(ext):
            return ext
    return ""


def _validate_magic(content: bytes, filename: str) -> None:
    """Validate image magic bytes."""
    ext = _get_ext(filename)
    if ext in {".jpg", ".jpeg"} and not content[:3].startswith(JPEG_MAGIC):
        raise ValueError("Invalid JPEG file (bad magic bytes)")
    if ext == ".png" and not content[:4].startswith(PNG_MAGIC):
        raise ValueError("Invalid PNG file (bad magic bytes)")
    # HEIC validation: check for "ftyp" at offset 4
    if ext in {".heic", ".heif"} and content[4:8] != b"ftyp":
        raise ValueError("Invalid HEIC file (bad magic bytes)")


def _load_image(content: bytes, filename: str):
    """Load image, including HEIC support."""
    from PIL import Image

    ext = _get_ext(filename)
    if ext in {".heic", ".heif"}:
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            raise ValueError("HEIC support not available (pillow-heif not installed)")

    return Image.open(io.BytesIO(content))


def _preprocess(img):
    """Pre-process image for OCR: EXIF rotation, RGB, resize."""
    from PIL import ImageOps

    # Apply EXIF rotation
    img = ImageOps.exif_transpose(img)

    # Convert to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize if too large
    w, h = img.size
    if max(w, h) > MAX_IMAGE_DIMENSION:
        ratio = MAX_IMAGE_DIMENSION / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)))

    return img


def _ocr_image(img) -> tuple[str, float]:
    """Run pytesseract OCR and return (text, confidence%)."""
    import pytesseract

    # Get detailed data for confidence
    ocr_data = pytesseract.image_to_data(img, lang="fra+eng", output_type=pytesseract.Output.DICT)

    # Calculate average confidence (exclude -1 = no text)
    confidences = [c for c in ocr_data["conf"] if c > 0]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    text = pytesseract.image_to_string(img, lang="fra+eng")
    return text, avg_conf


async def _vision_fallback(
    content: bytes, filename: str, ocr_text: str, ocr_confidence: float
) -> ParseResponse:
    """Use GPT-4 Vision to extract structured data from image."""
    warnings = [f"OCR confidence low ({ocr_confidence:.0f}%), used AI vision."]

    # Encode image as base64
    b64 = base64.b64encode(content).decode("utf-8")
    ext = _get_ext(filename)
    mime = "image/jpeg" if ext in {".jpg", ".jpeg"} else "image/png"

    prompt = (
        "Extract ALL structured data (tables, lists, numbers) from this image. "
        "Return ONLY a JSON array of objects. If you see a receipt, invoice, or table, "
        "extract every row. No explanation, just the JSON array."
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You extract structured data from images. Return ONLY valid JSON arrays.",
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "high"},
                                },
                            ],
                        },
                    ],
                    "max_tokens": 3000,
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            result = response.json()
            raw = result["choices"][0]["message"]["content"].strip()

            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)

            data = json.loads(raw)
            if not isinstance(data, list):
                data = [data] if isinstance(data, dict) else []

            if not data:
                warnings.append("AI vision could not extract structured data.")
                return ParseResponse(input_type="image", confidence=0.3, warnings=warnings)

            return ParseResponse(
                input_type="image",
                data=data,
                rows=len(data),
                columns=list(data[0].keys()) if data else [],
                confidence=0.75,
                preview_rows=data[:10],
                warnings=warnings,
            )

    except Exception as e:
        logger.warning("Vision fallback failed: %s", e)
        warnings.append("AI vision extraction failed.")

        # Last resort: return OCR text as single-row data
        if ocr_text.strip():
            from .text_parser import TextParser
            text_parser = TextParser()
            result = await text_parser.parse(ocr_text.encode("utf-8"), "ocr.txt")
            result.input_type = "image"
            result.warnings = warnings + result.warnings
            return result

        return ParseResponse(input_type="image", confidence=0.0, warnings=warnings)
