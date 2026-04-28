import uuid
import tempfile
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.models import Document, Chunk, Embedding
from backend.services.extractor import TextExtractor
from backend.services.chunker import ChunkingService
from backend.services.embedder import EmbeddingService

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_TYPES = {"pdf", "docx", "md", "txt"}


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    num_chunks: int


@router.post("", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filetype = file.filename.split(".")[-1].lower()
    if filetype not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type '{filetype}' not supported")

    document = Document(filename=file.filename, filetype=filetype, status="pending")
    db.add(document)
    db.commit()
    db.refresh(document)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filetype}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        extractor = TextExtractor()
        text = extractor.extract(tmp_path, filetype)

        chunker = ChunkingService()
        chunks_text = chunker.chunk_text(text)

        embedder = EmbeddingService()
        for idx, chunk_content in enumerate(chunks_text):
            chunk = Chunk(document_id=document.id, content=chunk_content, chunk_index=idx)
            db.add(chunk)
            db.flush()

            embedding = embedder.embed_text(chunk_content)
            embedding_record = Embedding(chunk_id=chunk.id, vector=embedding)
            db.add(embedding_record)

        document.status = "ready"
        db.commit()

        return UploadResponse(
            document_id=str(document.id),
            filename=document.filename,
            status=document.status,
            num_chunks=len(chunks_text),
        )

    except Exception as e:
        db.rollback()
        document.status = "error"
        try:
            db.commit()
        except Exception:
            db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path:
            import os
            os.unlink(tmp_path)
