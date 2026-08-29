<div align="center">
  <h1>⚖️ AI Legal Intelligence Platform (AILIP)</h1>
  <p><i>A full-stack, AI-powered legal search, RAG (Retrieval-Augmented Generation), and Contract Analysis system built for Vietnamese Law.</i></p>

  <p>
    <a href="#"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white" alt="Python"></a>
    <a href="#"><img src="https://img.shields.io/badge/FastAPI-005571.svg?logo=fastapi&logoColor=white" alt="FastAPI"></a>
    <a href="#"><img src="https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black" alt="React"></a>
    <a href="#"><img src="https://img.shields.io/badge/TypeScript-3178C6.svg?logo=typescript&logoColor=white" alt="TypeScript"></a>
    <a href="#"><img src="https://img.shields.io/badge/PostgreSQL-336791.svg?logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
    <a href="#"><img src="https://img.shields.io/badge/pgvector-Vector_Search-green.svg" alt="pgvector"></a>
    <a href="#"><img src="https://img.shields.io/badge/Playwright-2EAD33.svg?logo=playwright&logoColor=white" alt="Playwright"></a>
  </p>
</div>

---

## 📖 Overview
This project is an advanced **Legal AI Search & Assistant Engine**, developed as a Scientific Research (NCKH) initiative. It goes beyond simple keyword matching by implementing a **Hybrid Search Pipeline (BM25 + Semantic Search)** and an **anti-hallucination RAG engine** to provide accurate, citable legal answers based on Vietnamese Law. 

Designed with a **Modular Monolith** architecture, a modern **Glassmorphism UI**, and backed by a **comprehensive automated testing suite**, this project demonstrates end-to-end full-stack engineering and QA capabilities.

*(Add your demo link or a GIF/Screenshot of your application here)*
> `<img src="docs/demo.gif" width="800" alt="App Demo">`

---

## 🚀 Key Technical Highlights

### 1. Hybrid Search with Reciprocal Rank Fusion (RRF)
Implemented a custom search engine combining traditional full-text search (PostgreSQL `tsvector`/BM25) and semantic vector search (`pgvector` HNSW index). Results are reranked using the **RRF algorithm** to ensure extremely high retrieval accuracy for complex legal queries.

### 2. Real-time RAG Engine (Retrieval-Augmented Generation)
Integrated Google's Gemini API via **Server-Sent Events (SSE)** for real-time text streaming. Built a strict prompt engineering pipeline that forces the LLM to answer *only* using the provided context, rendering **inline citations** to prevent AI hallucinations.

### 3. Automated ETL & Vectorization Pipeline
Developed a custom Python ETL pipeline to scrape, clean, and process over 3,000 legal articles from Hugging Face. The pipeline automatically chunks the text and generates 768-dimensional embeddings using a local Bi-Encoder model (`bkai-foundation-models`) before indexing them into PostgreSQL.

### 4. Enterprise-Grade QA & Testing Infrastructure
Robust quality assurance implemented across all layers:
- **E2E UI Testing:** Automated browser testing using Playwright.
- **API Integration Testing:** Comprehensive `pytest` suite for authentication, search, and analytics endpoints.
- **Performance Load Testing:** Stress testing using `Locust` to ensure SLA compliance under heavy traffic.
- **Postman Collections:** Pre-configured API workflows for rapid debugging.

### 5. Smart Contract Analysis
A modular capability allowing users to upload legal contracts for AI-driven risk assessment and compliance checking, leveraging Chain-of-Thought (CoT) prompting.

---

## 🏗️ System Architecture

- **Frontend (Client):** React 18, Vite, TypeScript, Zustand (State Management), React Router. UI is built from scratch using vanilla CSS prioritizing a premium Dark Glassmorphism aesthetic.
- **Backend (API):** FastAPI with fully asynchronous endpoints. Follows strict OOP principles and a 3-tier architecture (Routers → Services → Repositories/Models).
- **Database:** PostgreSQL 16 with `pgvector` extension. Managed via SQLAlchemy 2.0 (Async) and Alembic for schema migrations.
- **AI / Embeddings:** `sentence-transformers` for local semantic embeddings (running on CPU/GPU) and Google Generative AI for the LLM brain.

---

## 💻 Features Breakdown

| Module | Features |
| :--- | :--- |
| **Authentication** | JWT-based Auth, Bcrypt hashing, Protected routes. |
| **Search Engine** | 3 Modes: Exact Match, Semantic Search, Hybrid Search. Highlights matching snippets. |
| **AI Assistant** | Context-aware chat, Source citations, Abortable streaming generation. |
| **Contract Analysis**| Upload, parse, and analyze legal contracts for risks and anomalies. |
| **Workspace** | Personal bookmarking, Document Collections, Inline personal notes. |
| **Analytics** | Interactive dashboard (Recharts) tracking search behavior and data distributions. |

---

## 🧪 Testing & Quality Assurance

To validate the stability of the platform, a full suite of tests is provided in the `test/` and `tests_e2e/` directories.

```bash
# 1. Run Integration Tests (Backend)
cd backend
python -m pytest tests/ -v

# 2. Run E2E UI Tests (Frontend)
cd tests_e2e
pytest tests/ -v

# 3. Run Load Testing
cd backend
locust -f locustfile.py
```
> *For detailed test cases, refer to the `test/NCKH_TestCase.xlsx` matrix and `TestingPlan.md`.*

---

## 🛠️ Local Development Setup

### 1. Requirements
- Docker & Docker Compose (for the Database)
- Node.js 18+
- Python 3.10+

### 2. Database Initialization
```bash
# Start PostgreSQL with pgvector extension
docker-compose up -d
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv

# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt

# Create .env file based on configurations below, then run migrations
alembic upgrade head
```

### 4. Frontend Setup
```bash
cd frontend
npm install
```

### 5. Running the Application
Use the provided automation script to spin up both servers instantly:
```powershell
.\start_dev.ps1
```
- **Frontend:** http://localhost:5173
- **Backend Swagger API:** http://localhost:8000/docs

---

## 🔧 Environment Variables (`backend/.env`)

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/legal_db
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your_gemini_api_key
OMP_NUM_THREADS=1
TOKENIZERS_PARALLELISM=false
```

---

## 📊 Generating the Dataset (ETL)

To populate the database with Vietnamese legal documents and generate vector embeddings:

```bash
cd backend
# 1. Download dataset
python scripts/etl/download_data.py
# 2. Chunk documents
python scripts/etl/chunker.py
# 3. Generate Embeddings (Requires CPU/GPU power)
python scripts/etl/embedder.py
# 4. Build HNSW Vector Index
python scripts/etl/build_index.py
```

---
<div align="center">
  <i>Built with passion to solve real-world legal tech challenges.</i>
</div>
