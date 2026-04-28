import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base
from pgvector.sqlalchemy import Vector

VECTOR_DIMENSION = 768


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=False, unique=True)
    vector = Column(Vector(VECTOR_DIMENSION), nullable=False)

    chunk = relationship("Chunk", back_populates="embedding")
