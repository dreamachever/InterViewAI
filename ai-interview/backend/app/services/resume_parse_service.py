from io import BytesIO

from fastapi import HTTPException
from pypdf import PdfReader


class ResumeParseService:
    def parse_pdf(self, content: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise HTTPException(status_code=422, detail="Failed to parse PDF resume") from exc
        normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if len(normalized) < 30:
            raise HTTPException(status_code=422, detail="PDF text is too short. Scanned PDFs are not supported yet.")
        return normalized
