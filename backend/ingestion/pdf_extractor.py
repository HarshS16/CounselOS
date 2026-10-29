from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF

from backend.config import settings

logger = logging.getLogger(__name__)

MIN_DIGITAL_TEXT_LENGTH = 50  # chars per page to consider it "has digital text"
OCR_DPI = 300


@dataclass
class PageResult:
    page_number: int
    text: str
    extraction_method: str  # "digital", "ocr", "mixed", "failed"
    quality_indicator: float  # 0-100


def _ocr_page_image(pix: fitz.Pixmap) -> tuple[str, float]:
    """Run Tesseract OCR on a pixmap and return (text, confidence)."""
    try:
        import pytesseract
        from PIL import Image

        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        data = pytesseract.image_to_data(
            img, lang=settings.ocr_language, output_type=pytesseract.Output.DICT
        )

        words: list[str] = []
        confidences: list[float] = []
        for i, conf in enumerate(data["conf"]):
            try:
                c = float(conf)
            except (ValueError, TypeError):
                continue
            if c > 0:
                confidences.append(c)
                words.append(data["text"][i])

        text = " ".join(w for w in words if w.strip())
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        return text, avg_conf
    except Exception:
        logger.exception("OCR failed for page image")
        return "", 0.0


def extract_pdf(file_path: Path, document_id: str) -> list[PageResult]:
    """Extract text from a PDF, using OCR for scanned pages."""
    results: list[PageResult] = []

    try:
        doc = fitz.open(str(file_path))
    except Exception:
        logger.exception("Failed to open PDF: %s", file_path)
        return [PageResult(page_number=1, text="", extraction_method="failed", quality_indicator=0)]

    try:
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                digital_text = page.get_text("text").strip()

                if len(digital_text) >= MIN_DIGITAL_TEXT_LENGTH:
                    # Sufficient digital text — estimate quality from text density
                    rect = page.rect
                    area = rect.width * rect.height if rect.width and rect.height else 1
                    density = min(len(digital_text) / (area / 1000), 100)
                    quality = max(density, 80.0)
                    results.append(PageResult(
                        page_number=page_num + 1,
                        text=digital_text,
                        extraction_method="digital",
                        quality_indicator=min(quality, 100.0),
                    ))
                else:
                    # Likely scanned — render and OCR
                    pix = page.get_pixmap(dpi=OCR_DPI)
                    ocr_text, ocr_conf = _ocr_page_image(pix)

                    if digital_text and ocr_text:
                        combined = digital_text + "\n" + ocr_text
                        method = "mixed"
                    elif ocr_text:
                        combined = ocr_text
                        method = "ocr"
                    elif digital_text:
                        combined = digital_text
                        method = "digital"
                    else:
                        combined = ""
                        method = "failed"

                    results.append(PageResult(
                        page_number=page_num + 1,
                        text=combined,
                        extraction_method=method,
                        quality_indicator=ocr_conf if method in ("ocr", "mixed") else 0.0,
                    ))

            except Exception:
                logger.exception("Failed to extract page %d of %s", page_num + 1, document_id)
                results.append(PageResult(
                    page_number=page_num + 1,
                    text="",
                    extraction_method="failed",
                    quality_indicator=0.0,
                ))
    finally:
        doc.close()

    return results
