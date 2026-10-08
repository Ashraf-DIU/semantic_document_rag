from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import Settings, get_settings
from app.dependencies import get_ingestion_service
from app.schemas.upload import DocumentInfo, UploadResponse
from app.services.ingestion_service import IngestionService
from app.services.pdf_service import PDFError
from app.utils.helpers import safe_filename
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse)
def upload(
    files: list[UploadFile] = File(...),
    ingestion: IngestionService = Depends(get_ingestion_service),
    settings: Settings = Depends(get_settings),
):
    # Plain `def` -> FastAPI runs this in a worker thread, so heavy embedding work doesn't block the event loop.
    max_bytes = settings.max_upload_mb * 1024 * 1024
    documents: list[DocumentInfo] = []
    skipped: list[str] = []

    for file in files:
        name = safe_filename(file.filename or "")
        if not name.lower().endswith(".pdf"):
            skipped.append(f"{name}: only PDF files are supported")
            continue

        data = file.file.read(max_bytes + 1)
        if len(data) > max_bytes:
            skipped.append(f"{name}: larger than {settings.max_upload_mb} MB")
            continue

        try:
            record = ingestion.ingest(name, data)
        except PDFError as exc:
            skipped.append(f"{name}: {exc}")
            continue
        except Exception:
            log.exception("Failed to ingest %s", name)
            skipped.append(f"{name}: unexpected error while processing")
            continue

        documents.append(DocumentInfo(**{k: getattr(record, k) for k in DocumentInfo.model_fields}))

    if not documents and skipped:
        raise HTTPException(status_code=400, detail="; ".join(skipped))
    return UploadResponse(documents=documents, skipped=skipped)
