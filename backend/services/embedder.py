from typing import List

import httpx

from backend.config import get_settings


class EmbeddingService:
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.OLLAMA_BASE_URL
        self.embed_model = settings.OLLAMA_EMBED_MODEL

    def embed_text(self, text: str) -> List[float]:
        response = httpx.post(
            f"{self.base_url}/api/embed",
            json={"model": self.embed_model, "input": text},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings")
        if not embeddings or not embeddings[0]:
            raise ValueError(f"Empty embedding returned for text: {text[:50]}")
        embedding = embeddings[0]
        if len(embedding) != 768:
            raise ValueError(f"Expected 768 dimensions, got {len(embedding)}")
        return embedding

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(text) for text in texts]
