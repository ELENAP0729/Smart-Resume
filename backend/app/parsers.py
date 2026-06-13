from pathlib import Path
from typing import Tuple
from pypdf import PdfReader
from docx import Document
from PIL import Image
import pytesseract


def parse_uploaded_file(file_path: Path, original_filename: str) -> Tuple[str, str]:
    suffix = Path(original_filename).suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text, "PDF"
    if suffix in {".docx", ".doc"}:
        doc = Document(str(file_path))
        text = "\n".join(p.text for p in doc.paragraphs)
        return text, "Word document"
    if suffix in {".md", ".txt", ".csv"}:
        return file_path.read_text(encoding="utf-8", errors="ignore"), "Text/Markdown"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        try:
            text = pytesseract.image_to_string(Image.open(file_path))
        except Exception as exc:
            text = f"OCR failed: {exc}"
        return text, "Image OCR"
    return file_path.read_text(encoding="utf-8", errors="ignore"), "Unknown text file"
