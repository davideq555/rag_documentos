import json
from typing import Any, Dict, List

import httpx
from pgvector.sqlalchemy import Vector
from sqlalchemy import text

from backend.config import get_settings


class RetrieverService:
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.OLLAMA_BASE_URL
        self.chat_model = settings.OLLAMA_CHAT_MODEL

    def retrieve_relevant_chunks(
        self,
        db,
        question_embedding: List[float],
        document_ids: List[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        from backend.models import Chunk, Embedding

        query = (
            db.query(Chunk.content, Chunk.document_id)
            .join(Embedding, Embedding.chunk_id == Chunk.id)
            .order_by(Embedding.vector.l2_distance(question_embedding))
        )

        if document_ids:
            query = query.filter(Chunk.document_id.in_(document_ids))

        results = query.limit(limit).all()
        return [
            {"content": r.content, "document_id": str(r.document_id)} for r in results
        ]

    def generate_answer(
        self, question: str, context_chunks: List[Dict[str, Any]]
    ) -> str:
        context = "\n\n".join(chunk["content"] for chunk in context_chunks)
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"

        full_response = ""
        with httpx.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json={
                "model": self.chat_model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=180,
        ) as response:
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get("done"):
                        full_response += chunk["message"]["content"]

        return full_response
