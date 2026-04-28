from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Chunk, Document, Embedding
from backend.services.embedder import EmbeddingService
from backend.services.retriever import RetrieverService

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None


class Source(BaseModel):
    content: str
    document_id: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]


class DocumentResponse(BaseModel):
    id: str
    filename: str
    filetype: str
    status: str
    created_at: str


@router.post("", response_model=QueryResponse)
async def query_documents(request: QueryRequest, db: Session = Depends(get_db)):
    embedder = EmbeddingService()
    retriever = RetrieverService()

    question_embedding = embedder.embed_text(request.question)

    context_chunks = retriever.retrieve_relevant_chunks(
        db, question_embedding, request.document_ids
    )

    answer = retriever.generate_answer(request.question, context_chunks)

    return QueryResponse(
        answer=answer,
        sources=[
            Source(content=chunk["content"], document_id=chunk["document_id"])
            for chunk in context_chunks
        ],
    )


documents_router = APIRouter(prefix="/documents", tags=["documents"])


@documents_router.get("", response_model=List[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return [
        DocumentResponse(
            id=str(doc.id),
            filename=doc.filename,
            filetype=doc.filetype,
            status=doc.status,
            created_at=doc.created_at.isoformat(),
        )
        for doc in documents
    ]


@documents_router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(
        id=str(document.id),
        filename=document.filename,
        filetype=document.filetype,
        status=document.status,
        created_at=document.created_at.isoformat(),
    )


@documents_router.get("/{document_id}/info")
async def get_document_info(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found")

    num_chunks = db.query(Chunk).filter(Chunk.document_id == document_id).count()
    num_embeddings = (
        db.query(Embedding).join(Chunk).filter(Chunk.document_id == document_id).count()
    )

    return {
        "document_id": str(document_id),
        "filename": document.filename,
        "num_chunks": num_chunks,
        "num_embeddings": num_embeddings,
        "status": document.status,
        "complete": num_chunks == num_embeddings,
    }


class VectorInfo(BaseModel):
    chunk_id: str
    chunk_index: int
    content: str
    dimensions: int
    vector_preview: str


class VectorsResponse(BaseModel):
    document_id: str
    num_chunks: int
    chunks: List[VectorInfo]


@documents_router.get("/{document_id}/vectors", response_model=VectorsResponse)
async def get_document_vectors(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found")

    chunks = (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
        .all()
    )

    result = []
    for chunk in chunks:
        embedding = db.query(Embedding).filter(Embedding.chunk_id == chunk.id).first()
        vector_preview = ""
        dimensions = 0
        if embedding is not None and embedding.vector is not None:
            dimensions = len(embedding.vector)
            # nomic-embed-text debe dar exactamente 768
            assert dimensions == 768, f"Dimensiones inesperadas: {dimensions}"
            preview_vals = embedding.vector[:5]
            vector_preview = str([round(float(v), 4) for v in preview_vals]) + "..."

        result.append(
            VectorInfo(
                chunk_id=str(chunk.id),
                chunk_index=chunk.chunk_index,
                content=chunk.content[:200] + "..."
                if len(chunk.content) > 200
                else chunk.content,
                dimensions=dimensions,
                vector_preview=vector_preview,
            )
        )

    return VectorsResponse(
        document_id=str(document_id),
        num_chunks=len(result),
        chunks=result,
    )


@documents_router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"message": "Document deleted"}
