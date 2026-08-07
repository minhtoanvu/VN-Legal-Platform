"""
FastAPI Application Entry Point — AI Legal Intelligence Platform

Chạy development:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Swagger UI: http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: startup và shutdown."""
    # Startup
    print("🚀 AI Legal Intelligence Platform đang khởi động...")
    # TODO W3: Khởi động embedding model tại đây để warm-up
    yield
    # Shutdown
    print("👋 Server đang tắt...")


app = FastAPI(
    title="AI Legal Intelligence Platform",
    description="""
## Nền tảng hỗ trợ tra cứu, phân tích và khai thác tri thức pháp lý

### Tính năng chính:
- 🔍 **Tìm kiếm ngữ nghĩa** (bkai vietnamese-bi-encoder + pgvector HNSW)
- 🤖 **AI Assistant** (RAG Pipeline: Retrieve → RRF → Augment → Generate)
- 🕸️ **Knowledge Graph** (Vis.js trực quan hóa quan hệ văn bản)
- 📊 **Dashboard Analytics** (xu hướng lập pháp theo lĩnh vực)
- 📁 **Workspace** (Bookmark, Ghi chú, Collection cá nhân)

### Phiên bản: v0.1.0 (Phase 1 — Nền tảng)
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # React CRA (fallback)
        "http://localhost:8080",   # Docker frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── ROUTES ───────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI Legal Intelligence Platform API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint — dùng cho Docker healthcheck."""
    return {"status": "ok", "service": "ai-legal-platform"}


# ── ROUTER MOUNTS ────────────────────────────────────────────────────
# TODO W3: from app.routers import auth, search, documents
# TODO W4: from app.routers import ai, graph, analytics
# TODO W5-7: Frontend served separately

# app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# app.include_router(search.router, prefix="/search", tags=["Search"])
# app.include_router(documents.router, prefix="/documents", tags=["Documents"])
# app.include_router(ai.router, prefix="/ai", tags=["AI Assistant"])
# app.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph"])
# app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
# app.include_router(workspace.router, prefix="/workspace", tags=["Workspace"])
