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
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.dependencies import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: startup và shutdown."""
    # Startup
    print("[START] AI Legal Intelligence Platform dang khoi dong...")
    # Model embedding sẽ được lazy-load khi có request đầu tiên.
    # Không warm-up lúc startup để tránh OOM trên máy RAM thấp (8GB).
    print("[OK] Server khoi dong thanh cong. Embedding model se duoc nap khi can.")
    yield
    # Shutdown
    print("[STOP] Server dang tat...")

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

### Phiên bản: v0.2.0 (Phase 2 — Auth + Search API)
    """,
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Kích hoạt SlowAPI vào ứng dụng
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",   # Vite dev server (IPv4/CI)
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
from app.routers import (
    admin,
    ai,
    analytics,
    auth,
    contract,
    documents,
    graph,
    search,
    workspace,
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(ai.router, prefix="/ai", tags=["AI Assistant"])
app.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(workspace.router, prefix="/workspace", tags=["Workspace"])
app.include_router(contract.router, prefix="/contract", tags=["Contract Analysis"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Panel"])
