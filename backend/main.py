from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers.upload import router as upload_router
from backend.routers.chat import router as query_router, documents_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Documentos API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(query_router)
app.include_router(documents_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
