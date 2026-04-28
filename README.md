# RAG App — Plan de Arquitectura

Aplicación web para cargar documentos (PDF, DOCX, MD), construir un RAG a partir de ellos y consultarlos mediante un chat.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | FastAPI + SQLAlchemy + Alembic |
| Base de datos | PostgreSQL + extensión `pgvector` |
| Extracción de texto | `pdfplumber` + `python-docx` |
| LLM local | Ollama |
| Frontend | React + TypeScript + Vite, Tailwind CSS + shadcn/ui |

---

## Estructura de la base de datos

### Tabla `documents`
Metadatos del archivo subido.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID PK | Identificador único |
| `filename` | VARCHAR | Nombre original del archivo |
| `filetype` | VARCHAR | pdf / docx / md / txt |
| `status` | VARCHAR | pending / processing / ready / error |
| `created_at` | TIMESTAMP | Fecha de subida |

### Tabla `chunks`
Fragmentos de texto extraídos del documento.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID PK | Identificador único |
| `document_id` | UUID FK | Referencia a `documents` |
| `content` | TEXT | Texto del fragmento |
| `chunk_index` | INTEGER | Posición dentro del documento |

### Tabla `embeddings`
Vectores generados por Ollama, vinculados a cada chunk.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID PK | Identificador único |
| `chunk_id` | UUID FK | Referencia a `chunks` |
| `vector` | VECTOR(768) | Embedding generado por Ollama |

---

## Estructura de carpetas

```
rag-app/
├── backend/
│   ├── main.py                # FastAPI app, CORS, routers
│   ├── config.py              # Variables de entorno (DB URL, Ollama URL)
│   ├── database.py            # SQLAlchemy engine + session
│   ├── models/
│   │   ├── document.py        # ORM: documents, chunks
│   │   └── embedding.py       # ORM: embeddings (vector type)
│   ├── routers/
│   │   ├── upload.py          # POST /upload
│   │   └── chat.py            # POST /query, GET /documents
│   ├── services/
│   │   ├── extractor.py       # Extracción de texto (pdfplumber, python-docx)
│   │   ├── chunker.py         # Lógica de chunking
│   │   ├── embedder.py        # Llamadas a Ollama embeddings
│   │   └── retriever.py       # Búsqueda vectorial + RAG
│   └── alembic/               # Migraciones de DB
├── frontend/                   # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/        # shadcn/ui components
│   │   ├── hooks/            # React Query hooks
│   │   ├── lib/              # API client
│   │   └── App.tsx           # Componente principal
│   ├── index.html
│   └── package.json
├── docker-compose.yml         # PostgreSQL + pgvector
└── requirements.txt
```

---

## Dependencias (`requirements.txt`)

```txt
fastapi
uvicorn
sqlalchemy
alembic
psycopg2-binary
pgvector
python-multipart
pdfplumber
python-docx
httpx
python-dotenv
pydantic-settings
```

---

## Configuración de Ollama

Ollama debe estar corriendo localmente en `http://localhost:11434`. Se necesitan dos modelos:

```bash
# Modelo de embeddings
ollama pull nomic-embed-text

# Modelo de generación (elegir uno)
ollama pull llama3.2
# o
ollama pull mistral
# o
ollama pull phi3
```

---

## Flujo de ingesta de documentos

```
POST /upload
    │
    ├─► Guardar archivo temporalmente
    ├─► Crear registro en `documents` (status: pending)
    ├─► pdfplumber / python-docx / built-in → extraer texto limpio
    ├─► Dividir en chunks (≈500 tokens, overlap 50)
    ├─► Ollama nomic-embed-text → generar embeddings
    └─► Persistir chunks + embeddings en PostgreSQL (status: ready)
```

### Parámetros de chunking recomendados
- Tamaño de chunk: 500 tokens
- Overlap entre chunks: 50 tokens
- Separadores: párrafos (`\n\n`), luego oraciones (`.`)

---

## Flujo de consulta / chat

```
POST /query  { "question": "...", "document_ids": [...] }
    │
    ├─► Ollama nomic-embed-text → embedding de la pregunta
    ├─► pgvector: SELECT chunks ORDER BY embedding <=> $1 LIMIT 5
    ├─► Construir prompt: [contexto chunks] + [pregunta]
    ├─► Ollama llama3.2 → generar respuesta
    └─► Retornar { "answer": "...", "sources": [...] }
```

### Búsqueda vectorial en pgvector

```sql
SELECT c.content, c.document_id, (e.vector <=> $1) AS distance
FROM embeddings e
JOIN chunks c ON c.id = e.chunk_id
ORDER BY distance ASC
LIMIT 5;
```

---

## Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/upload` | Sube y procesa un documento |
| `GET` | `/documents` | Lista todos los documentos |
| `GET` | `/documents/{id}` | Detalle de un documento |
| `DELETE` | `/documents/{id}` | Elimina documento y sus datos |
| `POST` | `/query` | Consulta RAG sobre los documentos |

---

## Variables de entorno (`.env`)

```env
DATABASE_URL=postgresql://davideq:password@localhost:5432/ragdb
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_CHAT_MODEL=llama3.2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

---

## Docker Compose (PostgreSQL + pgvector)

```yaml
version: "3.9"
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ragdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Levantar con:

```bash
docker compose up -d
```

---

## Migraciones con Alembic

```bash
# Inicializar (solo la primera vez)
alembic init alembic

# Crear migración
alembic revision --autogenerate -m "initial schema"

# Aplicar migraciones
alembic upgrade head
```

> Recordar habilitar la extensión pgvector en la primera migración:
> ```python
> op.execute("CREATE EXTENSION IF NOT EXISTS vector")
> ```

---

## Orden de implementación sugerido

1. Levantar PostgreSQL con pgvector via Docker Compose
2. Crear el schema con Alembic (tablas + extensión vector)
3. Implementar `extractor.py` con pdfplumber/python-docx y verificar salida
4. Implementar `chunker.py` con lógica de segmentación
5. Implementar `embedder.py` llamando a Ollama
6. Conectar el pipeline completo en `routers/upload.py`
7. Implementar `retriever.py` con búsqueda en pgvector
8. Conectar el pipeline de consulta en `routers/chat.py`
9. Construir el frontend (subida de archivos + chat)

---

## Notas adicionales

- La dimensión del vector (`VECTOR(768)`) debe coincidir con la salida del modelo de embeddings elegido. `nomic-embed-text` produce 768 dimensiones; verificar si se cambia el modelo.
- Para producción considerar un worker asíncrono (Celery o BackgroundTasks de FastAPI) para el procesamiento de documentos, ya que puede ser lento en archivos grandes.
- pgvector soporta índices HNSW para búsquedas más rápidas a escala: `CREATE INDEX ON embeddings USING hnsw (vector vector_cosine_ops)`.
