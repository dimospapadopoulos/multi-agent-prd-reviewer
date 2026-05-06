"""
File content extraction for uploaded PRD files
Supports .md (plaintext), .pdf (via pypdf), .docx (via python-docx)
"""

import io
from typing import Optional


def extract_text(content: bytes, filename: str) -> Optional[str]:
    """
    Extract plain text from raw file bytes.

    Args:
        content: Raw bytes of the uploaded file
        filename: Original filename — used to determine format

    Returns:
        Extracted text string, or None if the format is unsupported or empty
    """
    name = filename.lower()

    if name.endswith(".md"):
        text = content.decode("utf-8", errors="replace").strip()
        return text or None

    if name.endswith(".pdf"):
        text = _extract_pdf_text(content).strip()
        return text or None

    if name.endswith(".docx"):
        text = _extract_docx_text(content).strip()
        return text or None

    return None


def _extract_pdf_text(content: bytes) -> str:
    """Extract plain text from PDF bytes using pypdf."""
    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(content))
    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text and page_text.strip():
            pages.append(page_text.strip())

    return "\n\n".join(pages)


def _extract_docx_text(content: bytes) -> str:
    """Extract plain text from Word (.docx) bytes using python-docx."""
    import docx

    document = docx.Document(io.BytesIO(content))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)
