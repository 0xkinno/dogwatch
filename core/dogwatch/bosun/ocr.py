"""Local OCR. Images are read on this machine and never sent anywhere."""
from __future__ import annotations

from pathlib import Path


class OcrUnavailable(Exception):
    pass


def ocr_image(path: Path | str) -> str:
    """Tesseract 5 through pytesseract. Raises OcrUnavailable rather than returning invented text."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        raise OcrUnavailable("pytesseract or pillow is not installed") from e
    try:
        return pytesseract.image_to_string(Image.open(path), config="--psm 6")
    except pytesseract.TesseractNotFoundError as e:
        raise OcrUnavailable("tesseract binary not found") from e
