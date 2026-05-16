from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import get_settings


class ResumeFileService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = Path(self.settings.resume_storage_dir)

    async def read_pdf(self, file: UploadFile) -> bytes:
        filename = file.filename or ""
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=422, detail="Only PDF resumes are supported")
        if file.content_type and file.content_type not in {"application/pdf", "application/octet-stream"}:
            raise HTTPException(status_code=422, detail="Uploaded file must be a PDF")
        data = await file.read()
        max_bytes = self.settings.resume_upload_max_mb * 1024 * 1024
        if len(data) > max_bytes:
            raise HTTPException(status_code=413, detail=f"Resume PDF cannot exceed {self.settings.resume_upload_max_mb}MB")
        if not data.startswith(b"%PDF"):
            raise HTTPException(status_code=422, detail="Invalid PDF file")
        return data

    def save(self, user_id: str, resume_id: str, content: bytes) -> str:
        user_dir = self.root / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / f"{resume_id}.pdf"
        path.write_bytes(content)
        return str(path.as_posix())

    def delete(self, file_path: str) -> None:
        path = Path(file_path)
        try:
            if path.exists() and path.is_file():
                path.unlink()
        except OSError:
            pass
