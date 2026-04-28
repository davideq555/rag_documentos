import re
from typing import List
from backend.config import get_settings


class ChunkingService:
    def __init__(self):
        settings = get_settings()
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def chunk_text(self, text: str) -> List[str]:
        paragraphs = self._split_paragraphs(text)
        chunks = []
        for para in paragraphs:
            sentences = self._split_sentences(para)
            current_chunk = []
            current_length = 0

            for sentence in sentences:
                sentence_length = len(sentence.split())
                if current_length + sentence_length > self.chunk_size and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    overlap_text = " ".join(current_chunk)
                    current_chunk = []
                    current_length = 0

                    overlap_words = self._get_overlap_words(overlap_text)
                    if overlap_words:
                        current_chunk.append(overlap_words)
                        current_length = len(overlap_words.split())

                current_chunk.append(sentence)
                current_length += sentence_length

            if current_chunk:
                chunks.append(" ".join(current_chunk))

        return chunks

    def _split_paragraphs(self, text: str) -> List[str]:
        return [p.strip() for p in text.split("\n\n") if p.strip()]

    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _get_overlap_words(self, text: str) -> str:
        words = text.split()
        if len(words) <= self.chunk_overlap:
            return text
        return " ".join(words[-self.chunk_overlap:])
