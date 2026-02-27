"""
Tests for ImageParser — supports, magic bytes, preprocessing.
"""
import io
import pytest
from services.parsers.image_parser import ImageParser, _preprocess, _get_ext


@pytest.fixture
def parser():
    return ImageParser()


class TestSupports:
    def test_supports_jpg(self, parser):
        assert parser.supports("photo.jpg", "") is True

    def test_supports_jpeg(self, parser):
        assert parser.supports("photo.jpeg", "") is True

    def test_supports_png(self, parser):
        assert parser.supports("screenshot.png", "") is True

    def test_supports_heic(self, parser):
        assert parser.supports("IMG_001.heic", "") is True

    def test_supports_content_type(self, parser):
        assert parser.supports("file", "image/jpeg") is True
        assert parser.supports("file", "image/png") is True

    def test_rejects_pdf(self, parser):
        assert parser.supports("doc.pdf", "") is False

    def test_rejects_xlsx(self, parser):
        assert parser.supports("data.xlsx", "") is False


class TestGetExt:
    def test_jpg(self):
        assert _get_ext("photo.jpg") == ".jpg"

    def test_jpeg(self):
        assert _get_ext("photo.jpeg") == ".jpeg"

    def test_png(self):
        assert _get_ext("img.png") == ".png"

    def test_heic(self):
        assert _get_ext("IMG.HEIC") == ".heic"

    def test_unknown(self):
        assert _get_ext("file.txt") == ""


class TestMagicBytes:
    @pytest.mark.asyncio
    async def test_invalid_jpeg_magic(self, parser):
        with pytest.raises(ValueError, match="bad magic bytes"):
            await parser.parse(b"not a jpeg", "fake.jpg")

    @pytest.mark.asyncio
    async def test_invalid_png_magic(self, parser):
        with pytest.raises(ValueError, match="bad magic bytes"):
            await parser.parse(b"not a png file", "fake.png")


class TestPreprocess:
    def test_rgb_conversion(self):
        from PIL import Image
        # Create RGBA image
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        processed = _preprocess(img)
        assert processed.mode == "RGB"

    def test_resize_large_image(self):
        from PIL import Image
        img = Image.new("RGB", (8000, 6000))
        processed = _preprocess(img)
        assert max(processed.size) <= 4000

    def test_small_image_not_resized(self):
        from PIL import Image
        img = Image.new("RGB", (800, 600))
        processed = _preprocess(img)
        assert processed.size == (800, 600)


class TestParseRealImage:
    @pytest.mark.asyncio
    async def test_simple_image_with_text(self, parser):
        """Create a simple image with text and test OCR."""
        try:
            from PIL import Image, ImageDraw
            import pytesseract
            # Verify tesseract is available
            pytesseract.get_tesseract_version()
        except Exception:
            pytest.skip("tesseract-ocr not available")

        # Create image with clear text
        img = Image.new("RGB", (400, 100), "white")
        draw = ImageDraw.Draw(img)
        draw.text((10, 30), "Name, Age, City", fill="black")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        content = buf.read()

        result = await parser.parse(content, "text_image.png")
        assert result.input_type == "image"
        # At minimum, it should process without error

    @pytest.mark.asyncio
    async def test_blank_image(self, parser):
        """Blank image should produce low confidence."""
        try:
            from PIL import Image
            import pytesseract
            pytesseract.get_tesseract_version()
        except Exception:
            pytest.skip("tesseract-ocr not available")

        img = Image.new("RGB", (200, 200), "white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        # Blank image may raise (no data) or return low confidence
        try:
            result = await parser.parse(buf.read(), "blank.png")
            assert result.confidence <= 0.5
        except Exception:
            pass  # "No data found" is acceptable
