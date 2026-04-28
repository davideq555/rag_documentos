# AGENTS.md

## Stack
- Backend: FastAPI + SQLAlchemy + Alembic
- DB: PostgreSQL + pgvector (via Docker Compose)
- LLM/Embeddings: Ollama (local, must be running at `http://localhost:11434`)
- Text extraction: `pdfplumber` + `python-docx`
- Frontend: React + TypeScript + Vite, Tailwind CSS + shadcn/ui, React Query

## Dev setup

```bash
# 1. Start PostgreSQL + pgvector
docker compose up -d

# 2. Run Alembic migrations (enable pgvector extension first if needed)
alembic -c backend/alembic.ini upgrade head

# 3. Start Ollama (separate terminal or service)
ollama serve

# 4. Start backend
cd backend && uvicorn main:app --reload

# 5. Start frontend (from rag_documentos root)
cd frontend && npm install && npm run dev
```

## Required Ollama models
```bash
ollama pull nomic-embed-text   # embeddings — outputs 768-dim vectors
ollama pull llama3.2             # chat generation (mistral or phi3 also valid)
```

## Environment variables (`.env`)
```
DATABASE_URL=postgresql://davideq:password@localhost:5432/ragdb
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_CHAT_MODEL=llama3.2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

## DB schema
- `documents`: id, filename, filetype, status (pending/processing/ready/error), created_at
- `chunks`: id, document_id, content, chunk_index
- `embeddings`: id, chunk_id, vector VECTOR(768)

> **Important**: First Alembic migration must include `op.execute("CREATE EXTENSION IF NOT EXISTS vector")`.

## Key implementation details
- Chunking: 500 tokens, 50 token overlap, split on `\n\n` then sentences
- Vector search: `ORDER BY embedding <=> $1 LIMIT 5` (cosine distance via pgvector)
- pgvector index for scale: `CREATE INDEX ON embeddings USING hnsw (vector vector_cosine_ops)`
- Vector dimension (768) must match the embedding model — `nomic-embed-text` is 768-dim

## API endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/upload` | Upload and process a document |
| GET | `/documents` | List all documents |
| GET | `/documents/{id}` | Get document detail |
| DELETE | `/documents/{id}` | Delete document and its data |
| POST | `/query` | RAG query: { "question": "...", "document_ids": [...] } |

## Linting/typecheck/test
Backend: no tooling configured yet
Frontend: `npm run lint`, `npm run typecheck`, `npm test` (React Query for API state management)

## MCP tools
- Context7: for RAG context retrieval patterns
- Playwright: for frontend testing (E2E)
